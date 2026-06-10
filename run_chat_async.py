import os
import asyncio
import json
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient

# Load configuration
load_dotenv()

MEMORY_FILE = "session_memory.json"

async def load_or_create_threads_async(client):
    """
    ASYNC STATE MANAGEMENT: Loads existing cloud thread IDs from a local cache,
    or asynchronously provisions fresh ones if no active session memory is found.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                print(f"[Async Memory] Resuming active conversation streams...")
                return data["orchestrator_thread_id"], data["rag_thread_id"]
        except Exception:
            print("[Async Memory] Corrupted cache found. Resetting session threads...")

    print("[Async Memory] No active session found. Asynchronously provisioning fresh streams...")
    orch_thread = await client.threads.create()
    rag_thread = await client.threads.create()
    
    with open(MEMORY_FILE, "w") as f:
        json.dump({
            "orchestrator_thread_id": orch_thread.id,
            "rag_thread_id": rag_thread.id
        }, f, indent=4)
        
    return orch_thread.id, rag_thread.id

async def run_agent_async(client, thread_id, agent_id, instructions=""):
    """Asynchronously executes an agent run loop and polls using non-blocking event loops."""
    run = await client.runs.create(
        thread_id=thread_id, 
        agent_id=agent_id,
        additional_instructions=instructions
    )
    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(1)
        print(".", end="", flush=True)
        run = await client.runs.get(thread_id=thread_id, run_id=run.id)
    return run

def local_routing_validator(raw_decision: str) -> str:
    """GUARDRAIL LAYER: Sanitizes and validates the model's output formatting."""
    sanitized = raw_decision.strip().upper()
    if "[ROUTE_TO_RAG]" in sanitized or "RAG" in sanitized:
        return "RAG"
    return "GENERAL"

async def main():
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=credential) as client:
            
            print("Fetching active agents from Azure AI Foundry (Async Mode)...")
            orchestrator_id = os.environ["ORCHESTRATOR_ID"]
            rag_worker_id = os.environ["RAG_SPECIALIST_ID"]

            orchestrator_thread_id, rag_thread_id = await load_or_create_threads_async(client)

            print("\n" + "="*50)
            user_query = input("Enter your async query: ").strip()
            if not user_query:
                return
            print("="*50)

            # Phase 1: Append to Orchestrator Thread
            print("\n[Phase 1] Appending to Async Orchestrator Thread...")
            await client.messages.create(
                thread_id=orchestrator_thread_id,
                role="user",
                content=user_query
            )

            routing_directive = (
                "CRITICAL: Analyze the conversation history and the latest user message. "
                "If they are asking to fetch data, research project details, run calculations on the data file, "
                "or asking follow-up questions explicitly referencing the previously extracted project insights, "
                "reply with exactly: [ROUTE_TO_RAG]. Otherwise, reply with exactly: [ROUTE_TO_GENERAL]."
            )

            print("Orchestrator calculating routing path", end="")
            await run_agent_async(client, orchestrator_thread_id, orchestrator_id, instructions=routing_directive)
            
            # FIXED: Removed 'await' from the message list call
            messages = client.messages.list(thread_id=orchestrator_thread_id)
            raw_reply = ""
            async for msg in messages:
                if msg.role == "assistant" and msg.content:
                    raw_reply = msg.content[0].text.value
                    break
                    
            print(f"\nRaw Orchestrator Output: '{raw_reply.strip()}'")
            validated_route = local_routing_validator(raw_reply)
            print(f"Validated Execution Route: {validated_route}")

            # Phase 2: Dynamic Execution
            if validated_route == "RAG":
                print("\n[Phase 2] Appending task to persistent Async RAG Thread...")
                real_data_prompt = (
                    f"The user query is: '{user_query}'. "
                    "Analyze your attached 'knowledge_index.csv' file using your code interpreter tool "
                    "to extract or drill down into any matching parameters requested."
                )
                
                await client.messages.create(
                    thread_id=rag_thread_id,
                    role="user",
                    content=real_data_prompt
                )
                
                print("RAG Specialist processing task", end="")
                await run_agent_async(client, rag_thread_id, rag_worker_id)
                
                # FIXED: Removed 'await' from line 126 here too!
                rag_messages = client.messages.list(thread_id=rag_thread_id)
                rag_reply = ""
                async for msg in rag_messages:
                    if msg.role == "assistant" and msg.content:
                        rag_reply = msg.content[0].text.value
                        break
                        
                print("\n\n=== Final Output From Async RAG Specialist ===")
                print(rag_reply)

            else:
                print("\n[Phase 2] Direct conversational fallback handled.")

if __name__ == "__main__":
    asyncio.run(main())