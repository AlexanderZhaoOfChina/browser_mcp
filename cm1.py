import asyncio
from mcp.client.ws import websocket_client
from mcp.client.session import ClientSession

async def run_mcp_client():
    ws_url = "ws://localhost:9009/ws"
    async with websocket_client(ws_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("MCP 会话初始化成功！")
            # 列出可用工具
            tools_result = await session.list_tools()
            print("可用工具：", [tool["name"] for tool in tools_result["tools"]])
            # 你可以继续调用 session.call_tool(...) 等

if __name__ == "__main__":
    asyncio.run(run_mcp_client())