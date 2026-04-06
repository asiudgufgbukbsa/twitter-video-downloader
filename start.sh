#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Twitter/X Video Downloader"
echo "  Twitter/X 视频下载器"
echo "========================================"
echo ""

# 检查 Python 是否安装
echo "[检查 Python...]"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo ""
    echo "========================================"
    echo "[错误] 未检测到 Python！"
    echo "========================================"
    echo ""
    echo "请先安装 Python 3.8 或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# 显示 Python 版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"
echo ""

# 检查是否需要安装依赖
echo "[检查依赖...]"
$PYTHON_CMD -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "未检测到依赖，正在自动安装..."
    echo ""

    # 安装依赖
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
    $PYTHON_CMD -m pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo ""
        echo "========================================"
        echo "[错误] 依赖安装失败！"
        echo "========================================"
        echo ""
        echo "请尝试手动运行以下命令："
        echo "  pip install -r requirements.txt"
        echo ""
        exit 1
    fi

    # 安装 Playwright 浏览器（可选）
    echo ""
    echo "[安装浏览器组件...]"
    $PYTHON_CMD -m playwright install chromium 2>/dev/null
    echo ""
    echo "依赖安装完成！"
    echo ""
fi

# 启动 GUI
echo "[启动图形界面...]"
echo ""
$PYTHON_CMD "$SCRIPT_DIR/twitter_downloader_gui.py"

# 如果 GUI 启动失败，显示错误
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "[错误] 程序启动失败！"
    echo "========================================"
    echo ""
    echo "可能的原因："
    echo "  1. 依赖未正确安装，请手动运行: pip install -r requirements.txt"
    echo "  2. Python 版本过低，需要 3.8 或更高版本"
    echo "  3. 脚本文件缺失或损坏"
    echo ""
fi
