import asyncio
import websockets
import json

async def test_browser_navigate():
    uri = "ws://localhost:9009/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket 连接成功！")

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

            response = await websocket.recv()
            print("收到服务器响应：", response)

            # 自动判断是否成功
            resp = json.loads(response)
            if "result" in resp:
                print("调用成功，返回内容：", resp["result"])
            elif "error" in resp:
                print("调用失败，错误信息：", resp["error"])
            else:
                print("未知响应格式：", resp)

    except Exception as e:
        print("WebSocket 连接失败：", e)

if __name__ == "__main__":
    asyncio.run(test_browser_navigate())