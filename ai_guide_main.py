# -*- coding: utf-8 -*-
"""
AI引导主流程模块
协调截图、AI对话、输入框和引导执行
"""
import os
import threading
from screenshot import take_screenshot
from ai_guide import ask_ai
from guide_input import GuideInput
from hotkey_listener import HotkeyListener
from config import AI_OFFSET_X, AI_OFFSET_Y


class AIGuide:
    """AI引导主流程"""

    def __init__(self, guide_server=None):
        self.guide_server = guide_server
        self.input_box = GuideInput()
        self.hotkey_listener = HotkeyListener()
        self.screenshot_path = None

        self.input_box.submitted.connect(self.on_submit)
        self.input_box.cancelled.connect(self.on_cancel)
        self.hotkey_listener.triggered.connect(self.on_hotkey)

    def start(self):
        self.hotkey_listener.start()
        print("[AIGuide] 已启动，按Ctrl+Shift+H触发")

    def on_hotkey(self):
        print("[AIGuide] 截图中...")
        self.screenshot_path = take_screenshot()
        print(f"[AIGuide] 截图保存: {self.screenshot_path}")
        self.input_box.reset()
        self.input_box.show_at_center()

    def on_submit(self, question):
        print(f"[AIGuide] 问题: {question}")
        self.input_box.set_status("AI分析中...")
        self.input_box.send_btn.setEnabled(False)

        thread = threading.Thread(target=self._ask_ai_thread, args=(question,), daemon=True)
        thread.start()

    def _ask_ai_thread(self, question):
        result = ask_ai(question, self.screenshot_path)
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self.input_box, "on_ai_result",
            Qt.QueuedConnection,
            Q_ARG(object, result),
            Q_ARG(object, self.guide_server)
        )

    def on_cancel(self):
        """用户取消"""
        print("[AIGuide] 已取消")
        if self.screenshot_path and os.path.exists(self.screenshot_path):
            os.remove(self.screenshot_path)
