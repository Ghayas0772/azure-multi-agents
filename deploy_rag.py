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
    
    print(f"Provisioning new RAG Specialist linked directly to: {os.environ['MODEL_DEPLOYMENT_NAME']}")
    agent = client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="rag_specialist_fixed",
        instructions="You are a data research specialist. Extract and analyze internal information."
    )
    print("\n=== Success! ===")
    print(f"New RAG ID: {agent.id}")

except Exception as e:
    print(f"Failed: {e}")