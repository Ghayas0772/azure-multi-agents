import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

load_dotenv()

try:
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    print("Testing gpt-4o deployment directly...")
    thread = client.threads.create()
    
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Say the word 'Hello' and nothing else."
    )
    
    run = client.runs.create(thread_id=thread.id, agent_id=os.environ["ORCHESTRATOR_ID"])
    
    while run.status in ["queued", "in_progress"]:
        run = client.runs.get(thread_id=thread.id, run_id=run.id)
        
    messages = list(client.messages.list(thread_id=thread.id))
    print(f"Model Response: '{messages[0].content[0].text.value}'")

except Exception as e:
    print(f"Test failed: {e}")