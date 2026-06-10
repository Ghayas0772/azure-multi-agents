import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Azure Multi-Agent Orchestration API",
    description="Production-ready FastAPI wrapper for an asynchronous multi-agent orchestration routing mesh.",
    version="1.0.0"
)

# Shared global instances for the API lifecycle
client = None
credential = None
orchestrator_id = os.environ["ORCHESTRATOR_ID"]
rag_worker_id = os.environ["RAG_SPECIALIST_ID"]

# Fixed thread session pointers for continuity (matching your current setup)
# For true production, you would map these to individual User IDs in a database!
ORCHESTRATOR_THREAD_ID = "thread_Vvbe96T7fL8YpPmsYqDqYg7T" # Replace with your running JSON thread IDs
RAG_THREAD_ID = "thread_AkpL96K7fM4XpZmsYqDqYh2B"         # Replace with your running JSON thread IDs

# Define the expected JSON payload schema for incoming requests
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    route: str
    reply: str

@app.on_event("startup")
async def startup_event():
    """Lifecycle hook that initializes the Azure connection when the server spins up."""
    global client, credential
    try:
        credential = DefaultAzureCredential()
        client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"], 
            credential=credential
        )
        print("Successfully connected to Azure AI Foundry backend components.")
    except Exception as e:
        print(f"Critical error initializing Azure connection: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Lifecycle hook to gracefully close connections when stopping the server."""
    global client, credential
    if client:
        await client.close()
    if credential:
        await credential.close()
    print("Azure credentials and client connections safely terminated.")

async def run_agent_async(thread_id, agent_id, instructions=""):
    """Internal helper to non-blockingly poll the agent status."""
    run = await client.runs.create(
        thread_id=thread_id, 
        agent_id=agent_id,
        additional_instructions=instructions
    )
    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(1)
        run = await client.runs.get(thread_id=thread_id, run_id=run.id)
    return run

def local_routing_validator(raw_decision: str) -> str:
    """Guardrail layer to isolate and validate intent classification tokens."""
    sanitized = raw_decision.strip().upper()
    if "[ROUTE_TO_RAG]" in sanitized or "RAG" in sanitized:
        return "RAG"
    return "GENERAL"

@app.post("/api/chat", response_model=ChatResponse)
async def process_chat_message(payload: ChatRequest):
    """
    Main asynchronous endpoint handling intent classification,
    dynamic multi-agent routing, and data processing.
    """
    user_query = payload.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="User query text cannot be empty.")

    try:
        # Phase 1: Append to Orchestrator Thread
        await client.messages.create(
            thread_id=ORCHESTRATOR_THREAD_ID,
            role="user",
            content=user_query
        )

        routing_directive = (
            "CRITICAL: Analyze the conversation history and the latest user message. "
            "If they are asking to fetch data, research project details, run calculations on the data file, "
            "or asking follow-up questions explicitly referencing the previously extracted project insights, "
            "reply with exactly: [ROUTE_TO_RAG]. Otherwise, reply with exactly: [ROUTE_TO_GENERAL]."
        )

        # Trigger Orchestrator Run
        await run_agent_async(ORCHESTRATOR_THREAD_ID, orchestrator_id, instructions=routing_directive)
        
        # Pull Orchestrator decision string
        messages = client.messages.list(thread_id=ORCHESTRATOR_THREAD_ID)
        raw_reply = ""
        async for msg in messages:
            if msg.role == "assistant" and msg.content:
                raw_reply = msg.content[0].text.value
                break
                
        validated_route = local_routing_validator(raw_reply)

        # Phase 2: Dynamic Execution
        if validated_route == "RAG":
            real_data_prompt = (
                f"The user query is: '{user_query}'. "
                "Analyze your attached 'knowledge_index.csv' file using your code interpreter tool "
                "to extract or drill down into any matching parameters requested."
            )
            
            await client.messages.create(
                thread_id=RAG_THREAD_ID,
                role="user",
                content=real_data_prompt
            )
            
            # Trigger RAG Specialist Run
            await run_agent_async(RAG_THREAD_ID, rag_worker_id)
            
            # Extract final text output generated from the CSV data
            rag_messages = client.messages.list(thread_id=RAG_THREAD_ID)
            final_reply = ""
            async for msg in rag_messages:
                if msg.role == "assistant" and msg.content:
                    final_reply = msg.content[0].text.value
                    break
                    
            return ChatResponse(route="RAG_SPECIALIST", reply=final_reply)

        else:
            # General fallback response handled directly inside the routing system context
            return ChatResponse(
                route="GENERAL_FALLBACK", 
                reply="The message was routed to general assistance, as no explicit data index lookups were requested."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Agent Execution Failure: {str(e)}")