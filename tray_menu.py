# -*- coding: utf-8 -*-
"""
系统托盘菜单模块
"""
import os
import json
from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QDialog,
    QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QGroupBox, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor
import webbrowser

PLUGIN_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(PLUGIN_DIR, "config.py")
API_CONFIG_PATH = os.path.join(PLUGIN_DIR, "api_config.py")

STYLE = """
QDialog {
    background: #232322;
}
QTabWidget::pane {
    border: 2px solid #2f2f2e;
    background: #2a2a2a;
}
QTabBar::tab {
    background: #3a3a3a;
    color: #b5b5b5;
    padding: 8px 16px;
    border: 2px solid #2f2f2e;
    font-size: 12px;
    font-family: "Microsoft YaHei";
}
QTabBar::tab:selected {
    background: #2a2a2a;
    color: #e0e0e0;
    border-bottom: 2px solid #de7586;
}
QGroupBox {
    color: #e0e0e0;
    border: 2px solid #2f2f2e;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 15px;
    font-size: 12px;
    font-family: "Microsoft YaHei";
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLabel {
    color: #b5b5b5;
    font-size: 11px;
    font-family: "Microsoft YaHei";
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #1e1e1e;
    color: #e0e0e0;
    border: 2px solid #2f2f2e;
    border-radius: 3px;
    padding: 5px;
    font-size: 11px;
    font-family: "Microsoft YaHei";
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #b5b5b5;
}
QPushButton {
    background: #3a3a3a;
    color: #e0e0e0;
    border: 2px solid #2f2f2e;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: bold;
    font-family: "Microsoft YaHei";
}
QPushButton:hover {
    background: #555;
    border: 2px solid #b5b5b5;
}
QPushButton#save_btn {
    background: #2f2f2e;
    color: #e0e0e0;
}
QPushButton#save_btn:hover {
    background: #555;
}
QPushButton#cancel_btn {
    background: transparent;
    color: #de7586;
    border: 2px solid #de7586;
}
QPushButton#cancel_btn:hover {
    background: #de7586;
    color: white;
}
"""


