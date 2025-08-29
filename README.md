📌 Lang Graph Agent

This project implements a Lang Graph Agent that models query handling stages, persists state, and executes a sample query flow with responses.

🚀 Features

Stage Modeling – Defines stages like Intake, Understand, Ask, Retrieve, Decide, Update, and Complete.

State Persistence – Maintains context across stages and saves execution logs.

Sample Query Execution – Handles customer queries (e.g., internet issues) and provides knowledge base solutions with actions.

📂 Project Structure
lang_graph_agent/
│── outputs/
│   ├── execution_logs.txt      # Logs of execution flow
│   ├── final_payload.json      # Final structured output
│── abilities.py                # Defines agent abilities
│── agent.py                    # Main Lang Graph agent logic
│── config.yaml                 # Configuration & stage definitions
│── demo.py                     # Demo script to run the agent
│── mcp_clients.py              # Client integration
│── README.md                   # Documentation

▶️ How to Run

Clone the repo:

git clone https://github.com/rgowtham25/lang_graph_agent.git
cd lang_graph_agent


Create virtual environment & install dependencies:

python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Mac/Linux
pip install -r requirements.txt


Run demo:

python demo.py

📊Output

Execution Logs → outputs/execution_logs.txt

Final Payload → outputs/final_payload.json
