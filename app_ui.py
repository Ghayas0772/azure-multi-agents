import os
import asyncio
import streamlit as Streamlit
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient

# ==============================================================================
# 1. STREAMLIT CONFIGURATION & APP INITIALIZATION
# ==============================================================================
# Force layout optimization (Must be the very first Streamlit command called)
Streamlit.set_page_config(page_title="Multi-Agent Workspace", layout="wide")

# Load environment configurations from your local .env file
load_dotenv()

# Helper to execute asynchronous coroutines safely within Streamlit's rendering context
def run_async(coro):
    return asyncio.run(coro)

# ==============================================================================
# 2. PERSISTENT CLOUD STATE MANAGEMENT (SESSION CACHE)
# ==============================================================================
# This block provisions thread resources EXACTLY ONCE per user browser session.
# If threads already exist in state, it reuses them to maintain context history.
if "orchestrator_thread_id" not in Streamlit.session_state or "rag_thread_id" not in Streamlit.session_state:
    
    async def initialize_threads():
        async with DefaultAzureCredential() as credential:
            async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=credential) as client:
                orch_thread = await client.threads.create()
                rag_thread = await client.threads.create()
                return orch_thread.id, rag_thread.id

    # Run the initial sync call to provision thread resources on Azure AI Foundry
    with Streamlit.spinner("Initializing persistent conversation streams in Azure..."):
        orch_id, rag_id = run_async(initialize_threads())
        Streamlit.session_state.orchestrator_thread_id = orch_id
        Streamlit.session_state.rag_thread_id = rag_id

# Assign global variables to point directly to our cached session IDs
ORCHESTRATOR_THREAD_ID = Streamlit.session_state.orchestrator_thread_id
RAG_THREAD_ID = Streamlit.session_state.rag_thread_id

# Initialize persistent chat logs for rendering messages in the UI
if "messages" not in Streamlit.session_state:
    Streamlit.session_state.messages = []

# ==============================================================================
# 3. ASYNC RUNTIME ENGINE HELPERS
# ==============================================================================
async def run_agent_async(client, thread_id, agent_id, status_placeholder, instructions=""):
    """Executes an agent run loop and updates the Streamlit UI dynamically while polling."""
    run = await client.runs.create(
        thread_id=thread_id, 
        agent_id=agent_id,
        additional_instructions=instructions
    )
    
    # Visual polling indicators on screen
    dots = 0
    while run.status in ["queued", "in_progress"]:
        dots = (dots + 1) % 4
        status_placeholder.text("Processing" + "." * dots)
        await asyncio.sleep(1)
        run = await client.runs.get(thread_id=thread_id, run_id=run.id)
    return run

def local_routing_validator(raw_decision: str) -> str:
    """GUARDRAIL LAYER: Sanitizes and validates the model's output formatting."""
    sanitized = raw_decision.strip().upper()
    if "[ROUTE_TO_RAG]" in sanitized or "RAG" in sanitized:
        return "RAG"
    return "GENERAL"

# ==============================================================================
# 4. STREAMLIT USER INTERFACE LAYOUT & SIDEBAR
# ==============================================================================
Streamlit.title("🚀 Azure AI Foundry Multi-Agent Dashboard")
Streamlit.caption("Stateful Orchestrator Router & RAG Specialist Pipeline")

# Render Sidebar metadata panel
with Streamlit.sidebar:
    Streamlit.header("⚙️ System Registry")
    Streamlit.success("Connected to Azure AI Foundry")
    
    # Display running configuration statuses
    Streamlit.info(f"**Orchestrator ID:**\n`{os.environ.get('ORCHESTRATOR_ID')[:20]}...`")
    Streamlit.info(f"**RAG Specialist ID:**\n`{os.environ.get('RAG_SPECIALIST_ID')[:20]}...`")
    Streamlit.info(f"**Active Thread (Orch):**\n`{ORCHESTRATOR_THREAD_ID[:20]}...`")
    Streamlit.info(f"**Active Thread (RAG):**\n`{RAG_THREAD_ID[:20]}...`")
    
    # Clear history button that pops session keys to force a full hard restart
    if Streamlit.button("🗑️ Clear Chat History", use_container_width=True):
        Streamlit.session_state.messages = []
        Streamlit.session_state.pop("orchestrator_thread_id", None)
        Streamlit.session_state.pop("rag_thread_id", None)
        Streamlit.rerun()

