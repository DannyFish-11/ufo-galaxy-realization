# UFO Galaxy - Windows PowerShell 启动脚本
# ==========================================
# 功能：
# 1. 设置 UTF-8 编码支持
# 2. 验证 Python 环境
# 3. 检查和修复配置
# 4. 启动 UFO Galaxy 系统
#
# 使用方法：
#   .\start_windows.ps1              # 默认启动
#   .\start_windows.ps1 -Mode validate # 仅验证配置
#   .\start_windows.ps1 -Mode fix     # 自动修复配置
#
# 注意：首次运行可能需要执行以下命令以允许脚本执行：
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#
# 作者：UFO Galaxy 修复系统
# 日期：2026-02-11

param(
    [string]$Mode = "start"
)

# 设置编码
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = 1

# 打印横幅
Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║     ██╗   ██╗███████╗ ██████╗      ██████╗  █████╗ ██╗      ║" -ForegroundColor Cyan
Write-Host "║     ██║   ██║██╔════╝██╔═══██╗    ██╔════╝ ██╔══██╗██║      ║" -ForegroundColor Cyan
Write-Host "║     ██║   ██║█████╗  ██║   ██║    ██║  ███╗███████║██║      ║" -ForegroundColor Cyan
Write-Host "║     ██║   ██║██╔══╝  ██║   ██║    ██║   ██║██╔══██║██║      ║" -ForegroundColor Cyan
Write-Host "║     ╚██████╔╝██║     ╚██████╔╝    ╚██████╔╝██║  ██║███████╗ ║" -ForegroundColor Cyan
Write-Host "║      ╚═════╝ ╚═╝      ╚═════╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║              L4 级自主性智能系统 v1.0 (修复版)                 ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[*] 检查 Python 环境..." -ForegroundColor Yellow
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonPath) {
    Write-Host "[!] 错误：未找到 Python" -ForegroundColor Red
    Write-Host "[!] 请先安装 Python 3.8+ 并将其添加到 PATH" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}

$pythonVersion = & python --version 2>&1
Write-Host "[+] 找到 Python：$pythonVersion" -ForegroundColor Green
Write-Host ""

# 根据模式执行
switch ($Mode) {
    "validate" {
        Write-Host "[*] 运行配置验证..." -ForegroundColor Yellow
        & python main_fixed.py --validate
        Read-Host "按 Enter 键退出"
        exit 0
    }
    
    "fix" {
        Write-Host "[*] 运行自动修复..." -ForegroundColor Yellow
        & python auto_fix.py
        Write-Host ""
        Write-Host "[*] 再次验证配置..." -ForegroundColor Yellow
        & python config_validator.py
        Read-Host "按 Enter 键退出"
        exit 0
    }
    
    "status" {
        Write-Host "[*] 查看系统状态..." -ForegroundColor Yellow
        & python main_fixed.py --status
        Read-Host "按 Enter 键退出"
        exit 0
    }
    
    default {
        # 默认启动模式
        Write-Host "[*] 第一步：验证配置..." -ForegroundColor Yellow
        $validateResult = & python config_validator.py 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] 配置验证失败" -ForegroundColor Red
            Write-Host "[*] 尝试自动修复..." -ForegroundColor Yellow
            & python auto_fix.py
            Write-Host ""
        }
        
        Write-Host "[*] 第二步：启动 UFO Galaxy 系统..." -ForegroundColor Yellow
        Write-Host ""
        & python main_fixed.py
        
        Read-Host "按 Enter 键退出"
    }
}
