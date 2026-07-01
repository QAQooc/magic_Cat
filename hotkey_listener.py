# -*- coding: utf-8 -*-
"""
快捷键监听模块
监听Ctrl+Shift+H触发截图
"""
import keyboard
from PyQt5.QtCore import QObject, pyqtSignal


class HotkeyListener(QObject):
    """快捷键监听器"""

    triggered = pyqtSignal()

    def __init__(self, hotkey="ctrl+shift+h"):
        super().__init__()
        self.hotkey = hotkey
        self._listener = None

    def start(self):
        """开始监听"""
        keyboard.add_hotkey(self.hotkey, self._on_trigger)
        print(f"[Hotkey] 已注册: {self.hotkey}")

    def _on_trigger(self):
        """快捷键触发回调"""
        print(f"[Hotkey] 触发: {self.hotkey}")
        self.triggered.emit()

    def stop(self):
        """停止监听"""
        keyboard.unhook_all()
