# -*- coding: utf-8 -*-
import os

# ===== 精灵图设置 =====
SPRITE_PATH = os.path.join(os.path.dirname(__file__), "cat_sprite_sheet.png")

# ===== 猫咪尺寸 =====
CAT_SIZE = 128  # 猫咪显示大小（像素）
FRAME_SIZE = 32      # 精灵图每帧原始大小

# ===== 鼠标跟随 =====
MOUSE_OFFSET_X = 30  # 鼠标X轴偏移量（猫咪在鼠标右侧）
MOUSE_OFFSET_Y = 50  # 鼠标Y轴偏移量（猫咪在鼠标下方）
MOUSE_LERP = 0.05  # 跟随平滑度（越大越快）
MOUSE_SPEED_THRESHOLD = 5  # 触发行走的速度阈值
RUN_SPEED_THRESHOLD = 100  # 触发奔跑的速度阈值

# ===== 动画设置 =====
IDLE_TIMEOUT = 15  # 多少秒无操作进入睡眠（秒）
IDLE_ANIM_SPEED = 0.4    # 待机动画速度
WALK_ANIM_SPEED = 0.8    # 行走动画速度
RUN_ANIM_SPEED = 1.2     # 奔跑动画速度
SLEEP_ANIM_SPEED = 0.2   # 睡眠动画速度
ANIM_TICK_MS = 100       # 动画刷新间隔（毫秒）

# ===== 对话气泡 =====
BUBBLE_MAX_WIDTH = 120   # 气泡最大宽度
BUBBLE_FONT_SIZE = 9     # 字体大小
BUBBLE_PADDING = 6       # 气泡内边距
BUBBLE_DURATION = 4      # 气泡显示时长（秒）
BUBBLE_OFFSET_X = -1    # 气泡X偏移
BUBBLE_OFFSET_Y = 0      # 气泡Y偏移

# ===== Widget尺寸 =====
WIDGET_EXTRA_W = 25     # widget额外宽度（气泡余量）
WIDGET_EXTRA_H = 150    # widget额外高度（气泡余量）

# ===== AI坐标偏移修正 =====
AI_OFFSET_X = 1  # AI解析X轴偏移量
AI_OFFSET_Y = 1  # AI解析Y轴偏移量

# ===== 引导偏移量 =====
GUIDE_OFFSET_X = -30  # 引导时X轴偏移（猫咪在目标左侧）
GUIDE_OFFSET_Y = -50  # 引导时Y轴偏移（猫咪在目标上方）

# ===== 日志 =====
LOG_ENABLED = True  # 是否启用日志输出到 log/ 目录
