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

:: 尝试多种方式查找 Python
echo [检查 Python...]
set "PYTHON_EXE="

:: 方法1: 直接调用 python
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :found_python
)

:: 方法2: 尝试 python3
python3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python3"
    goto :found_python
)

:: 方法3: 尝试 py 启动器
py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    goto :found_python
)

:: 方法4: 尝试 py -3
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py -3"
    goto :found_python
)

:: 方法5: 检查常见安装路径
if exist "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        set "PYTHON_EXE=%%i\python.exe"
        goto :found_python
    )
)

if exist "C:\Python3*\python.exe" (
    for /d %%i in ("C:\Python3*") do (
        set "PYTHON_EXE=%%i\python.exe"
        goto :found_python
    )
)

:: 未找到 Python
echo.
echo ========================================
echo [错误] 未找到 Python！
echo ========================================
echo.
echo 请先安装 Python 3.8 或更高版本
echo 下载地址: https://www.python.org/downloads/
echo.
echo 安装时请务必勾选以下选项：
echo   [√] Add Python to PATH
echo   [√] Add Python to environment variables
echo.
echo 如果已安装，请尝试：
echo   1. 重新安装 Python 并勾选 "Add Python to PATH"
echo   2. 或将 Python 添加到系统环境变量
echo   3. 重启电脑后再试
echo.
pause
exit /b 1

:found_python
:: 显示 Python 版本
for /f "tokens=2 delims= " %%v in ('%PYTHON_EXE% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo 找到 Python: %PYTHON_VERSION%
echo 路径: %PYTHON_EXE%
echo.

:: 检查是否需要安装依赖
echo [检查依赖...]
%PYTHON_EXE% -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 未安装依赖，正在自动安装...
    echo.

    :: 安装依赖
    %PYTHON_EXE% -m pip install --upgrade pip >nul 2>&1
    %PYTHON_EXE% -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo.
        echo ========================================
        echo [错误] 依赖安装失败！
        echo ========================================
        echo.
        echo 请尝试手动运行以下命令：
        echo   %PYTHON_EXE% -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )

    :: 安装 Playwright 浏览器（可选）
    echo.
    echo [安装浏览器组件...]
    %PYTHON_EXE% -m playwright install chromium 2>nul
    echo.
    echo 依赖安装完成！
    echo.
)

:: 启动 GUI
echo [启动程序...]
echo.
%PYTHON_EXE% "%SCRIPT_DIR%twitter_downloader_gui.py"

:: 如果 GUI 启动失败，显示错误
if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] 程序启动失败！
    echo ========================================
    echo.
    echo 可能的原因：
    echo   1. 依赖未正确安装
    echo   2. Python 版本过低（需要 3.8+）
    echo   3. 脚本文件缺失
    echo.
    pause
)
