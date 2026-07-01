import asyncio
import json
import websockets

async def guide():
    ws = await websockets.connect('ws://127.0.0.1:19233')
    await ws.send(json.dumps({'A': {'x': 13, 'y': 709, 'text': '腾讯QQ在这里'}}))
    print('已发送引导指令')
    await ws.close()

asyncio.run(guide())