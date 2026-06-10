import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
# Import the brand new dedicated agent client
from azure.ai.agents import AgentsClient

# 1. Load your secure configuration from .env
load_dotenv()

print("Connecting to your Microsoft Foundry Project via Agent Service...")
try:
    # 2. Establish your credentialed agent client
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    print("\nCreating the main Orchestrator Agent via SDK...")
    
    # 3. Create your agent version dynamically
    orchestrator_agent = client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"], # Uses 'gpt-4o'
        name="orchestrator",
        instructions=(
            "You are the master routing supervisor of a multi-agent system. "
            "Your job is to analyze complex user goals, break them into smaller tasks, "
            "and eventually coordinate assignments with your specialist worker agents."
        )
    )
    
    print("\n=== Success! ===")
    print(f"Agent Name : {orchestrator_agent.name}")
    print(f"Agent ID   : {orchestrator_agent.id}")
    print("\nCopy this Agent ID! We will need it later to link our systems together.")

except Exception as e:
    print("\n=== Provisioning Failed ===")
    print(f"Error details: {e}")