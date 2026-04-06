#!/bin/bash

echo "========================================"
echo "  Twitter/X Video Downloader Installer"
echo "  Twitter/X 视频下载器 安装程序"
echo "========================================"
echo ""

# Check Python / 检查 Python
echo "[1/4] Checking Python... / 正在检查 Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo ""
        echo "[ERROR] Python is not installed"
        echo "[错误] Python 未安装"
        echo ""
        echo "Please install Python 3.8+ from https://www.python.org/downloads/"
        echo "请从 https://www.python.org/downloads/ 安装 Python 3.8+"
        echo ""
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python version / Python 版本: $PYTHON_VERSION"
echo ""

# Install dependencies / 安装依赖
echo "[2/4] Installing dependencies... / 正在安装依赖..."
$PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Failed to install dependencies"
    echo "[错误] 安装依赖失败"
    echo ""
    exit 1
fi
echo ""

# Install Playwright browsers / 安装 Playwright 浏览器
echo "[3/4] Installing Playwright browsers... / 正在安装 Playwright 浏览器..."
$PYTHON_CMD -m playwright install chromium
if [ $? -ne 0 ]; then
    echo ""
    echo "[WARNING] Failed to install Playwright browsers"
    echo "[警告] 安装 Playwright 浏览器失败"
    echo "The video downloader will still work, but bookmark downloader may not."
    echo "视频下载器仍可使用，但书签下载器可能无法工作。"
    echo ""
fi
echo ""

# Make run script executable / 使运行脚本可执行
echo "[4/4] Making scripts executable... / 设置脚本可执行权限..."
chmod +x run_gui.sh 2>/dev/null
echo ""

echo "========================================"
echo "  Installation completed successfully!"
echo "  安装成功完成！"
echo "========================================"
echo ""
echo "How to use / 使用方法:"
echo ""
echo "  1. Run ./run_gui.sh to start the graphical interface"
echo "     运行 ./run_gui.sh 启动图形界面"
echo ""
echo "  2. Or use command line:"
echo "     或使用命令行:"
echo "     python3 twitter_video_downloader.py 'https://x.com/...'"
echo "     python3 twitter_bookmark_downloader.py"
echo ""
echo "========================================"
