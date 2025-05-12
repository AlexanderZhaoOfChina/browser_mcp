import asyncio
import websockets
import json

async def test_browser_navigate():
    uri = "ws://localhost:9009/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket 连接成功！")

            # 构造调用 browser_navigate 的 JSON-RPC 消息
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "browser_navigate",
                    "arguments": {
                        "url": "https://www.baidu.com"
                    }
                }
            }
            await websocket.send(json.dumps(request))
            print("已发送 browser_navigate 请求")

            # 等待服务器响应
            response = await websocket.recv()
            print("收到服务器响应：", response)

    except Exception as e:
        print("WebSocket 连接失败：", e)

if __name__ == "__main__":
    asyncio.run(test_browser_navigate())