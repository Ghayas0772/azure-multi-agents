import os
import time
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# Load configuration
load_dotenv()

MEMORY_FILE = "session_memory.json"

def load_or_create_threads(client):
    """
    STATE MANAGEMENT: Loads existing cloud thread IDs from a local cache,
    or provisions fresh ones if no active session memory is found.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                print(f"[Memory Cache] Found active session threads. Resuming chat history...")
                return data["orchestrator_thread_id"], data["rag_thread_id"]
        except Exception:
            print("[Memory Cache] Corrupted cache found. Resetting session threads...")

    # Provision fresh threads if cache doesn't exist or failed to parse
    print("[Memory Cache] No active session found. Provisioning fresh conversation streams...")
    orch_thread = client.threads.create()
    rag_thread = client.threads.create()
    
    # Save IDs to local storage
    with open(MEMORY_FILE, "w") as f:
        json.dump({
            "orchestrator_thread_id": orch_thread.id,
            "rag_thread_id": rag_thread.id
        }, f, indent=4)
        
    return orch_thread.id, rag_thread.id

def run_agent_with_instructions(client, thread_id, agent_id, instructions=""):
    """Executes an agent run loop and polls until completion."""
    run = client.runs.create(
        thread_id=thread_id, 
        agent_id=agent_id,
        additional_instructions=instructions
    )
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        print(".", end="", flush=True)
        run = client.runs.get(thread_id=thread_id, run_id=run.id)
    return run

def local_routing_validator(raw_decision: str) -> str:
    """GUARDRAIL LAYER: Sanitizes and validates the model's output formatting."""
    sanitized = raw_decision.strip().upper()
    if "[ROUTE_TO_RAG]" in sanitized or "RAG" in sanitized:
        return "RAG"
    elif "[ROUTE_TO_GENERAL]" in sanitized or "GENERAL" in sanitized:
        return "GENERAL"
    return "GENERAL"

try:
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )

    print("Fetching active agents from Azure AI Foundry...")
    orchestrator_id = os.environ["ORCHESTRATOR_ID"]
    rag_worker_id = os.environ["RAG_SPECIALIST_ID"]

    # ------------------------------------------------------------------
    # SESSION STATE MEMORY INTERCEPTION
    # ------------------------------------------------------------------
    orchestrator_thread_id, rag_thread_id = load_or_create_threads(client)

    # ------------------------------------------------------------------
    # ENTER DYNAMIC USER QUERY INPUT
    # ------------------------------------------------------------------
    print("\n" + "="*50)
    user_query = input("Enter your message/follow-up query: ").strip()
    if not user_query:
        print("Empty query. Exiting script.")
        exit()
    print("="*50)

    # ------------------------------------------------------------------
    # PHASE 1: Stateful Orchestrator Classification
    # ------------------------------------------------------------------
    print("\n[Phase 1] Appending to Orchestrator Routing Thread...")
    client.messages.create(
        thread_id=orchestrator_thread_id,
        role="user",
        content=user_query
    )

    routing_directive = (
        "CRITICAL: Analyze the conversation history and the latest user message. "
        "If they are asking to fetch data, research project details, run calculations on the data file, "
        "or asking follow-up questions explicitly referencing the previously extracted project insights, "
        "reply with exactly: [ROUTE_TO_RAG]. Otherwise, reply with exactly: [ROUTE_TO_GENERAL]."
        "Do not include any conversational filler."
    )

    print("Orchestrator calculating routing path", end="")
    run_agent_with_instructions(client, orchestrator_thread_id, orchestrator_id, instructions=routing_directive)
    
    # Safely extract the newest response from history
    messages = list(client.messages.list(thread_id=orchestrator_thread_id))
    raw_reply = ""
    for msg in messages:
        if msg.role == "assistant" and msg.content:
            raw_reply = msg.content[0].text.value
            break
            
    print(f"\nRaw Orchestrator Output: '{raw_reply.strip()}'")
    validated_route = local_routing_validator(raw_reply)
    print(f"Validated Execution Route: {validated_route}")

    # ------------------------------------------------------------------
    # PHASE 2: Validated Dynamic Execution (With Thread Memory)
    # ------------------------------------------------------------------
    if validated_route == "RAG":
        print("\n[Phase 2] Appending task to persistent RAG Specialist Thread...")
        
        real_data_prompt = (
            f"The user query is: '{user_query}'. "
            "Examine your thread history to maintain continuity. Open and analyze your attached "
            "'knowledge_index.csv' file to extract or drill down into any matching parameters requested."
        )
        
        client.messages.create(
            thread_id=rag_thread_id,
            role="user",
            content=real_data_prompt
        )
        
        print("RAG Specialist processing task (Analyzing Data File)", end="")
        run_agent_with_instructions(client, rag_thread_id, rag_worker_id)
        
        rag_messages = list(client.messages.list(thread_id=rag_thread_id))
        rag_reply = ""
        for msg in rag_messages:
            if msg.role == "assistant" and msg.content:
                rag_reply = msg.content[0].text.value
                break
                
        print("\n\n=== Final Output From RAG Specialist ===")
        print(rag_reply)

    elif validated_route == "GENERAL":
        print("\n[Phase 2] Run handled directly by Orchestrator context loop...")
        print("Orchestrator provides general conversational context fallback.")

except Exception as e:
    print(f"\nExecution Failed: {e}")