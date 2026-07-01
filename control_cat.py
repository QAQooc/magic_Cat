import asyncio
import json
import websockets
import sys
import ctypes

# 尝试获取屏幕分辨率
try:
    # 使用Windows API获取屏幕分辨率
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    print(f"屏幕分辨率: {screen_width}x{screen_height}")
except Exception as e:
    print(f"获取屏幕分辨率失败: {e}，使用默认分辨率1920x1080")
    screen_width, screen_height = 1920, 1080

# 计算屏幕中心坐标
center_x = screen_width // 2
center_y = screen_height // 2
print(f"屏幕中心坐标: ({center_x}, {center_y})")

async def control_cat():
    uri = "ws://127.0.0.1:19233"
    try:
        async with websockets.connect(uri) as websocket:
            # 构造控制消息
            message = {
                "A": {
                    "x": center_x,
                    "y": center_y,
                    "text": "你好"
                }
            }
            
            print(f"发送控制消息: {json.dumps(message, ensure_ascii=False)}")
            await websocket.send(json.dumps(message))
            
            # 等待一小段时间确保消息发送成功
            await asyncio.sleep(0.1)
            print("控制消息已发送，猫咪应该正在移动到屏幕中心...")
            
    except ConnectionRefusedError:
        print("错误: 无法连接到端口19233，猫咪程序可能未运行")
        print("请先启动猫咪程序: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"连接错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(control_cat())