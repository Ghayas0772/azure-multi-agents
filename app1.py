import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
# Import the tool that lets agents talk to other agents
from azure.ai.agents.models import ConnectedAgentTool

# 1. Initialize environment configurations
load_dotenv()

try:
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )

    print("Fetching pre-configured agents from cloud...")
    # 2. Re-instantiate your existing cloud agents using just their IDs
    orchestrator = client.get_agent(agent_id=os.environ["ORCHESTRATOR_ID"])
    rag_worker = client.get_agent(agent_id=os.environ["RAG_SPECIALIST_ID"])

    print(f"-> Successfully linked manager: '{orchestrator.name}'")
    print(f"-> Successfully linked specialist: '{rag_worker.name}'")

    # 3. Package the RAG worker as an actionable tool for the Orchestrator
    rag_tool = ConnectedAgentTool(
        id=rag_worker.id,
        name=rag_worker.name,
        description=(
            "Use this tool when the user asks to search documents, retrieve data, "
            "or requires factual research from your internal knowledge bases."
        )
    )

    print(f"\nRegistering '{rag_worker.name}' as a functional tool inside '{orchestrator.name}'...")
    # Add the worker agent directly into the orchestrator's available tools array
    orchestrator.tools.append(rag_tool)
    
    print("\n=== Architecture Connected Successfully! ===")
    print("Your multi-agent framework is bound and ready for execution threads.")

except Exception as e:
    print(f"\nConnection Loop Failed: {e}")