import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter
from speech_bubble import SpeechBubble
from config import (
    CAT_SIZE, FRAME_SIZE, IDLE_ANIM_SPEED, WALK_ANIM_SPEED,
    RUN_ANIM_SPEED, SLEEP_ANIM_SPEED, ANIM_TICK_MS,
    WIDGET_EXTRA_W, WIDGET_EXTRA_H
)


class CatSprite(QWidget):
    IDLE = 0
    WALKING = 1
    RUNNING = 2
    SLEEPING = 3

    def __init__(self, sprite_path):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(CAT_SIZE + WIDGET_EXTRA_W, CAT_SIZE + WIDGET_EXTRA_H)

        self.sprite_sheet = None
        if sprite_path:
            try:
                self.sprite_sheet = QPixmap(sprite_path)
            except:
                pass

        self._state = self.IDLE
        self.current_frame = 0
        self.frame_accumulator = 0.0
        self.idle_row = 0
        self.idle_change_timer = 0
        self.flipped = False

        self.bubble = SpeechBubble(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(ANIM_TICK_MS)

    def set_state(self, state):
        if self._state != state:
            self._state = state
            self.current_frame = 0
            if state == self.IDLE:
                self.idle_row = random.choice([0, 1, 2, 3])

    def show_text(self, text, duration=4):
        self.bubble.show(text, duration)

    def _tick(self):
        self.bubble.update()

        if self._state == self.IDLE:
            speed = IDLE_ANIM_SPEED
            self.idle_change_timer += 1
            if self.idle_change_timer > 50:
                self.idle_row = random.choice([0, 1, 2, 3])
                self.idle_change_timer = 0
        elif self._state == self.WALKING:
            speed = WALK_ANIM_SPEED
            self.idle_change_timer = 0
        elif self._state == self.RUNNING:
            speed = RUN_ANIM_SPEED
            self.idle_change_timer = 0
        else:
            speed = SLEEP_ANIM_SPEED

        self.frame_accumulator += speed
        if self.frame_accumulator >= 1.0:
            self.current_frame += int(self.frame_accumulator)
            self.frame_accumulator -= int(self.frame_accumulator)
            if self.current_frame >= 4:
                self.current_frame = 0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        self.bubble.draw(painter)

        if self.sprite_sheet:
            row = self._state_map()
            x = self.current_frame * FRAME_SIZE
            y = row * FRAME_SIZE
            frame = self.sprite_sheet.copy(x, y, FRAME_SIZE, FRAME_SIZE)
            scaled = frame.scaled(CAT_SIZE, CAT_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation)
            if self.flipped:
                painter.translate(CAT_SIZE, 60)
                painter.scale(-1, 1)
                painter.drawPixmap(0, 0, scaled)
            else:
                painter.drawPixmap(0, 60, scaled)

        painter.end()

    def _state_map(self):
        if self._state == self.IDLE:
            return self.idle_row
        elif self._state == self.WALKING:
            return 4
        elif self._state == self.RUNNING:
            return 5
        elif self._state == self.SLEEPING:
            return 6
        return 0