# Render all existing conversations from history logs onto the workspace
for message in Streamlit.session_state.messages:
    with Streamlit.chat_message(message["role"]):
        Streamlit.markdown(message["content"])

# ==============================================================================
# 5. ASYNC RUNTIME ORCHESTRATION PIPELINE
# ==============================================================================
# Listen for incoming user prompts from the chat input tray
if user_query := Streamlit.chat_input("Ask a question about your project indices..."):
    
    # Append and display user input directly to the browser view
    with Streamlit.chat_message("user"):
        Streamlit.markdown(user_query)
    Streamlit.session_state.messages.append({"role": "user", "content": user_query})

    # Wrapper coroutine to handle async steps non-blockingly
    async def process_pipeline():
        async with DefaultAzureCredential() as credential:
            async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=credential) as client:
                
                # --- PHASE 1: DETERMINISTIC ROUTING ---
                with Streamlit.status("🧠 Orchestrator Evaluating Route...", expanded=True) as status:
                    status_text = Streamlit.empty()
                    
                    # Push user query to persistent cloud thread
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
                    
                    # Execute routing worker run
                    await run_agent_async(client, ORCHESTRATOR_THREAD_ID, os.environ["ORCHESTRATOR_ID"], status_text, instructions=routing_directive)
                    
                    # Consume AsyncItemPaged iterator safely
                    messages = client.messages.list(thread_id=ORCHESTRATOR_THREAD_ID)
                    raw_reply = ""
                    async for msg in messages:
                        if msg.role == "assistant" and msg.content:
                            raw_reply = msg.content[0].text.value
                            break
                    
                    validated_route = local_routing_validator(raw_reply)
                    status.update(label=f"✅ Routing Confirmed: {validated_route}", state="complete", expanded=False)
                
                # --- PHASE 2: CONTEXTUAL WORKER EXECUTION ---
                if validated_route == "RAG":
                    with Streamlit.status("📊 RAG Specialist Processing Data Index...", expanded=True) as status:
                        status_text = Streamlit.empty()
                        
                        real_data_prompt = (
                            f"The user query is: '{user_query}'. "
                            "Analyze your attached 'knowledge_index.csv' file using your code interpreter tool "
                            "to extract or drill down into any matching parameters requested."
                        )
                        # Push task parameters to our persistent RAG specialized chat thread
                        await client.messages.create(thread_id=RAG_THREAD_ID, role="user", content=real_data_prompt)
                        
                        # Execute code interpreter compute run
                        await run_agent_async(client, RAG_THREAD_ID, os.environ["RAG_SPECIALIST_ID"], status_text)
                        
                        # Consume AsyncItemPaged result stream
                        rag_messages = client.messages.list(thread_id=RAG_THREAD_ID)
                        rag_reply = ""
                        async for msg in rag_messages:
                            if msg.role == "assistant" and msg.content:
                                rag_reply = msg.content[0].text.value
                                break
                        status.update(label="✅ Computation Complete!", state="complete", expanded=False)
                        
                    return rag_reply
                else:
                    return "The request was handled as a general conversational query; no data indexing was requested."

    # Process pipeline inside the spinner and stream back into the chat component
    with Streamlit.chat_message("assistant"):
        response_placeholder = Streamlit.empty()
        with Streamlit.spinner("Generating final response..."):
            final_output = run_async(process_pipeline())
        response_placeholder.markdown(final_output)
        
    # Append the assistant's answer to our structural memory logs
    Streamlit.session_state.messages.append({"role": "assistant", "content": final_output})