def read_config():
    """读取config.py中的参数"""
    config = {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # 简单解析配置值
        for line in content.split("\n"):
            line = line.strip()
            if "=" in line and not line.startswith("#") and not line.startswith("import"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip().split("#")[0].strip().strip('"').strip("'")
                    try:
                        if "." in val:
                            config[key] = float(val)
                        else:
                            config[key] = int(val)
                    except ValueError:
                        config[key] = val
    except Exception as e:
        print(f"[Config] 读取失败: {e}")
    return config


def write_config(key, value):
    """修改config.py中的单个参数"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
                    # 保留注释
                    comment = ""
                    if "#" in line:
                        comment = "  " + line.split("#", 1)[1].strip()
                        comment = "  # " + comment.lstrip("# ")
                    if isinstance(value, float):
                        f.write(f"{key} = {value}{comment}\n")
                    elif isinstance(value, int):
                        f.write(f"{key} = {value}{comment}\n")
                    else:
                        f.write(f'{key} = "{value}"{comment}\n')
                else:
                    f.write(line)
        print(f"[Config] 已更新 {key} = {value}")
    except Exception as e:
        print(f"[Config] 写入失败: {e}")


def read_api_config():
    """读取api_config.py中的模型配置"""
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location("api_config", API_CONFIG_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {
            "DEFAULT_MODEL": mod.DEFAULT_MODEL,
            "MODELS": mod.MODELS
        }
    except Exception as e:
        print(f"[API Config] 读取失败: {e}")
        return {"DEFAULT_MODEL": "xiaomi", "MODELS": {}}


def write_api_config(model_name, field, value):
    """修改api_config.py中的模型配置"""
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # 定位模型块并修改字段
        import re
        # 找到模型块
        pattern = rf'("{model_name}":\s*\{{[^}}]*)("{field}":\s*)([^,\}}]+)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            old_val = match.group(3).strip()
            if isinstance(value, (int, float)):
                new_val = str(value)
            else:
                new_val = f'"{value}"'
            new_content = content[:match.start(3)] + new_val + content[match.end(3):]
            with open(API_CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[API Config] 已更新 {model_name}.{field} = {value}")
        else:
            print(f"[API Config] 未找到 {model_name}.{field}")
    except Exception as e:
        print(f"[API Config] 写入失败: {e}")


def write_default_model(model_name):
    """修改默认模型"""
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(API_CONFIG_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip().startswith("DEFAULT_MODEL"):
                    f.write(f'DEFAULT_MODEL = "{model_name}"\n')
                else:
                    f.write(line)
        print(f"[API Config] 默认模型已改为 {model_name}")
    except Exception as e:
        print(f"[API Config] 写入失败: {e}")


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("魔法猫咪 - 设置")
        self.setWindowFlags(Qt.Dialog)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setMinimumWidth(450)
        self.setStyleSheet(STYLE)

        self.config = read_config()
        self.api_config = read_api_config()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        tabs = QTabWidget()
        tabs.addTab(self.create_ui_tab(), "界面设置")
        tabs.addTab(self.create_api_tab(), "API设置")
        layout.addWidget(tabs)

        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.hide)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_ui_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 猫咪参数
        cat_group = QGroupBox("猫咪参数")
        cat_form = QFormLayout()
        self.cat_size = QSpinBox()
        self.cat_size.setRange(32, 512)
        self.cat_size.setValue(self.config.get("CAT_SIZE", 128))
        cat_form.addRow("猫咪大小 (px):", self.cat_size)

        self.mouse_lerp = QDoubleSpinBox()
        self.mouse_lerp.setRange(0.01, 1.0)
        self.mouse_lerp.setSingleStep(0.01)
        self.mouse_lerp.setValue(self.config.get("MOUSE_LERP", 0.05))
        cat_form.addRow("跟随平滑度:", self.mouse_lerp)

        self.speed_threshold = QSpinBox()
        self.speed_threshold.setRange(1, 100)
        self.speed_threshold.setValue(self.config.get("MOUSE_SPEED_THRESHOLD", 5))
        cat_form.addRow("行走速度阈值:", self.speed_threshold)

        self.run_threshold = QSpinBox()
        self.run_threshold.setRange(5, 200)
        self.run_threshold.setValue(self.config.get("RUN_SPEED_THRESHOLD", 15))
        cat_form.addRow("奔跑速度阈值:", self.run_threshold)

        self.idle_timeout = QSpinBox()
        self.idle_timeout.setRange(5, 300)
        self.idle_timeout.setValue(self.config.get("IDLE_TIMEOUT", 30))
        cat_form.addRow("待机超时 (秒):", self.idle_timeout)

        cat_group.setLayout(cat_form)
        layout.addWidget(cat_group)

        # 偏移参数
        offset_group = QGroupBox("偏移参数")
        offset_form = QFormLayout()
        self.offset_x = QSpinBox()
        self.offset_x.setRange(-200, 200)
        self.offset_x.setValue(self.config.get("MOUSE_OFFSET_X", -30))
        offset_form.addRow("鼠标X偏移:", self.offset_x)

        self.offset_y = QSpinBox()
        self.offset_y.setRange(-200, 200)
        self.offset_y.setValue(self.config.get("MOUSE_OFFSET_Y", -50))
        offset_form.addRow("鼠标Y偏移:", self.offset_y)

        self.ai_offset_x = QSpinBox()
        self.ai_offset_x.setRange(-500, 500)
        self.ai_offset_x.setValue(self.config.get("AI_OFFSET_X", -77))
        offset_form.addRow("AI坐标X偏移:", self.ai_offset_x)

        self.ai_offset_y = QSpinBox()
        self.ai_offset_y.setRange(-500, 500)
        self.ai_offset_y.setValue(self.config.get("AI_OFFSET_Y", 13))
        offset_form.addRow("AI坐标Y偏移:", self.ai_offset_y)

        offset_group.setLayout(offset_form)
        layout.addWidget(offset_group)

        # 日志设置
        log_group = QGroupBox("日志")
        log_form = QFormLayout()
        self.log_enabled = QComboBox()
        self.log_enabled.addItems(["关闭", "开启"])
        log_val = self.config.get("LOG_ENABLED", False)
        if isinstance(log_val, str):
            log_val = log_val.lower() == "true"
        self.log_enabled.setCurrentIndex(1 if log_val else 0)
        log_form.addRow("运行日志:", self.log_enabled)
        log_group.setLayout(log_form)
        layout.addWidget(log_group)

        return tab

    def create_api_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 模型选择
        model_group = QGroupBox("默认模型")
        model_form = QFormLayout()
        self.model_combo = QComboBox()
        models = self.api_config.get("MODELS", {})
        self.model_combo.addItems(models.keys())
        current = self.api_config.get("DEFAULT_MODEL", "xiaomi")
        idx = self.model_combo.findText(current)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_form.addRow("选择模型:", self.model_combo)
        model_group.setLayout(model_form)
        layout.addWidget(model_group)

        # 获取API密钥链接
        link_label = QLabel('<a href="https://openai-hk.com/?i=35006" style="color: #de7586;">获取你的API密钥</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setStyleSheet("font-size: 12px; margin: 5px;")
        layout.addWidget(link_label)

        # 模型详情
        detail_group = QGroupBox("模型配置")
        self.detail_form = QFormLayout()
        self.gateway_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.model_name_input = QLineEdit()
        self.temp_input = QDoubleSpinBox()
        self.temp_input.setRange(0, 2)
        self.temp_input.setSingleStep(0.1)
        self.max_tokens_input = QSpinBox()
        self.max_tokens_input.setRange(100, 32000)
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(5, 120)

        self.detail_form.addRow("网关地址:", self.gateway_input)
        self.detail_form.addRow("API密钥:", self.api_key_input)
        self.detail_form.addRow("模型名称:", self.model_name_input)
        self.detail_form.addRow("温度:", self.temp_input)
        self.detail_form.addRow("最大token:", self.max_tokens_input)
        self.detail_form.addRow("超时(秒):", self.timeout_input)
        detail_group.setLayout(self.detail_form)
        layout.addWidget(detail_group)

        # 加载当前模型配置
        self.on_model_changed(current)

        return tab

    def on_model_changed(self, model_name):
        models = self.api_config.get("MODELS", {})
        m = models.get(model_name, {})
        self.gateway_input.setText(m.get("gateway_url", ""))
        self.api_key_input.setText(m.get("api_key", ""))
        self.model_name_input.setText(m.get("model_name", ""))
        self.temp_input.setValue(m.get("temperature", 0.7))
        self.max_tokens_input.setValue(m.get("max_tokens", 1000))
        self.timeout_input.setValue(m.get("timeout", 30))

    def save_settings(self):
        # 保存界面设置
        write_config("CAT_SIZE", self.cat_size.value())
        write_config("MOUSE_LERP", self.mouse_lerp.value())
        write_config("MOUSE_SPEED_THRESHOLD", self.speed_threshold.value())
        write_config("RUN_SPEED_THRESHOLD", self.run_threshold.value())
        write_config("IDLE_TIMEOUT", self.idle_timeout.value())
        write_config("MOUSE_OFFSET_X", self.offset_x.value())
        write_config("MOUSE_OFFSET_Y", self.offset_y.value())
        write_config("AI_OFFSET_X", self.ai_offset_x.value())
        write_config("AI_OFFSET_Y", self.ai_offset_y.value())
        log_on = self.log_enabled.currentIndex() == 1
        write_config("LOG_ENABLED", log_on)

        # 保存API设置
        model_name = self.model_combo.currentText()
        write_default_model(model_name)
        write_api_config(model_name, "gateway_url", self.gateway_input.text())
        write_api_config(model_name, "api_key", self.api_key_input.text())
        write_api_config(model_name, "model_name", self.model_name_input.text())
        write_api_config(model_name, "temperature", self.temp_input.value())
        write_api_config(model_name, "max_tokens", self.max_tokens_input.value())
        write_api_config(model_name, "timeout", self.timeout_input.value())

        # 发送实时更新参数
        settings = {
            "MOUSE_LERP": self.mouse_lerp.value(),
            "MOUSE_SPEED_THRESHOLD": self.speed_threshold.value(),
            "RUN_SPEED_THRESHOLD": self.run_threshold.value(),
            "IDLE_TIMEOUT": self.idle_timeout.value(),
            "MOUSE_OFFSET_X": self.offset_x.value(),
            "MOUSE_OFFSET_Y": self.offset_y.value(),
        }
        self.settings_changed.emit(settings)

        QMessageBox.information(self, "保存成功", "设置已保存！\n猫咪大小、AI坐标偏移和日志设置需要重启生效。")
        self.hide()


class TrayMenu:
    def __init__(self, app=None):
        self.app = app
        self.tray = None
        self.settings_dialog = None

    def setup(self):
        icon_path = os.path.join(PLUGIN_DIR, "icon.png")
        if not os.path.exists(icon_path):
            print("[Tray] icon.png 未找到，跳过系统托盘")
            return

        icon = QIcon(icon_path)
        self.tray = QSystemTrayIcon(icon, self.app.app)
        self.tray.setToolTip("魔法猫咪")

        menu = QMenu()

        settings_action = QAction("设置", self.app.app)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)

        self.follow_action = QAction("停止跟随", self.app.app)
        self.follow_action.triggered.connect(self.toggle_follow)
        menu.addAction(self.follow_action)

        menu.addSeparator()

        quit_action = QAction("退出", self.app.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()
        print("[Tray] 系统托盘已启动")

    def show_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.settings_changed.connect(self.app.update_settings)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def toggle_follow(self):
        is_following = self.app.toggle_follow()
        if is_following:
            self.follow_action.setText("停止跟随")
        else:
            self.follow_action.setText("开始跟随")

    def quit_app(self):
        print("[Tray] 退出软件")
        if self.tray:
            self.tray.hide()
        self.app.app.quit()
