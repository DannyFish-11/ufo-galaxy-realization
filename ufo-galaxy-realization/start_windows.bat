@echo off
REM UFO Galaxy - Windows 启动脚本
REM ================================
REM 功能：
REM 1. 设置 UTF-8 编码支持
REM 2. 验证 Python 环境
REM 3. 检查和修复配置
REM 4. 启动 UFO Galaxy 系统
REM
REM 使用方法：
REM   start_windows.bat              # 默认启动
REM   start_windows.bat validate     # 仅验证配置
REM   start_windows.bat fix          # 自动修复配置
REM
REM 作者：UFO Galaxy 修复系统
REM 日期：2026-02-11

setlocal enabledelayedexpansion

REM 设置 UTF-8 编码
chcp 65001 > nul
set PYTHONUTF8=1

REM 打印横幅
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║     ██╗   ██╗███████╗ ██████╗      ██████╗  █████╗ ██╗      ║
echo ║     ██║   ██║██╔════╝██╔═══██╗    ██╔════╝ ██╔══██╗██║      ║
echo ║     ██║   ██║█████╗  ██║   ██║    ██║  ███╗███████║██║      ║
echo ║     ██║   ██║██╔══╝  ██║   ██║    ██║   ██║██╔══██║██║      ║
echo ║     ╚██████╔╝██║     ╚██████╔╝    ╚██████╔╝██║  ██║███████╗ ║
echo ║      ╚═════╝ ╚═╝      ╚═════╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ║
echo ║                                                                ║
echo ║              L4 级自主性智能系统 v1.0 (修复版)                 ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
echo [*] 检查 Python 环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo [!] 错误：未找到 Python
    echo [!] 请先安装 Python 3.8+ 并将其添加到 PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [+] 找到 Python：%PYTHON_VERSION%
echo.

REM 获取命令行参数
set MODE=start
if not "%1"=="" set MODE=%1

REM 根据模式执行
if "%MODE%"=="validate" (
    echo [*] 运行配置验证...
    python main_fixed.py --validate
    pause
    exit /b 0
)

if "%MODE%"=="fix" (
    echo [*] 运行自动修复...
    python auto_fix.py
    echo.
    echo [*] 再次验证配置...
    python config_validator.py
    pause
    exit /b 0
)

if "%MODE%"=="status" (
    echo [*] 查看系统状态...
    python main_fixed.py --status
    pause
    exit /b 0
)

REM 默认启动模式
echo [*] 第一步：验证配置...
python config_validator.py > nul 2>&1
if errorlevel 1 (
    echo [!] 配置验证失败
    echo [*] 尝试自动修复...
    python auto_fix.py
    echo.
)

echo [*] 第二步：启动 UFO Galaxy 系统...
echo.
python main_fixed.py

REM 保持窗口打开
pause
