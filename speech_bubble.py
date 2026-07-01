import time
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from config import BUBBLE_MAX_WIDTH, BUBBLE_FONT_SIZE, BUBBLE_PADDING, CAT_SIZE


class SpeechBubble:
    def __init__(self, parent):
        self.parent = parent
        self.text = None
        self.visible = False
        self.start_time = 0
        self.duration = 4

    def show(self, text, duration=4):
        self.text = text
        self.visible = True
        self.start_time = time.time()
        self.duration = duration
        self.parent.update()

    def hide(self):
        self.visible = False
        self.text = None
        self.parent.update()

    def update(self):
        if self.visible and time.time() - self.start_time >= self.duration:
            self.hide()

    def wrap_text(self, font, text):
        metrics = QFontMetrics(font)
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append("")
                continue
            current = ""
            for char in paragraph:
                test = current + char
                if metrics.horizontalAdvance(test) > BUBBLE_MAX_WIDTH:
                    if current:
                        lines.append(current)
                    current = char
                else:
                    current = test
            if current:
                lines.append(current)
        return lines

    def draw(self, painter):
        if not self.visible or not self.text:
            return

        font = QFont("Microsoft YaHei", BUBBLE_FONT_SIZE)
        painter.setFont(font)

        lines = self.wrap_text(font, self.text)
        if not lines:
            return

        metrics = QFontMetrics(font)
        line_h = metrics.height()

        max_w = 0
        for line in lines:
            w = metrics.horizontalAdvance(line) if line else 0
            if w > max_w:
                max_w = w

        pad = BUBBLE_PADDING
        bw = max_w + pad * 2
        bh = len(lines) * line_h + pad * 2

        # 获取屏幕边界
        screen = QApplication.primaryScreen().geometry()
        widget_pos = self.parent.mapToGlobal(self.parent.rect().topLeft())

        # 猫咪屏幕位置
        cat_screen_y = widget_pos.y() + 60  # 猫咪sprite在widget中的y偏移

        # 猫咪在屏幕上1/3区域时，气泡放下面；否则放上面
        if cat_screen_y < screen.height() // 3:
            y = 60 + CAT_SIZE + 5  # 猫咪下方
        else:
            y = 60 - bh - 5        # 猫咪头顶

        x = CAT_SIZE // 2 - bw // 2  # 水平居中

        # 检查是否超出屏幕边界，自动调整
        # 左边界
        if widget_pos.x() + x < 0:
            x = -widget_pos.x() + 5
        # 右边界
        if widget_pos.x() + x + bw > screen.width():
            x = screen.width() - widget_pos.x() - bw - 5
        # 下边界
        if widget_pos.y() + y + bh > screen.height():
            y = screen.height() - widget_pos.y() - bh - 5
        # 上边界
        if widget_pos.y() + y < 0:
            y = 5

        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(x, y, bw, bh)

        painter.setPen(Qt.black)
        for i, line in enumerate(lines):
            if line:
                tx = x + pad
                ty = y + pad + metrics.ascent() + i * line_h
                painter.drawText(tx, ty, line)
