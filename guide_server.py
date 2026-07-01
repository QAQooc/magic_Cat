# -*- coding: utf-8 -*-
"""
猫咪引导WebSocket服务器
端口19233，接收AI或手动触发的引导消息
"""
import os
import json
import threading
import asyncio

PLUGIN_DIR = os.path.dirname(__file__)


class GuideServer:
    """引导WebSocket服务器"""

    def __init__(self, app=None, port=19233):
        self.app = app
        self.port = port
        self.running = False
        self.server = None
        self.thread = None

    async def handle_client(self, websocket):
        """处理客户端连接"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self._process_guide(data)
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    def _process_guide(self, data):
        """处理引导数据"""
        import logger
        if not self.app:
            return

        waypoints = []
        for key in sorted(data.keys()):
            point = data[key]
            waypoints.append({
                "pos": (point.get("x", 0), point.get("y", 0)),
                "text": point.get("text", "")
            })

        if waypoints:
            logger.log(f"[GuideServer] 收到引导指令: {len(waypoints)} 个点")
            self.app.start_guidance(waypoints)

    async def start_server_async(self):
        """启动WebSocket服务器"""
        try:
            import websockets
            self.server = await websockets.serve(
                self.handle_client,
                "127.0.0.1",
                self.port
            )
            print(f"Guide服务器已启动 | 端口: {self.port}")
            await self.server.wait_closed()
        except ImportError:
            print("未安装websockets，Guide功能不可用")
        except Exception as e:
            print(f"Guide服务器启动失败: {str(e)}")

    def _run_server(self):
        """在新线程中运行服务器"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_server_async())

    def start(self):
        """启动服务器（非阻塞）"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server:
            self.server.close()
