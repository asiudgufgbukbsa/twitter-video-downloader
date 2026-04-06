#!/bin/bash

# Get the directory where this script is located / 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed / 检查 Python 是否安装
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed"
    echo "[错误] Python 未安装"
    echo ""
    echo "Please run install.sh first to install dependencies"
    echo "请先运行 install.sh 安装依赖"
    echo ""
    exit 1
fi

# Start the GUI / 启动 GUI
echo "Starting Twitter/X Video Downloader..."
echo "正在启动 Twitter/X 视频下载器..."
echo ""
$PYTHON_CMD "$SCRIPT_DIR/twitter_downloader_gui.py"
