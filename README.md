# 🐱 魔法猫咪 - Nuke 智能指导助手

一款可爱的桌面宠物猫咪，为 Nuke 合成师提供智能指导和快捷操作。

## ✨ 功能特性

- 🐱 **桌面宠物** - 可爱的猫咪精灵跟随鼠标移动
- 🤖 **AI 智能指导** - 基于 AI 的 Nuke 操作指导
- 📸 **截图工具** - 快速截取屏幕内容进行分析
- 💬 **对话气泡** - 猫咪会用对话框与你交流
- 🔧 **系统托盘** - 最小化到托盘，随时待命

## 📦 安装

### 环境要求
- Python 3.8+
- Windows 10/11

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/QAQooc/magic_Cat.git
cd magic_Cat

# 安装依赖
pip install -r requirements.txt
```

## 🚀 使用方法

### 方式一：双击启动
直接双击 `启动.bat` 即可运行

### 方式二：命令行启动
```bash
python main.py
```

### 方式三：一键配置
双击 `一键配置.bat` 自动安装依赖并启动

## ⌨️ 快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl + Shift + H` | 切换跟随模式 | 猫咪默认跟随鼠标移动，按下此快捷键可暂停/恢复跟随 |

> 💡 **提示**：暂停跟随后，猫咪会停在原地不动，再次按下快捷键可恢复跟随。

## 📁 项目结构

```
magic_Cat/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── api_config.py        # API 配置
├── sprite.py            # 猫咪精灵动画
├── cat_control.py       # 猫咪控制
├── speech_bubble.py     # 对话气泡
├── tray_menu.py         # 系统托盘菜单
├── ai_guide.py          # AI 指导核心
├── ai_guide_main.py     # AI 指导入口
├── guide_server.py      # 指导服务
├── guide_input.py       # 输入处理
├── nuke_listener.py     # Nuke 监听器
├── screenshot.py        # 截图工具
├── screenshot_grid.py   # 网格截图
├── hotkey_listener.py   # 热键监听
├── logger.py            # 日志工具
├── requirements.txt     # 依赖列表
├── 启动.bat             # 启动脚本
├── 停止.bat             # 停止脚本
├── 一键配置.bat          # 一键配置
├── 诊断工具.py          # 诊断工具
├── UI.png               # UI 界面图
├── icon.png             # 应用图标
├── cat_sprite_sheet.png # 猫咪精灵图
└── nuke_dialogs.txt     # Nuke 对话数据
```

## ⚙️ 配置说明

运行前可修改 `config.py` 中的参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `SPRITE_PATH` | 精灵图路径 | `cat_sprite_sheet.png` |
| `CAT_SIZE` | 猫咪大小 | `(120, 120)` |
| `MOUSE_LERP` | 跟随灵敏度 | `0.08` |
| `AI_OFFSET_X/Y` | AI 窗口偏移 | `200, 50` |

## 📝 更新日志

### v1.0.0 (2026-07-01)
- 🎉 初始发布
- 🐱 桌面宠物猫咪
- 🤖 AI 智能指导
- 📸 截图分析功能
- ⌨️ 快捷键切换跟随模式

## 👤 作者

**QAQooc** - [GitHub](https://github.com/QAQooc)

## 📄 许可证

MIT License
