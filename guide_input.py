# -*- coding: utf-8 -*-
"""
PyQt5输入框模块
长条型简洁风格，深灰浅灰配色
"""
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPainter, QColor

# 配色
BG_COLOR = "#3a3a3a"        # 深灰背景
INPUT_BG = "#2a2a2a"        # 输入框深色
LIGHT = "#e0e0e0"           # 浅灰文字
MID = "#b5b5b5"             # 中灰
PINK = "#de7586"            # 粉色（取消按钮）
BTN_BG = "#4a4a4a"          # 按钮背景
BTN_HOVER = "#555555"       # 按钮悬停

STYLE = """
QWidget {
    background: """ + BG_COLOR + """;
}
QTextEdit {
    background: """ + INPUT_BG + """;
    color: """ + LIGHT + """;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 5px;
    font-size: 12px;
    font-family: "Microsoft YaHei";
}
QTextEdit:focus {
    border: 1px solid """ + MID + """;
}
QPushButton#send_btn {
    background: """ + BTN_BG + """;
    color: """ + LIGHT + """;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 8px 16px;
    font-size: 12px;
    font-family: "Microsoft YaHei";
}
QPushButton#send_btn:hover {
    background: """ + BTN_HOVER + """;
}
QPushButton#cancel_btn {
    background: transparent;
    color: """ + PINK + """;
    border: 1px solid """ + PINK + """;
    border-radius: 3px;
    padding: 8px 16px;
    font-size: 12px;
    font-family: "Microsoft YaHei";
}
QPushButton#cancel_btn:hover {
    background: """ + PINK + """;
    color: white;
}
QLabel#status {
    color: """ + MID + """;
    font-size: 10px;
    background: transparent;
}
"""


class GuideInput(QWidget):
    submitted = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("魔法猫咪")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(500, 45)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("输入问题，例如：Roto笔刷怎么改大小？")
        self.text_edit.setMaximumHeight(35)
        self.text_edit.setMinimumWidth(280)
        layout.addWidget(self.text_edit)

        self.send_btn = QPushButton("提问")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setFixedHeight(35)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self.on_submit)
        layout.addWidget(self.send_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setFixedHeight(35)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_btn)

        self.setStyleSheet(STYLE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(BG_COLOR))
        painter.drawRoundedRect(self.rect(), 6, 6)
        painter.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def on_submit(self):
        text = self.text_edit.toPlainText().strip()
        if text:
            self.send_btn.setText("分析中...")
            self.send_btn.setEnabled(False)
            self.submitted.emit(text)

    def on_cancel(self):
        self.cancelled.emit()
        self.close()

    def set_status(self, text):
        self.send_btn.setText(text[:8] if len(text) > 8 else text)

    def reset(self):
        self.text_edit.clear()
        self.send_btn.setText("提问")
        self.send_btn.setEnabled(True)

    def show_at_center(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - 80  # 屏幕底部，状态栏上方
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    @pyqtSlot(object, object)
    def on_ai_result(self, result, guide_server):
        from config import AI_OFFSET_X, AI_OFFSET_Y
        import logger

        answer = result.get("answer", "无回答")
        steps = result.get("steps", [])

        logger.log(f"[AIGuide] answer: {answer}")
        logger.log(f"[AIGuide] steps数量: {len(steps)}, raw: {steps}")

        display_answer = answer[:60] + "..." if len(answer) > 60 else answer
        self.set_status(f"回答: {display_answer}")
        self.send_btn.setEnabled(True)

        if steps and guide_server:
            try:
                waypoints = []
                for s in steps:
                    x = s.get("x", 0)
                    y = s.get("y", 0)
                    if isinstance(x, list):
                        x = x[0] if x else 0
                    if isinstance(y, list):
                        y = y[0] if y else 0
                    waypoints.append({"pos": (int(x) + AI_OFFSET_X, int(y) + AI_OFFSET_Y), "text": s.get("text", "")})
                logger.log(f"[AIGuide] waypoints: {waypoints}")
                guide_server.app.start_guidance(waypoints)
                logger.log(f"[AIGuide] 引导已启动")
            except Exception as e:
                logger.log(f"[AIGuide] 引导启动失败: {e}")
        else:
            # 兜底：当没有引导坐标时，使用屏幕中央坐标显示回答
            bubble_text = answer if answer and answer.strip() else "喵~"
            if guide_server:
                try:
                    screen = self.screen()
                    if screen:
                        screen_geo = screen.geometry()
                        center_x = screen_geo.width() // 2
                        center_y = screen_geo.height() // 2
                    else:
                        center_x = 960
                        center_y = 540
                    default_waypoint = [{"pos": (center_x + AI_OFFSET_X, center_y + AI_OFFSET_Y), "text": bubble_text}]
                    logger.log(f"[AIGuide] 兜底引导: pos=({center_x},{center_y}), text={bubble_text}")
                    guide_server.app.start_guidance(default_waypoint)
                    logger.log(f"[AIGuide] 兜底引导已启动")
                except Exception as e:
                    logger.log(f"[AIGuide] 兜底引导启动失败: {e}")

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, self.close)
