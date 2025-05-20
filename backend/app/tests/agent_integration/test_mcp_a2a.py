try:
    import mcp_tools
except ImportError:
    mcp_tools = None
    print("[WARN] MCP tools not installed. Skipping MCP tests.")

try:
    import agent2agent_protocol as a2a
except ImportError:
    a2a = None
    print("[WARN] A2A protocol not installed. Skipping A2A tests.")

def test_mcp_registration():
    if not mcp_tools:
        print("[SKIP] MCP tools not installed.")
        return
    try:
        registry = mcp_tools.AgentRegistry()
        agent_metadata = {"name": "TestAgent", "features": ["test"], "status": "active"}
        result = registry.register_agent(agent_metadata)
        print(f"[PASS] MCP registration: {result}")
        registry.update_status(result.get('id', 'test-id'), "testing")
        print(f"[PASS] MCP status update for {result.get('id', 'test-id')}")
    except Exception as e:
        print(f"[FAIL] MCP registration/status: {e}")

def test_a2a_message():
    if not a2a:
        print("[SKIP] A2A protocol not installed.")
        return
    try:
        msg = a2a.create_message(sender="TestAgent", recipient="OtherAgent", content="Hello A2A!")
        parsed = a2a.parse_message(msg)
        print(f"[PASS] A2A message parse: {parsed}")
    except Exception as e:
        print(f"[FAIL] A2A message: {e}")

if __name__ == "__main__":
    test_mcp_registration()
    test_a2a_message() 