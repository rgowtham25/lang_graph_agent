# demo.py code from earlier answer
from agent import LangGraphAgent
import json, os

def main():
    agent = LangGraphAgent(os.path.join(os.path.dirname(__file__), "config.yaml"))
    # Sample input
    payload = {
        "customer_name": "Alice Johnson",
        "email": "alice@example.com",
        "query": "My internet is not working since morning.",
        "priority": "high",
        "ticket_id": "TCK12345"
    }
    result = agent.run(payload)
    # Save outputs
    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "final_payload.json"), "w") as f:
        json.dump({k:v for k,v in result.items() if k != "_logs"}, f, indent=2)
    with open(os.path.join(out_dir, "execution_logs.txt"), "w") as f:
        f.write("\n".join(result["_logs"]))
    print("Final Payload:")
    print(json.dumps({k:v for k,v in result.items() if k != "_logs"}, indent=2))
    print("\nExecution Logs written to outputs/execution_logs.txt")

if __name__ == "__main__":
    main()
