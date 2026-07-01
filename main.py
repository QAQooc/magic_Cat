# -*- coding: utf-8 -*-
import sys
import math
import time
import logger
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QCursor
from sprite import CatSprite
from config import (
    SPRITE_PATH, MOUSE_OFFSET_X, MOUSE_OFFSET_Y, MOUSE_LERP,
    MOUSE_SPEED_THRESHOLD, RUN_SPEED_THRESHOLD, IDLE_TIMEOUT, CAT_SIZE,
    WIDGET_EXTRA_W, WIDGET_EXTRA_H, AI_OFFSET_X, AI_OFFSET_Y
)
from nuke_listener import NukeListener
from guide_server import GuideServer
from ai_guide_main import AIGuide
from tray_menu import TrayMenu


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        from config import LOG_ENABLED
        logger.init(LOG_ENABLED)
        logger.log("[App] 启动")
        self.sprite = CatSprite(SPRITE_PATH)

        # 可实时更新的参数
        self.mouse_lerp = MOUSE_LERP
        self.speed_threshold = MOUSE_SPEED_THRESHOLD
        self.run_threshold = RUN_SPEED_THRESHOLD
        self.idle_timeout = IDLE_TIMEOUT
        self.offset_x = MOUSE_OFFSET_X
        self.offset_y = MOUSE_OFFSET_Y

        screen = self.app.primaryScreen().geometry()
        cat_x = screen.width() // 2 - CAT_SIZE // 2
        cat_y = screen.height() // 2 - CAT_SIZE // 2
        self.sprite.move(cat_x, cat_y - WIDGET_EXTRA_H)
        self.sprite.show()

        self.sprite.show_text("你好！我是猫咪助手~")
        QTimer.singleShot(5000, lambda: self.sprite.show_text("有什么可以帮你的吗？"))
        QTimer.singleShot(10000, lambda: self.sprite.show_text("喵喵喵~"))

        self.pos = QPointF(cat_x, cat_y)
        self.dragging = False
        self.last_move_time = time.time()

        self.screen = self.app.primaryScreen().geometry()
        self._min_x = 2
        self._max_x = self.screen.width() - CAT_SIZE - 2
        self._min_y = -WIDGET_EXTRA_H + 10
        self._max_y = self.screen.height() - CAT_SIZE + 10

        self._guided = False
        self._completed = False
        self._following = True
        self._guide_queue = []
        self._guide_current = None
        self._guide_wait = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.follow)
        self.timer.start(16)

        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start(1000)

        self.sprite.mousePressEvent = self.press
        self.sprite.mouseReleaseEvent = self.release

        self.nuke_listener = NukeListener(cat_sprite=self.sprite)
        self.nuke_listener.start()

        self.guide_server = GuideServer(app=self)
        self.guide_server.start()

        self.ai_guide = AIGuide(guide_server=self.guide_server)
        self.ai_guide.start()

        # 系统托盘
        self.tray_menu = TrayMenu(app=self)
        self.tray_menu.setup()

    def update_settings(self, settings):
        """实时更新运行参数"""
        if "MOUSE_LERP" in settings:
            self.mouse_lerp = settings["MOUSE_LERP"]
        if "MOUSE_SPEED_THRESHOLD" in settings:
            self.speed_threshold = settings["MOUSE_SPEED_THRESHOLD"]
        if "RUN_SPEED_THRESHOLD" in settings:
            self.run_threshold = settings["RUN_SPEED_THRESHOLD"]
        if "IDLE_TIMEOUT" in settings:
            self.idle_timeout = settings["IDLE_TIMEOUT"]
        if "MOUSE_OFFSET_X" in settings:
            self.offset_x = settings["MOUSE_OFFSET_X"]
        if "MOUSE_OFFSET_Y" in settings:
            self.offset_y = settings["MOUSE_OFFSET_Y"]
        print(f"[Settings] 参数已更新: lerp={self.mouse_lerp}, 速度阈值={self.speed_threshold}/{self.run_threshold}")

    def toggle_follow(self):
        """切换跟随状态"""
        self._following = not self._following
        if self._following:
            self.sprite.set_state(self.sprite.IDLE)
            self.last_move_time = time.time()
            print("[Follow] 恢复跟随")
        else:
            self._guided = False
            self._completed = False
            self.sprite.bubble.hide()
            screen = self.app.primaryScreen().geometry()
            x = screen.width() - CAT_SIZE - 10
            y = screen.height() - CAT_SIZE - 10
            self.pos = QPointF(x, y)
            self.sprite.move(int(x), int(y) - WIDGET_EXTRA_H)
            self.sprite.set_state(self.sprite.SLEEPING)
            print("[Follow] 停止跟随，移至右下角")
        return self._following

    def _clamp_pos(self):
        x = max(self._min_x, min(self._max_x, self.pos.x()))
        y = max(self._min_y, min(self._max_y, self.pos.y()))
        self.pos.setX(x)
        self.pos.setY(y)

    def follow(self):
        if self.dragging or not self._following:
            return

        if self._guided:
            self._tick_guide()
            return

        if self._completed:
            return

        cp = QCursor.pos()
        dx = cp.x() - self.pos.x() + self.offset_x
        dy = cp.y() - self.pos.y() + self.offset_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self.run_threshold:
            self.last_move_time = time.time()
            self.sprite.set_state(self.sprite.RUNNING)
            self.sprite.flipped = dx < 0
        elif dist > self.speed_threshold:
            self.last_move_time = time.time()
            self.sprite.set_state(self.sprite.WALKING)
            self.sprite.flipped = dx < 0
        else:
            if self.sprite._state != self.sprite.SLEEPING:
                self.sprite.set_state(self.sprite.IDLE)
        self.pos.setX(self.pos.x() + dx * self.mouse_lerp)
        self.pos.setY(self.pos.y() + dy * self.mouse_lerp)
        self._clamp_pos()
        self.sprite.move(int(self.pos.x()), int(self.pos.y()) - WIDGET_EXTRA_H)

    def start_guidance(self, waypoints):
        logger.log(f"[Guide] start_guidance 收到 {len(waypoints)} 个点: {waypoints}")
        self._guided = True
        self._guide_queue = list(waypoints)
        self._guide_current = None
        self._guide_wait = 0
        self._next_guide_point()

    def _next_guide_point(self):
        if not self._guide_queue:
            self._guided = False
            self._completed = False
            self.sprite.bubble.hide()
            self.sprite.set_state(self.sprite.IDLE)
            self.last_move_time = time.time()
            print("[Guide] 引导完成，已恢复跟随")
            return
        self._guide_current = self._guide_queue.pop(0)
        self._guide_wait = 0

    def _tick_guide(self):
        if self._guide_wait > 0:
            self._guide_wait -= 1
            if self._guide_wait <= 0:
                self._next_guide_point()
            return

        if not self._guide_current:
            return

        tx, ty = self._guide_current["pos"]
        tx = max(self._min_x, min(self._max_x, tx))
        ty = max(self._min_y, min(self._max_y, ty))
        dx = tx - self.pos.x()
        dy = ty - self.pos.y()
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 10:
            self.sprite.set_state(self.sprite.IDLE)
            text = self._guide_current.get("text", "")
            logger.log(f"[Guide] 到达目标 pos=({self.pos.x():.0f},{self.pos.y():.0f}), text='{text}'")
            if text:
                self.sprite.show_text(text, duration=15)
                logger.log(f"[Guide] 气泡已显示")
            else:
                logger.log(f"[Guide] text为空，跳过气泡")
            self._guide_current = None
            self._guide_wait = 937
            return

        self.sprite.set_state(self.sprite.WALKING)
        self.sprite.flipped = dx < 0
        self.pos.setX(self.pos.x() + dx * self.mouse_lerp)
        self.pos.setY(self.pos.y() + dy * self.mouse_lerp)
        self._clamp_pos()
        self.sprite.move(int(self.pos.x()), int(self.pos.y()) - WIDGET_EXTRA_H)

    def _reset_to_follow(self):
        self._completed = False
        self.sprite.bubble.hide()
        self.sprite.set_state(self.sprite.IDLE)
        self.last_move_time = time.time()
        print("[Guide] 已恢复跟随鼠标")

    def check_idle(self):
        if time.time() - self.last_move_time > self.idle_timeout:
            if self.sprite._state != self.sprite.SLEEPING:
                self.sprite.set_state(self.sprite.SLEEPING)

    def press(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True

    def release(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False

    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    App().run()
