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
    
    print(f"Provisioning new Orchestrator linked directly to: {os.environ['MODEL_DEPLOYMENT_NAME']}")
    agent = client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="orchestrator_fixed",
        instructions="You are a helpful multi-agent supervisor. Answer user queries clearly."
    )
    print("\n=== Success! ===")
    print(f"New Orchestrator ID: {agent.id}")

except Exception as e:
    print(f"Failed: {e}")