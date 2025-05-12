from mcp.client import ClientSession
import asyncio
import json
import os

async def main():
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
    async with ClientSession(
        command=server_command,
        args=server_args,
        env=env
    ) as session:
        try:
            # 列出可用工具
            tools_result = await session.list_tools()
            print("Available tools:", [tool["name"] for tool in tools_result["tools"]])

            # 示例：调用浏览器自动化工具（假设工具名为 "browser_automation"）
            # 注意：实际工具名称需根据 list_tools() 的输出确认
            task = {
                "name": "browser_automation",  # 替换为实际工具名称
                "arguments": {
                    "instruction": "Open the webpage https://www.example.com and click the first button on the page"
                }
            }

            # 调用工具
            result = await session.call_tool(task)
            print("Tool result:", json.dumps(result, indent=2))

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # 在 Windows 上可能需要设置事件循环策略
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())