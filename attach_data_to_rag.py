import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    CodeInterpreterTool,
    ToolResources,
    CodeInterpreterToolResource
)

# Load configuration
load_dotenv()

try:
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )

    rag_agent_id = os.environ["RAG_SPECIALIST_ID"]
    file_id = "assistant-EXgcx1gnyPEfpWMvphmbRn"

    print(f"File already verified in Azure. ID: {file_id}")
    print(f"\nEquipping RAG Specialist ({rag_agent_id}) with Code Interpreter via typed models...")
    
    # 1. Initialize the tool definition
    code_interpreter = CodeInterpreterTool()

    # 2. Build the resources using explicit SDK class definitions instead of a raw dict
    tool_resources_config = ToolResources(
        code_interpreter=CodeInterpreterToolResource(file_ids=[file_id])
    )

    # 3. Update the cloud agent asset
    updated_agent = client.update_agent(
        agent_id=rag_agent_id,
        tools=code_interpreter.definitions,
        tool_resources=tool_resources_config  # Passing the typed object satisfies the internal validator
    )

    print("\n=== Data Binding Complete! ===")
    print(f"Agent '{updated_agent.name}' is now securely connected to the data file.")

except Exception as e:
    print(f"\nBinding Failed: {e}")