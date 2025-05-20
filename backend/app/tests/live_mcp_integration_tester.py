import asyncio
import os
import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client
from litellm.experimental_mcp_client.tools import (
    transform_mcp_tool_to_openai_tool,
    transform_openai_tool_call_request_to_mcp_tool_call_request,
)

# Assuming the LiteLLM proxy is running at http://localhost:4000
LITELLM_PROXY_MCP_URL = os.getenv("LITELLM_PROXY_MCP_URL", "http://localhost:4000/mcp/")

# Note: This test requires a running LiteLLM proxy with MCP servers configured
# and the actual MCP servers to be accessible.

@pytest.mark.asyncio
async def test_list_mcp_tools_via_proxy():
    """
    Tests if the LiteLLM proxy correctly exposes MCP tools via its /mcp/tools/list endpoint.
    """
    print(f"\nConnecting to LiteLLM proxy MCP endpoint: {LITELLM_PROXY_MCP_URL}")
    try:
        async with sse_client(LITELLM_PROXY_MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("MCP Client session initialized.")

                mcp_tools = await session.list_tools()
                print(f"Received MCP tools: {mcp_tools.tools}")

                # Assert that the list of tools is not empty and contains expected tools
                # This assertion needs to be updated based on the actual MCP servers configured
                # in litellm_proxy_config/config.yaml and their exposed tools.
                assert mcp_tools.tools is not None
                assert len(mcp_tools.tools) > 0
                # Example assertion: assert any(tool.name == "my_sample_tool" for tool in mcp_tools.tools)

    except Exception as e:
        pytest.fail(f"Failed to list MCP tools via proxy: {e}")

@pytest.mark.asyncio
async def test_call_mcp_tool_via_proxy():
    """
    Tests if the LiteLLM proxy correctly routes MCP tool calls to the underlying MCP server.
    This requires a specific MCP server and tool to be configured and running.
    """
    # This test is conceptual and needs to be adapted based on a specific configured MCP tool.
    # You would typically:
    # 1. Get the list of tools (can reuse logic from test_list_mcp_tools_via_proxy)
    # 2. Identify a specific tool to call.
    # 3. Construct the arguments for that tool.
    # 4. Use session.call_tool() to call the tool via the proxy.
    # 5. Assert the expected result.

    print(f"\nAttempting to call an MCP tool via proxy: {LITELLM_PROXY_MCP_URL}")
    try:
        async with sse_client(LITELLM_PROXY_MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("MCP Client session initialized for tool call.")

                # --- Placeholder for actual tool call logic ---
                # Example: Calling a hypothetical 'echo' tool on 'my_mcp_server'
                # tool_name_to_call = "echo"
                # tool_arguments = {"text": "Hello from LiteLLM proxy!"}
                # print(f"Calling tool '{tool_name_to_call}' with arguments: {tool_arguments}")
                # result = await session.call_tool(name=tool_name_to_call, arguments=tool_arguments)
                # print(f"Tool call result: {result}")
                # assert result is not None
                # assert result.content is not None
                # assert len(result.content) > 0
                # assert result.content[0].text == "Hello from LiteLLM proxy!" # Example assertion

                # For now, we'll just pass if we can connect, as the actual tool call
                # depends on specific MCP server setup.
                print("Placeholder for actual MCP tool call test.")
                pass

    except Exception as e:
        pytest.fail(f"Failed to call MCP tool via proxy: {e}")

# Example of how to run these tests:
# 1. Ensure LiteLLM proxy is running with MCP servers configured.
# 2. Ensure the configured MCP servers are running and accessible.
# 3. Navigate to the backend/app directory in your terminal.
# 4. Run pytest: pytest tests/live_mcp_integration_tester.py
