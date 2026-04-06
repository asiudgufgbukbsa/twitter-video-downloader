@echo off
chcp 65001 >nul
title Twitter/X Video Downloader Installer

echo ========================================
echo   Twitter/X Video Downloader Installer
echo   Twitter/X 视频下载器 安装程序
echo ========================================
echo.

:: Check Python / 检查 Python
echo [1/4] Checking Python... / 正在检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo [错误] Python 未安装或未添加到环境变量
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo 请从 https://www.python.org/downloads/ 安装 Python 3.8+
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Python version / Python 版本: %PYTHON_VERSION%
echo.

:: Install dependencies / 安装依赖
echo [2/4] Installing dependencies... / 正在安装依赖...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo [错误] 安装依赖失败
    echo.
    pause
    exit /b 1
)
echo.

:: Install Playwright browsers / 安装 Playwright 浏览器
echo [3/4] Installing Playwright browsers... / 正在安装 Playwright 浏览器...
python -m playwright install chromium
if errorlevel 1 (
    echo.
    echo [WARNING] Failed to install Playwright browsers
    echo [警告] 安装 Playwright 浏览器失败
    echo The video downloader will still work, but bookmark downloader may not.
    echo 视频下载器仍可使用，但书签下载器可能无法工作。
    echo.
)
echo.

:: Create desktop shortcut (optional) / 创建桌面快捷方式（可选）
echo [4/4] Setup complete! / 设置完成！
echo.
echo ========================================
echo   Installation completed successfully!
echo   安装成功完成！
echo ========================================
echo.
echo How to use / 使用方法:
echo.
echo   1. Double-click run_gui.bat to start the graphical interface
echo      双击 run_gui.bat 启动图形界面
echo.
echo   2. Or use command line:
echo      或使用命令行:
echo      python twitter_video_downloader.py "https://x.com/..."
echo      python twitter_bookmark_downloader.py
echo.
echo ========================================
echo.
pause
