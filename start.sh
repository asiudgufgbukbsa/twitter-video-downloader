#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Twitter/X Video Downloader"
echo "  Twitter/X 视频下载器"
echo "========================================"
echo ""

# 尝试多种方式查找 Python
echo "[检查 Python...]"
PYTHON_EXE=""

# 方法1: python3
if command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
# 方法2: python
elif command -v python &> /dev/null; then
    PYTHON_EXE="python"
# 方法3: 检查常见路径
elif [ -f "/usr/bin/python3" ]; then
    PYTHON_EXE="/usr/bin/python3"
elif [ -f "/usr/local/bin/python3" ]; then
    PYTHON_EXE="/usr/local/bin/python3"
fi

# 未找到 Python
if [ -z "$PYTHON_EXE" ]; then
    echo ""
    echo "========================================"
    echo "[错误] 未找到 Python！"
    echo "========================================"
    echo ""
    echo "请先安装 Python 3.8 或更高版本"
    echo ""
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "macOS:         brew install python3"
    echo ""
    exit 1
fi

# 显示 Python 版本
PYTHON_VERSION=$($PYTHON_EXE --version 2>&1 | awk '{print $2}')
echo "找到 Python: $PYTHON_VERSION"
echo "路径: $(command -v $PYTHON_EXE)"
echo ""

# 检查是否需要安装依赖
echo "[检查依赖...]"
$PYTHON_EXE -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "未安装依赖，正在自动安装..."
    echo ""

    # 安装依赖
    $PYTHON_EXE -m pip install --upgrade pip > /dev/null 2>&1
    $PYTHON_EXE -m pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo ""
        echo "========================================"
        echo "[错误] 依赖安装失败！"
        echo "========================================"
        echo ""
        echo "请尝试手动运行以下命令："
        echo "  $PYTHON_EXE -m pip install -r requirements.txt"
        echo ""
        exit 1
    fi

    # 安装 Playwright 浏览器（可选）
    echo ""
    echo "[安装浏览器组件...]"
    $PYTHON_EXE -m playwright install chromium 2>/dev/null
    echo ""
    echo "依赖安装完成！"
    echo ""
fi

# 启动 GUI
echo "[启动程序...]"
echo ""
$PYTHON_EXE "$SCRIPT_DIR/twitter_downloader_gui.py"

# 如果 GUI 启动失败，显示错误
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "[错误] 程序启动失败！"
    echo "========================================"
    echo ""
    echo "可能的原因："
    echo "  1. 依赖未正确安装"
    echo "  2. Python 版本过低（需要 3.8+）"
    echo "  3. 脚本文件缺失"
    echo ""
fi
