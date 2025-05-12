import json
import os
import sys
import subprocess
import time
import websocket
import threading
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP客户端，用于与Model Context Protocol服务器通信"""
    
    def __init__(self, server_process=None):
        self.server_process = server_process
        self.ws = None
        self.connected = False
        self.message_queue = {}
        self.ws_thread = None
    
    def connect(self, url="ws://localhost:9009/ws"):
        """连接到MCP服务器"""
        try:
            self.ws = websocket.WebSocketApp(
                url,
                on_open=lambda ws: self._on_open(ws),
                on_message=lambda ws, msg: self._on_message(ws, msg),
                on_error=lambda ws, error: self._on_error(ws, error),
                on_close=lambda ws, close_status_code, close_msg: self._on_close(ws, close_status_code, close_msg)
            )
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # 等待连接建立
            timeout = 10
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                logger.error("连接MCP服务器超时")
                return False
                
            logger.info("已连接到MCP服务器")
            return True
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {str(e)}")
            return False
    
    def _on_open(self, ws):
        """WebSocket连接打开时的回调"""
        logger.info("WebSocket连接已打开")
        self.connected = True
    
    def _on_message(self, ws, message):
        """接收到WebSocket消息时的回调"""
        try:
            data = json.loads(message)
            logger.debug(f"收到消息: {data}")
            
            # 处理响应
            if "id" in data and data["id"] in self.message_queue:
                self.message_queue[data["id"]] = data
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
    
    def _on_error(self, ws, error):
        """WebSocket错误时的回调"""
        logger.error(f"WebSocket错误: {str(error)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭时的回调"""
        logger.info(f"WebSocket连接已关闭: {close_status_code} - {close_msg}")
        self.connected = False
    
    def send_request(self, method, params=None, timeout=30):
        """发送请求到MCP服务器"""
        if not self.connected:
            logger.error("未连接到MCP服务器")
            return None
        
        message_id = str(uuid.uuid4())
        request = {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            # 发送请求
            self.message_queue[message_id] = None
            self.ws.send(json.dumps(request))
            
            # 等待响应
            start_time = time.time()
            while self.message_queue[message_id] is None and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            response = self.message_queue.pop(message_id, None)
            if response is None:
                logger.error(f"请求超时: {method}")
                return None
            
            if "error" in response:
                logger.error(f"请求错误: {response['error']}")
                return None
            
            return response.get("result")
        except Exception as e:
            logger.error(f"发送请求时出错: {str(e)}")
            return None
    
    def list_tools(self):
        """列出可用工具"""
        return self.send_request("listTools")
    
    def call_tool(self, name, arguments=None):
        """调用工具"""
        return self.send_request("callTool", {
            "name": name,
            "arguments": arguments or {}
        })
    
    def browser_navigate(self, url):
        """浏览器导航到指定URL"""
        return self.call_tool("mcp_browsermcp_browser_navigate", {"url": url})
    
    def browser_snapshot(self):
        """获取浏览器当前页面的快照"""
        return self.call_tool("mcp_browsermcp_browser_snapshot", {"random_string": "dummy"})
    
    def browser_click(self, element, ref):
        """点击浏览器页面上的元素"""
        return self.call_tool("mcp_browsermcp_browser_click", {"element": element, "ref": ref})
    
    def close(self):
        """关闭客户端连接"""
        if self.ws:
            self.ws.close()
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            logger.info("已关闭MCP服务器")

def run_command(command):
    """运行命令并返回输出"""
    try:
        logger.info(f"执行命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e.stderr}")
        return None

def main():
    logger.info("正在检查Node.js是否已安装...")
    node_version = run_command("node --version")
    if not node_version:
        logger.error("未找到Node.js，请先安装Node.js")
        return
    
    logger.info(f"Node.js版本: {node_version.strip()}")
    
    logger.info("正在检查npm是否已安装...")
    npm_version = run_command("npm --version")
    if not npm_version:
        logger.error("未找到npm，请先安装npm")
        return
    
    logger.info(f"npm版本: {npm_version.strip()}")
    
    try:
        # 检查websocket包是否已安装
        import websocket
    except ImportError:
        logger.info("正在安装websocket-client包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websocket-client"])
        import websocket
    
    logger.info("正在安装@browsermcp/mcp包...")
    install_result = run_command("npm install -g @browsermcp/mcp@latest")
    if not install_result:
        logger.error("安装@browsermcp/mcp失败")
        return
    
    logger.info("正在启动浏览器自动化服务...")
    # 启动MCP服务器，指定端口9009
    server_process = subprocess.Popen(
        "npm exec @browsermcp/mcp@latest -- --port 9009",
        shell=True,
        env={
            "NODE_ENV": "production",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "PYTHONUTF8": "1",
            **os.environ
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务启动
    logger.info("等待服务启动...")
    time.sleep(5)
    
    # 创建MCP客户端
    client = MCPClient(server_process)
    
    try:
        # 连接到MCP服务器
        if not client.connect():
            logger.error("无法连接到MCP服务器")
            return
        
        # 列出可用工具
        tools = client.list_tools()
        if tools:
            logger.info(f"可用工具: {[tool['name'] for tool in tools['tools']]}")
        
        # 浏览器自动化示例
        logger.info("示例: 自动打开https://www.example.com并查看页面")
        
        # 打开网页
        navigate_result = client.browser_navigate("https://www.example.com")
        if navigate_result:
            logger.info("成功导航到example.com")
        
        # 获取页面快照
        snapshot = client.browser_snapshot()
        if snapshot:
            logger.info("成功获取页面快照")
            
            # 查找页面上的链接或按钮
            elements = snapshot.get("elements", [])
            for element in elements:
                if element.get("role") == "link" or element.get("role") == "button":
                    logger.info(f"找到元素: {element.get('name')}")
                    
                    # 点击第一个找到的链接或按钮
                    click_result = client.browser_click(element.get("name"), element.get("ref"))
                    if click_result:
                        logger.info(f"成功点击元素: {element.get('name')}")
                    break
        
        logger.info("浏览器自动化演示完成")
        
        # 让用户看到输出
        input("按回车键结束程序...")
        
    except Exception as e:
        logger.error(f"运行过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭客户端连接和服务器
        if client:
            client.close()

if __name__ == "__main__":
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"正在运行脚本...")
    
    main()