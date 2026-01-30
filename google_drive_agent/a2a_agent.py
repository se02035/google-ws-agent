from google.adk.a2a.utils.agent_to_a2a import to_a2a
from agent import root_agent

A2A_PORT = 8877
a2a_app = to_a2a(root_agent, port=A2A_PORT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(a2a_app, host="0.0.0.0", port=A2A_PORT, log_level="info")
