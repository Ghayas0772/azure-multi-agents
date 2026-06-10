---
title: "Azure Async Multi-Agent Orchestrator"
author: Ghayasudin Ghayas
date: "`r Sys.Date 06/10/2026
output: github_document
---

# Azure Async Multi-Agent Orchestrator

A high-performance, asynchronous multi-agent orchestration framework built on **Azure AI Foundry**. This project routes user queries to specialized AI agents (Orchestrator + RAG Specialist) while maintaining stateful session context via a Streamlit dashboard.

##  System Architecture

The project relies on a decoupled, modular design to ensure scalability.



* **Orchestrator**: Acts as the traffic controller, analyzing user intent and applying local guardrails.
* **RAG Specialist**: A worker agent that performs data analysis within a secure sandbox using the `CodeInterpreterTool`.
* **Async Core**: Built with `asyncio` to handle non-blocking agent polling, keeping the UI responsive.

##  File Anatomy

| File | Role |
| :--- | :--- |
| `app_ui.py` | The "Brain": Handles UI, state management, and async orchestration logic. |
| `.env` | The "Vault": Secure storage for your API keys and project endpoints. |
| `.gitignore` | The "Shield": Prevents secrets and temporary files from entering Git. |
| `requirements.txt` | The "Manifest": Lists all necessary Python dependencies. |

##  Quick Setup

### 1. Prerequisites
Ensure you have **Python 3.12+** installed. You will need an active Azure AI Foundry project. Create a `.env` file in the root folder with:
```text
PROJECT_ENDPOINT=your_endpoint_here
ORCHESTRATOR_ID=your_orchestrator_id_here
RAG_SPECIALIST_ID=your_rag_specialist_id_here

# 2. Installation
# Clone the repository
git clone [https://github.com/your-username/azure-multi-agents.git](https://github.com/your-username/azure-multi-agents.git)
cd azure-multi-agents

# Set up the virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# 3. Launching the Dashboard
streamlit run app_ui.py
