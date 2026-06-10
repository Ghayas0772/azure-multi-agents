import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# 1. Look up your .env file keys
load_dotenv()

print("Connecting to your Microsoft Foundry Project...")
try:
    # 2. Start the project bridge using your active terminal credentials
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    # 3. Pull a list of all agents currently living in your cloud workspace
    agents_list = project_client.agents.list_agents()
    
    print("\n=== Connection Successful! ===")
    print(f"Connected to Endpoint: {project_client.endpoint}")
    print("\nAvailable Agents in your cloud project:")
    
    # 4. Print out any agents you created in the playground
    if not agents_list.data:
        print("- No agents found yet. (Ready to create fresh ones via code!)")
    else:
        for agent in agents_list.data:
            print(f"- Name: '{agent.name}' | ID: {agent.id}")
            
except Exception as e:
    print("\n=== Connection Failed ===")
    print(f"Error details: {e}")