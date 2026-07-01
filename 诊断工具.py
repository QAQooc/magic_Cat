# -*- coding: utf-8 -*-
"""
魔法猫咪 - 诊断与环境修复脚本
检查依赖、文件完整性，自动修复环境
"""
import os
import sys
import subprocess
import importlib

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== 必需的Python包 =====
REQUIRED_PACKAGES = {
    "PyQt5": "PyQt5",
    "websockets": "websockets",
    "requests": "requests",
    "keyboard": "keyboard",
    "PIL": "Pillow",
}

# ===== 必需的文件 =====
REQUIRED_FILES = {
    # Python模块
    "main.py": "主程序",
    "sprite.py": "猫咪精灵类",
    "speech_bubble.py": "对话气泡类",
    "config.py": "应用配置",
    "api_config.py": "AI API配置",
    "guide_input.py": "输入框界面",
    "guide_server.py": "引导WebSocket服务器",
    "ai_guide.py": "AI对话模块",
    "ai_guide_main.py": "AI引导主流程",
    "screenshot.py": "截图模块",
    "hotkey_listener.py": "快捷键监听",
    "tray_menu.py": "系统托盘菜单",
    "nuke_listener.py": "Nuke通信监听",
    # 资源文件
    "cat_sprite_sheet.png": "猫咪精灵图",
    "icon.png": "应用图标",
    "UI.png": "输入框背景图",
    "nuke_dialogs.txt": "Nuke台词文件",
    # 配置文件
    "requirements.txt": "依赖列表",
    "启动.bat": "启动脚本",
    "停止.bat": "停止脚本",
}

# ===== 必需的目录 =====
REQUIRED_DIRS = [
    "backup",
    "versions",
    "docs",
]


def check_python_version():
    """检查Python版本"""
    print("\n[1/5] 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False


def check_packages():
    """检查Python包"""
    print("\n[2/5] 检查Python包...")
    missing = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (未安装)")
            missing.append(package_name)
    return missing


def install_packages(packages):
    """安装缺失的包"""
    if not packages:
        return
    print("\n[*] 安装缺失的包...")
    for package in packages:
        print(f"  安装 {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  ✓ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"  ✗ {package} 安装失败，请手动安装: pip install {package}")


def check_files():
    """检查必需文件"""
    print("\n[3/5] 检查文件完整性...")
    missing = []
    for filename, desc in REQUIRED_FILES.items():
        filepath = os.path.join(PLUGIN_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} - {desc} (缺失)")
            missing.append((filename, desc))
    return missing


def check_dirs():
    """检查目录结构"""
    print("\n[4/5] 检查目录结构...")
    for dirname in REQUIRED_DIRS:
        dirpath = os.path.join(PLUGIN_DIR, dirname)
        if os.path.exists(dirpath):
            count = len(os.listdir(dirpath))
            print(f"  ✓ {dirname}/ ({count} 个文件)")
        else:
            print(f"  ✗ {dirname}/ (缺失，已创建)")
            os.makedirs(dirpath, exist_ok=True)


def check_config():
    """检查配置文件"""
    print("\n[5/5] 检查配置文件...")
    config_path = os.path.join(PLUGIN_DIR, "config.py")
    api_config_path = os.path.join(PLUGIN_DIR, "api_config.py")

    # 检查config.py
    try:
        spec = importlib.util.spec_from_file_location("config", config_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        required_params = [
            "CAT_SIZE", "FRAME_SIZE", "MOUSE_OFFSET_X", "MOUSE_OFFSET_Y",
            "MOUSE_LERP", "MOUSE_SPEED_THRESHOLD", "RUN_SPEED_THRESHOLD",
            "IDLE_TIMEOUT", "BUBBLE_MAX_WIDTH", "BUBBLE_FONT_SIZE",
            "WIDGET_EXTRA_W", "WIDGET_EXTRA_H", "AI_OFFSET_X", "AI_OFFSET_Y"
        ]
        for param in required_params:
            if hasattr(mod, param):
                print(f"  ✓ config.{param} = {getattr(mod, param)}")
            else:
                print(f"  ✗ config.{param} (缺失)")
    except Exception as e:
        print(f"  ✗ config.py 解析失败: {e}")

    # 检查api_config.py
    try:
        spec = importlib.util.spec_from_file_location("api_config", api_config_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "MODELS"):
            models = mod.MODELS
            print(f"  ✓ api_config.MODELS ({len(models)} 个模型)")
            for name, config in models.items():
                print(f"    - {name}: {config.get('model_name', '?')}")
        if hasattr(mod, "DEFAULT_MODEL"):
            print(f"  ✓ api_config.DEFAULT_MODEL = {mod.DEFAULT_MODEL}")
    except Exception as e:
        print(f"  ✗ api_config.py 解析失败: {e}")


def generate_report(python_ok, missing_packages, missing_files):
    """生成诊断报告"""
    print("\n" + "=" * 50)
    print("诊断报告")
    print("=" * 50)

    if python_ok and not missing_packages and not missing_files:
        print("\n✓ 环境检查全部通过！可以正常使用。")
        print("\n启动方式: python main.py 或 双击 启动.bat")
    else:
        print("\n⚠ 发现以下问题:")
        if not python_ok:
            print("  - Python版本过低，需要3.8+")
        if missing_packages:
            print(f"  - 缺失 {len(missing_packages)} 个Python包: {', '.join(missing_packages)}")
        if missing_files:
            print(f"  - 缺失 {len(missing_files)} 个文件:")
            for filename, desc in missing_files:
                print(f"    - {filename} ({desc})")
        print("\n请修复上述问题后重试。")

    print("\n" + "=" * 50)


def main():
    print("=" * 50)
    print("魔法猫咪 - 环境诊断工具")
    print("=" * 50)
    print(f"项目目录: {PLUGIN_DIR}")
    print(f"Python: {sys.executable}")

    # 1. 检查Python版本
    python_ok = check_python_version()

    # 2. 检查包
    missing_packages = check_packages()

    # 3. 检查文件
    missing_files = check_files()

    # 4. 检查目录
    check_dirs()

    # 5. 检查配置
    check_config()

    # 6. 自动修复
    if missing_packages:
        answer = input("\n是否自动安装缺失的包? (y/n): ").strip().lower()
        if answer == 'y':
            install_packages(missing_packages)
            # 重新检查
            missing_packages = check_packages()

    # 7. 生成报告
    generate_report(python_ok, missing_packages, missing_files)


if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
