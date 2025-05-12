import asyncio
import json
import os
import sys
import anyio
import signal
from typing import Optional
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.client.ws import websocket_client
from mcp.client.session import ClientSession

try:
    from mcp.client import ClientSession
except ImportError:
    try:
        from mcp.fastmcp import ClientSession
        print("使用 mcp.fastmcp.ClientSession 作为回退")
    except ImportError:
        raise ImportError("无法找到 ClientSession。请确保安装正确的 mcp 包：git+https://github.com/modelcontextprotocol/python-sdk.git")

# Windows 特定的事件循环设置
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class MCPServer:
    def __init__(self):
        self.process: Optional[asyncio.subprocess.Process] = None
        self._shutdown_event = asyncio.Event()

    async def start(self):
        try:
            print("正在启动 MCP 服务器...")
            npm_path = r"C:\Program Files\nodejs\npm.cmd"
            
            # 创建进程
            self.process = await asyncio.create_subprocess_shell(
                f'"{npm_path}" exec @browsermcp/mcp@latest',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            # 启动后台任务来读取输出
            asyncio.create_task(self._read_output())
            
            # 等待服务器启动
            try:
                # 增加超时时间到 60 秒
                await asyncio.wait_for(self._wait_for_server(), timeout=60)
                print("MCP 服务器已启动")
                return True
            except asyncio.TimeoutError:
                print("服务器启动超时")
                await self.stop()
                return False
            except Exception as e:
                print(f"服务器启动异常: {str(e)}")
                await self.stop()
                return False
                
        except Exception as e:
            print(f"启动 MCP 服务器错误: {str(e)}")
            import traceback
            print(f"错误详情:\n{traceback.format_exc()}")
            return False

    async def _read_output(self):
        if not self.process:
            return
            
        try:
            while True:
                if self.process.stdout:
                    line = await self.process.stdout.readline()
                    if not line:
                        break
                    print(f"服务器输出: {line.decode().strip()}")
                    
                if self.process.stderr:
                    line = await self.process.stderr.readline()
                    if not line:
                        break
                    print(f"服务器错误: {line.decode().strip()}")
        except Exception as e:
            print(f"读取输出错误: {str(e)}")

    async def _wait_for_server(self):
        # 等待服务器启动信号
        # 这里可以根据实际情况修改等待条件
        await asyncio.sleep(5)  # 给服务器一些启动时间
        return True

    async def stop(self):
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception as e:
                print(f"停止服务器错误: {str(e)}")
            finally:
                self.process = None

async def run_mcp_client():
    ws_url = "ws://localhost:9009/ws"
    async with websocket_client(ws_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("会话初始化成功")
            
            # 列出可用工具
            tools_result = await session.list_tools()
            print("\n可用工具列表:")
            for tool in tools_result["tools"]:
                print(f"- {tool['name']}: {tool.get('description', '无描述')}")

            # 测试任务：打开百度并搜索
            test_task = {
                "name": "browser_automation",
                "arguments": {
                    "instruction": "打开百度首页 https://www.baidu.com，在搜索框中输入'Python自动化测试'，然后点击搜索按钮"
                }
            }

            print("\n开始执行测试任务...")
            result = await session.call_tool(test_task)
            print("\n任务执行结果:", json.dumps(result, indent=2, ensure_ascii=False))

async def main():
    server = MCPServer()
    try:
        if await server.start():
            # 运行 MCP 客户端
            await run_mcp_client()
    finally:
        await server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常: {str(e)}")
        import traceback
        print(f"错误详情:\n{traceback.format_exc()}")