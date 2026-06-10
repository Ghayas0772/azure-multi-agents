import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# 1. Load the project endpoint from your .env file
load_dotenv()

print("Connecting to Azure AI Foundry...")

try:
    # 2. Initialize the client using your terminal's active login
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    # 3. Test the connection by asking Azure for your project's properties
    project_properties = project_client.get_project_properties()
    print("\n[SUCCESS] Successfully connected to your Azure Project!")
    print(f"Project Name: {project_properties.name}")
    print(f"Location: {project_properties.location}")

except Exception as e:
    print("\n[ERROR] Could not connect to your Azure Project.")
    print(f"Details: {e}")