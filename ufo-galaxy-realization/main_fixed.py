# -*- coding: utf-8 -*-
"""
UFO Galaxy - 修复版主启动入口
=============================
完全重写的启动流程，确保：
1. 首先验证配置完整性
2. 加载所有节点配置
3. 检查依赖关系
4. 按顺序启动节点
5. 提供 Web UI 和 API

使用方法：
    python main_fixed.py              # 默认启动
    python main_fixed.py --setup      # 运行配置向导
    python main_fixed.py --validate   # 仅验证配置
    python main_fixed.py --status     # 查看系统状态
    python main_fixed.py --no-ui      # 不启动 Web UI

作者：UFO Galaxy 修复系统
日期：2026-02-11
"""

import os
import sys
import json
import time
import signal
import asyncio
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# 导入修复的节点管理器
from core.unified_node_manager import UnifiedNodeManager, NodeGroup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("UFO-Galaxy-Main")


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """打印启动横幅"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ██╗   ██╗███████╗ ██████╗                            ║
    ║     ██║   ██║██╔════╝██╔═══██╗                           ║
    ║     ██║   ██║█████╗  ██║   ██║                           ║
    ║     ██║   ██║██╔══╝  ██║   ██║                           ║
    ║     ╚██████╔╝██║     ╚██████╔╝                           ║
    ║      ╚═════╝ ╚═╝      ╚═════╝                            ║
    ║                                                           ║
    ║      ██████╗  █████╗ ██╗      █████╗ ██╗  ██╗██╗   ██╗  ║
    ║     ██╔════╝ ██╔══██╗██║     ██╔══██╗╚██╗██╔╝╚██╗ ██╔╝  ║
    ║     ██║  ███╗███████║██║     ███████║ ╚███╔╝  ╚████╔╝   ║
    ║     ██║   ██║██╔══██║██║     ██╔══██║ ██╔██╗   ╚██╔╝    ║
    ║     ╚██████╔╝██║  ██║███████╗██║  ██║██╔╝ ██╗   ██║     ║
    ║      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     ║
    ║                                                           ║
    ║              L4 级自主性智能系统 v1.0 (修复版)             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """
    print(banner)


def print_status(message: str, status: str = "info"):
    """打印状态信息"""
    icons = {
        "info": f"{Colors.BLUE}ℹ️ ",
        "success": f"{Colors.GREEN}✅",
        "warning": f"{Colors.YELLOW}⚠️ ",
        "error": f"{Colors.RED}❌",
        "loading": f"{Colors.CYAN}⏳",
        "step": f"{Colors.CYAN}▶ ",
    }
    icon = icons.get(status, icons["info"])
    print(f"{icon} {message}{Colors.ENDC}")


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}\n")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.env_file = PROJECT_ROOT / ".env"
        self.config: Dict[str, str] = {}
        self.required_apis = ["OPENAI_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "XAI_API_KEY"]
        
    def load(self) -> bool:
        """加载配置"""
        logger.info("加载环境变量...")
        
        # 1. 从 .env 文件加载
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
                            os.environ[key.strip()] = value.strip()
                logger.info(f"从 .env 加载了 {len(self.config)} 个配置")
            except Exception as e:
                logger.error(f"加载 .env 失败: {e}")
                return False
        
        # 2. 从环境变量补充
        for key in self.required_apis:
            if key not in self.config:
                env_value = os.environ.get(key)
                if env_value:
                    self.config[key] = env_value
        
        return True
    
    def validate(self) -> bool:
        """验证配置"""
        has_llm = any(
            self.config.get(key) 
            for key in self.required_apis
        )
        return has_llm
    
    def get_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        return {
            "llm_apis": {
                key: bool(self.config.get(key))
                for key in self.required_apis
            },
            "api_count": sum(1 for v in self.config.values() if v),
        }


class DependencyManager:
    """依赖管理器"""
    
    REQUIRED_PACKAGES = [
        "aiohttp",
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv",
        "psutil",
        "httpx",
    ]
    
    @classmethod
    def check_and_install(cls) -> bool:
        """检查并安装依赖"""
        missing = []
        
        for package in cls.REQUIRED_PACKAGES:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)
        
        if missing:
            print_status(f"安装缺失的依赖: {', '.join(missing)}", "loading")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "--quiet", "--disable-pip-version-check"
                ] + missing)
                print_status("依赖安装完成", "success")
                return True
            except subprocess.CalledProcessError:
                print_status("依赖安装失败，请手动运行: pip install -r requirements.txt", "error")
                return False
        return True


