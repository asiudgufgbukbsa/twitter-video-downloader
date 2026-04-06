@echo off
chcp 65001 >nul
title Twitter/X Video Downloader / Twitter/X 视频下载器

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo   Twitter/X Video Downloader
echo   Twitter/X 视频下载器
echo ========================================
echo.

:: 检查 Python 是否安装
echo [检查 Python...]
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] 未检测到 Python！
    echo ========================================
    echo.
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH" 选项！
    echo.
    pause
    exit /b 1
)

:: 显示 Python 版本
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Python 版本: %PYTHON_VERSION%
echo.

:: 检查是否需要安装依赖
echo [检查依赖...]
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 未检测到依赖，正在自动安装...
    echo.

    :: 安装依赖
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo.
        echo ========================================
        echo [错误] 依赖安装失败！
        echo ========================================
        echo.
        echo 请尝试手动运行以下命令：
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )

    :: 安装 Playwright 浏览器（可选）
    echo.
    echo [安装浏览器组件...]
    python -m playwright install chromium 2>nul
    echo.
    echo 依赖安装完成！
    echo.
)

:: 启动 GUI
echo [启动图形界面...]
echo.
python "%SCRIPT_DIR%twitter_downloader_gui.py"

:: 如果 GUI 启动失败，显示错误
if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] 程序启动失败！
    echo ========================================
    echo.
    echo 可能的原因：
    echo   1. 依赖未正确安装，请手动运行: pip install -r requirements.txt
    echo   2. Python 版本过低，需要 3.8 或更高版本
    echo   3. 脚本文件缺失或损坏
    echo.
    pause
)
