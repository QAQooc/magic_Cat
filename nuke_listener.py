# -*- coding: utf-8 -*-
"""
Nuke通信监听模块
接收Nuke创建节点的消息，在猫咪对话气泡中显示对应台词
"""
import os
import json
import random
import threading
import asyncio

# 台词配置
PLUGIN_DIR = os.path.dirname(__file__)
DIALOG_FILE = os.path.join(PLUGIN_DIR, "nuke_dialogs.txt")
NODE_DIALOGS = {}
DEFAULT_DIALOGS = [
    "新节点创建成功~",
    "主人工作好认真哦",
    "节点就位，准备开工",
    "加油加油，快完成啦",
    "你超厉害的！"
]


def load_dialogs():
    """加载台词文件"""
    global NODE_DIALOGS, DEFAULT_DIALOGS
    try:
        if not os.path.exists(DIALOG_FILE):
            return
        with open(DIALOG_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        current_node = None
        current_list = []
        default_list = []
        for line in lines:
            if line.startswith("[") and line.endswith("]"):
                if current_node and current_list:
                    if current_node == "DEFAULT":
                        default_list = current_list
                    else:
                        NODE_DIALOGS[current_node] = current_list.copy()
                current_node = line[1:-1].strip()
                current_list = []
            else:
                current_list.append(line)
        if current_node and current_list:
            if current_node == "DEFAULT":
                default_list = current_list
            else:
                NODE_DIALOGS[current_node] = current_list.copy()
        if default_list:
            DEFAULT_DIALOGS = default_list
        print(f"Nuke台词加载成功 | 已加载 {len(NODE_DIALOGS)} 个节点台词")
    except Exception as e:
        print(f"Nuke台词加载失败，使用默认台词：{str(e)}")


load_dialogs()


class NukeListener:
    """Nuke通信监听器"""

    def __init__(self, cat_sprite=None, port=19232):
        self.cat_sprite = cat_sprite
        self.port = port
        self.running = False
        self.server = None
        self.thread = None

    def get_dialog(self, node_class):
        """获取节点对应的台词"""
        lines = NODE_DIALOGS.get(node_class, DEFAULT_DIALOGS)
        return random.choice(lines)

    async def handle_client(self, websocket):
        """处理客户端连接"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    node_class = data.get("node", "")
                    text = data.get("text", "")

                    if node_class and self.cat_sprite:
                        dialog = self.get_dialog(node_class)
                        self.cat_sprite.show_text(dialog)
                        print(f"[Nuke → 猫咪] {node_class}: {dialog}")
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    async def start_server_async(self):
        """启动WebSocket服务器"""
        try:
            import websockets
            self.server = await websockets.serve(
                self.handle_client,
                "127.0.0.1",
                self.port
            )
            print(f"Nuke监听服务器已启动 | 端口: {self.port}")
            await self.server.wait_closed()
        except ImportError:
            print("未安装websockets，Nuke监听功能不可用")
        except Exception as e:
            print(f"Nuke监听服务器启动失败: {str(e)}")

    def _run_server(self):
        """在新线程中运行服务器"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_server_async())

    def start(self):
        """启动监听（非阻塞）"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def stop(self):
        """停止监听"""
        self.running = False
        if self.server:
            self.server.close()
