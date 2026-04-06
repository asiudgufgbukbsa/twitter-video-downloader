@echo off
chcp 65001 >nul
title Twitter/X Video Downloader

:: Check if Python is installed / 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo [错误] Python 未安装
    echo.
    echo Please run install.bat first to install dependencies
    echo 请先运行 install.bat 安装依赖
    echo.
    pause
    exit /b 1
)

:: Start the GUI / 启动 GUI
echo Starting Twitter/X Video Downloader...
echo 正在启动 Twitter/X 视频下载器...
echo.
python "%~dp0twitter_downloader_gui.py"
