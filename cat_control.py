import asyncio
import json
import websockets
import sys
import os

# 加载配置
sys.path.insert(0, os.path.dirname(__file__))
from config import GUIDE_OFFSET_X, GUIDE_OFFSET_Y

async def guide(x, y, text=""):
    # 应用偏移：发送的坐标是鼠标位置，需要转换为猫咪位置
    cat_x = x + GUIDE_OFFSET_X
    cat_y = y + GUIDE_OFFSET_Y
    ws = await websockets.connect('ws://127.0.0.1:19233')
    await ws.send(json.dumps({'A': {'x': cat_x, 'y': cat_y, 'text': text}}))
    await ws.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python cat_control.py <x> <y> [text]")
        print("  x, y: 鼠标位置坐标（目标位置）")
        print(f"  当前引导偏移量: X={GUIDE_OFFSET_X}, Y={GUIDE_OFFSET_Y}")
        sys.exit(1)
    x, y = int(sys.argv[1]), int(sys.argv[2])
    text = sys.argv[3] if len(sys.argv) > 3 else ""
    asyncio.run(guide(x, y, text))
    print(f"已引导猫咪到目标位置 ({x}, {y})")