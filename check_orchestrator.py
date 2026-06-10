import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# Load environment variables
load_dotenv()

try:
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )

    print("Fetching Orchestrator Agent configuration...")
    orchestrator_id = os.environ["ORCHESTRATOR_ID"]
    
    # 1. Create a pristine thread
    print("\nCreating a clean diagnostic thread...")
    thread = client.threads.create()

    # 2. Add a simple, baseline prompt
    test_prompt = "Hello Orchestrator! Please respond with a short greeting so I can verify you are working."
    print(f"Sending User Message: '{test_prompt}'")
    
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content=test_prompt
    )

    # 3. Start the execution run
    print("\nTriggering Orchestrator run loop", end="")
    run = client.runs.create(thread_id=thread.id, agent_id=orchestrator_id)
    
    # Poll until done
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        print(".", end="", flush=True)
        run = client.runs.get(thread_id=thread.id, run_id=run.id)
        
    print(f"\nRun finished with Status: {run.status}")

    # 4. Dump the RAW conversation transcript
    print("\n--- Raw Thread Transcript Logs ---")
    messages = list(client.messages.list(thread_id=thread.id))
    
    # We iterate backwards (oldest to newest) to trace the exact timeline
    for idx, msg in enumerate(reversed(messages)):
        print(f"\n[Message #{idx+1}] Role: {msg.role.upper()}")
        if not msg.content:
            print("Content: (EMPTY CONTENT ARRAY)")
        for block in msg.content:
            # Safely extract text value regardless of object structure
            text_val = getattr(getattr(block, 'text', block), 'value', str(block))
            print(f"Content Block: '{text_val}'")

except Exception as e:
    print(f"\nDiagnostic Failed: {e}")