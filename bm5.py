import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:9009/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket 连接成功！")
            # 你可以在这里发送/接收消息
            await websocket.send('{"test": "hello"}')
            # 如果服务器有回应，可以接收
            # response = await websocket.recv()
            # print("收到服务器消息：", response)
    except Exception as e:
        print("WebSocket 连接失败：", e)

if __name__ == "__main__":
    asyncio.run(test_ws())