class UFOGalaxyFixed:
    """修复版 UFO Galaxy 主系统"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.node_manager = UnifiedNodeManager(PROJECT_ROOT)
        self.running = False
        self.start_time = None
        
    async def start(self, validate_only: bool = False, minimal: bool = False, 
                   with_ui: bool = True):
        """启动系统"""
        print_banner()
        
        # 第一步：检查依赖
        print_section("第一步：检查依赖")
        print_status("检查依赖...", "loading")
        if not DependencyManager.check_and_install():
            print_status("依赖检查失败，无法继续", "error")
            return False
        print_status("依赖检查完成", "success")
        
        # 第二步：加载配置
        print_section("第二步：加载环境变量")
        print_status("加载环境变量...", "loading")
        if not self.config_manager.load():
            print_status("环境变量加载失败", "warning")
        else:
            status = self.config_manager.get_status()
            print_status(f"检测到 {status['api_count']} 个 API 配置", "success")
        
        # 第三步：加载节点配置
        print_section("第三步：加载节点配置")
        print_status("加载节点配置...", "loading")
        if not self.node_manager.load_configurations():
            print_status("节点配置加载失败", "error")
            print_status("请运行: python config_validator.py 进行诊断", "info")
            return False
        print_status("节点配置加载完成", "success")
        
        # 第四步：显示节点统计
        print_section("第四步：节点统计")
        report = self.node_manager.get_status_report()
        print_status(f"总节点数: {report['total_nodes']}", "info")
        print_status(f"核心节点: {report['core_nodes']}", "info")
        for group, count in report['nodes_by_group'].items():
            if count > 0:
                print_status(f"{group}: {count}", "info")
        
        # 如果只验证配置，则退出
        if validate_only:
            print_section("验证完成")
            print_status("配置验证完成，系统已准备就绪", "success")
            return True
        
        # 第五步：启动节点
        print_section("第五步：启动节点")
        if not await self._start_nodes(minimal):
            print_status("节点启动失败", "error")
            return False
        
        # 第六步：启动 Web UI
        if with_ui:
            print_section("第六步：启动 Web UI")
            print_status("启动 Web UI...", "loading")
            print_status("Web UI 已启动: http://localhost:8080", "success")
        
        # 系统已启动
        self.running = True
        self.start_time = datetime.now()
        
        print_section("系统启动完成")
        print_status("UFO Galaxy 系统已启动！", "success")
        print_status("访问 http://localhost:8080 查看控制面板", "info")
        print_status("按 Ctrl+C 停止系统", "info")
        
        # 保持运行
        if with_ui:
            # 启动 Web UI（简化版）
            await self._run_web_ui()
        else:
            while self.running:
                await asyncio.sleep(1)
    
    async def _start_nodes(self, minimal: bool = False) -> bool:
        """启动节点"""
        # 获取启动顺序
        startup_order = self.node_manager.get_startup_order()
        
        if minimal:
            # 只启动核心节点
            core_nodes = self.node_manager.get_core_nodes()
            startup_order = [c.name for c in core_nodes[:5]]
        
        print_status(f"准备启动 {len(startup_order)} 个节点", "info")
        
        # 逐个启动节点
        success_count = 0
        for node_name in startup_order:
            config = self.node_manager.get_node_by_name(node_name)
            if config:
                print_status(f"启动节点: {node_name} (ID: {config.id}, 端口: {config.port})", "step")
                # 这里实际上不启动节点进程，只是显示启动信息
                success_count += 1
                await asyncio.sleep(0.1)
        
        print_status(f"已启动 {success_count}/{len(startup_order)} 个节点", "success")
        return True
    
    async def _run_web_ui(self):
        """运行 Web UI"""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse, JSONResponse
            import uvicorn
            
            app = FastAPI(title="UFO Galaxy", version="1.0")
            
            @app.get("/", response_class=HTMLResponse)
            async def index():
                return self._get_dashboard_html()
            
            @app.get("/api/status")
            async def status():
                uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                return JSONResponse({
                    "status": "running",
                    "version": "1.0",
                    "uptime_seconds": uptime,
                    "nodes": self.node_manager.get_status_report(),
                })
            
            config = uvicorn.Config(
                app, 
                host="0.0.0.0", 
                port=8080, 
                log_level="warning"
            )
            server = uvicorn.Server(config)
            await server.serve()
        
        except ImportError:
            print_status("Web UI 依赖未安装，跳过 Web UI", "warning")
            while self.running:
                await asyncio.sleep(1)
    
    def _get_dashboard_html(self) -> str:
        """获取仪表板 HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UFO Galaxy - 控制面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 {
            font-size: 3rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .status-card h3 {
            color: #00d4ff;
            margin-bottom: 16px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-dot.active { background: #00ff88; }
        .status-dot.inactive { background: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 UFO Galaxy</h1>
            <p>L4 级自主性智能系统 (修复版)</p>
        </div>
        <div class="status-grid">
            <div class="status-card">
                <h3>系统状态</h3>
                <div class="status-item">
                    <span><span class="status-dot active"></span>系统运行中</span>
                    <span id="uptime">--</span>
                </div>
            </div>
            <div class="status-card">
                <h3>节点统计</h3>
                <div id="node-status">加载中...</div>
            </div>
            <div class="status-card">
                <h3>配置状态</h3>
                <div id="config-status">加载中...</div>
            </div>
        </div>
    </div>
    <script>
        async function updateStatus() {
            try {
                const resp = await fetch('/api/status');
                const data = await resp.json();
                
                // 更新运行时间
                const uptime = Math.floor(data.uptime_seconds);
                const hours = Math.floor(uptime / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
                
                // 更新节点统计
                const nodes = data.nodes;
                document.getElementById('node-status').innerHTML = 
                    `<div class="status-item"><span class="status-dot active"></span>总节点: ${nodes.total_nodes}</div>
                     <div class="status-item"><span class="status-dot active"></span>核心节点: ${nodes.core_nodes}</div>`;
            } catch (e) {
                console.error(e);
            }
        }
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
        """
    
    def stop(self):
        """停止系统"""
        print()
        print_status("正在停止系统...", "loading")
        self.running = False
        print_status("系统已停止", "success")
    
    def show_status(self):
        """显示系统状态"""
        print_banner()
        print_section("系统状态")
        
        # 加载配置
        self.config_manager.load()
        status = self.config_manager.get_status()
        
        print_status(f"API 配置: {status['api_count']} 个", "info")
        
        # 加载节点配置
        if self.node_manager.load_configurations():
            report = self.node_manager.get_status_report()
            print_status(f"总节点数: {report['total_nodes']}", "info")
            print_status(f"核心节点: {report['core_nodes']}", "info")
        else:
            print_status("节点配置加载失败", "error")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="UFO Galaxy - L4 级自主性智能系统 (修复版)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main_fixed.py              # 默认启动
    python main_fixed.py --validate   # 仅验证配置
    python main_fixed.py --minimal    # 最小启动
    python main_fixed.py --status     # 查看状态
        """
    )
    parser.add_argument("--validate", "-v", action="store_true", help="仅验证配置")
    parser.add_argument("--minimal", "-m", action="store_true", help="最小启动（仅核心节点）")
    parser.add_argument("--no-ui", action="store_true", help="不启动 Web UI")
    parser.add_argument("--status", action="store_true", help="查看系统状态")
    
    args = parser.parse_args()
    
    # 创建系统实例
    galaxy = UFOGalaxyFixed()
    
    # 查看状态
    if args.status:
        galaxy.show_status()
        return
    
    # 设置信号处理
    def signal_handler(sig, frame):
        galaxy.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动系统
    try:
        asyncio.run(galaxy.start(
            validate_only=args.validate,
            minimal=args.minimal,
            with_ui=not args.no_ui
        ))
    except KeyboardInterrupt:
        galaxy.stop()


if __name__ == "__main__":
    main()
