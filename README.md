Azure Async Multi-Agent Orchestrator
A high-performance, asynchronous multi-agent orchestration framework built on Azure AI Foundry. This project routes user queries to specialized AI agents—an Orchestrator and a RAG Specialist—while maintaining stateful session context via an interactive Streamlit dashboard.

Features
Async Core: Built with asyncio to handle non-blocking agent polling, ensuring a highly responsive user interface.

Decoupled Architecture: Modular design separating the orchestration logic, UI state management, and agent tool execution.

Specialized Agent Roles: * Orchestrator: Analyzes user intent and applies local guardrails.

RAG Specialist: Performs targeted data analysis within a secure sandbox using the CodeInterpreterTool.

Stateful UI: Streamlit-based dashboard for real-time interaction and session tracking.

Enterprise-Ready Design: Configured for integration with Azure AI Foundry endpoints.

Project Structure
Plaintext
azure-multi-agents/
│
├── app_ui.py              # Streamlit dashboard & state management
├── create_orchestrator.py # Orchestrator agent initialization
├── create_rag_agent.py    # RAG specialist agent logic
├── run_chat_async.py      # Core asynchronous polling logic
├── deploy_orchestrator.py # Deployment scripts for Azure AI
├── requirements.txt       # Project dependencies
└── .env                   # Environment/API configuration
Setup Instructions
Clone the repository

Bash
git clone https://github.com/Ghayas0772/azure-multi-agents.git
cd azure-multi-agents
Create virtual environment

Bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install dependencies

Bash
pip install -r requirements.txt
Configure Environment
Create a .env file with your Azure AI Foundry credentials:

Plaintext
PROJECT_ENDPOINT=your_endpoint_here
ORCHESTRATOR_ID=your_orchestrator_id_here
RAG_SPECIALIST_ID=your_rag_specialist_id_here
Run the dashboard

Bash
streamlit run app_ui.py
Tech Stack
Python 3.12+

Azure AI Foundry (Agent Orchestration)

Streamlit (Frontend Dashboard)

AsyncIO (Concurrency)

CodeInterpreterTool (Secure Sandbox Execution)

Purpose
This project is built for:

Mastering Azure AI agent orchestration.

Implementing asynchronous workflows in AI applications.

Building scalable, multi-agent systems for data-heavy tasks.

Author
Ghayasudin Ghayas
MS Data Science | AI & Machine Learning Enthusiast
