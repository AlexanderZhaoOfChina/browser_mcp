import asyncio
import json
import os
try:
    from mcp.client import ClientSession
except ImportError:
    from mcp.fastmcp import ClientSession  # Fallback to fastmcp if available
    print("Using mcp.fastmcp.ClientSession as fallback")

async def run_mcp_client():
    # 配置 MCP 服务器
    server_command = "npx"
    server_args = ["@browsermcp/mcp@latest"]
    env = {
        "NODE_ENV": "production",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1"
    }

    # 初始化 MCP 客户端
    try:
        async with ClientSession(
            command=server_command,
            args=server_args,
            env=env
        ) as session:
            # 列出可用工具
            tools_result = await session.list_tools()
            print("Available tools:", [tool["name"] for tool in tools_result["tools"]])

            # 示例：调用浏览器自动化工具
            # 注意：工具名称需根据 list_tools() 输出替换
            task = {
                "name": "browser_automation",  # 替换为实际工具名称
                "arguments": {
                    "instruction": "Open the webpage https://www.example.com and click the first button on the page"
                }
            }

            # 调用工具
            result = await session.call_tool(task)
            print("Tool result:", json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error during MCP session: {str(e)}")

async def main():
    # 启动 MCP 服务器（可选：如果服务器未运行，程序会自动启动）
    try:
        process = await asyncio.create_subprocess_exec(
            "npx", "@browsermcp/mcp@latest",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("MCP server started with PID:", process.pid)

        # 运行 MCP 客户端
        await run_mcp_client()

        # 等待服务器进程结束（可选）
        stdout, stderr = await process.communicate()
        if stdout:
            print("Server stdout:", stdout.decode())
        if stderr:
            print("Server stderr:", stderr.decode())

    except Exception as e:
        print(f"Error starting MCP server: {str(e)}")

if __name__ == "__main__":
    # Windows 异步事件循环策略
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())