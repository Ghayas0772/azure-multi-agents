import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# 1. Load your secure configuration from .env
load_dotenv()

print("Connecting to your Microsoft Foundry Project via Agent Service...")
try:
    # 2. Open the communication bridge to Azure using our clean client
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    print("\nCreating the RAG Specialist Agent via Python SDK...")
    
    # 3. Create your RAG specialist worker agent
    rag_agent = client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"], # Uses 'gpt-4o'
        name="rag_specialist",
        instructions=(
            "You are a dedicated retrieval expert and data researcher. "
            "Your sole focus is searching through provided knowledge indexes, "
            "extracting accurate contextual facts, and answering user queries "
            "using only verified data documentation. Do not guess or assume."
        )
    )
    
    print("\n=== Success! ===")
    print(f"Agent Name : {rag_agent.name}")
    print(f"Agent ID   : {rag_agent.id}")
    print("\nCopy this RAG Agent ID! We will paste it into our config next.")

except Exception as e:
    print("\n=== Provisioning Failed ===")
    print(f"Error details: {e}")