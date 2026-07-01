@echo off
chcp 65001 >nul
echo ========================================
echo   魔法猫咪 - 一键环境配置
echo ========================================
echo.

:: 检查Python
echo [1/3] 检查Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python已安装

:: 安装依赖
echo.
echo [2/3] 安装依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装失败，尝试使用官方源...
    pip install -r requirements.txt
)

:: 创建必要目录
echo.
echo [3/3] 创建目录结构...
if not exist "backup" mkdir backup
if not exist "versions" mkdir versions
if not exist "docs" mkdir docs
if not exist "screenshot" mkdir screenshot
echo [OK] 目录结构已创建

echo.
echo ========================================
echo   配置完成！
echo ========================================
echo.
echo 启动方式:
echo   1. 双击 "启动.bat"
echo   2. 或运行: python main.py
echo.
echo 设置API:
echo   右键系统托盘图标 → 设置 → API设置
echo.
pause
