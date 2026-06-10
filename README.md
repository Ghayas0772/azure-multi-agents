---
title: "Azure Async Multi-Agent Orchestrator"
author: "Your Name"
date: "`r Sys.Date()`"
output: github_document
---

# Azure Async Multi-Agent Orchestrator

A high-performance, asynchronous multi-agent orchestration framework built on **Azure AI Foundry**. This project demonstrates a production-ready pattern for routing user queries to specialized AI agents while maintaining stateful session context through an interactive **Streamlit** dashboard.

## Architectural Concept

The system follows a modular "Orchestrator-Worker" pattern, designed for scalability and high performance.



* **Orchestrator**: Acts as the intelligent traffic controller, analyzing user intent and applying local guardrails.
* **Worker Agents (RAG)**: Specialized agents that perform data analysis within a secure sandbox using the Code Interpreter tool.
* **Async Core**: Built with `asyncio` to handle non-blocking agent polling, ensuring the UI remains responsive during long-running tasks.

## Prerequisites

To run this project, you will need:
* Python 3.12+
* An active **Azure AI Foundry** project.
* The following environment variables defined in a `.env` file:
    * `PROJECT_ENDPOINT`
    * `ORCHESTRATOR_ID`
    * `RAG_SPECIALIST_ID`

##  Usage

### Installation

```bash
# Clone the repository
git clone [https://github.com/your-username/azure-multi-agents.git](https://github.com/your-username/azure-multi-agents.git)
cd azure-multi-agents

# Set up the virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
### Running the Dashboard
Launch the application using the Streamlit CLI:
<img width="644" height="81" alt="image" src="https://github.com/user-attachments/assets/190b3fba-c72d-43ed-ae1a-64b506ba89ff" />


# Install dependencies
pip install -r requirements.txt

### File Structure
<img width="663" height="178" alt="image" src="https://github.com/user-attachments/assets/24e58a1a-565c-4660-bf82-d0a4a86ca5dc" />

