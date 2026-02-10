#!/usr/bin/env python3
"""
UFO Galaxy 系统完整性审计工具
检查系统配置、依赖、节点和启动文件
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Tuple

class SystemAuditor:
    """系统审计器"""
    
    def __init__(self, project_root='.'):
        self.root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def check_file_exists(self, path, desc):
        """检查文件是否存在"""
        full_path = self.root / path
        if full_path.exists():
            self.successes.append(f"✅ {desc}: {path}")
            return True
        else:
            self.issues.append(f"❌ {desc}: {path} 不存在")
            return False
    
    def check_json_format(self, path, desc):
        """检查JSON文件格式"""
        full_path = self.root / path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if desc == "节点依赖配置":
                if isinstance(data, dict) and 'nodes' in data:
                    node_count = len(data['nodes'])
                    self.successes.append(f"✅ {desc}: {path} ({node_count} 个节点)")
                    return True
                else:
                    self.issues.append(f"❌ {desc}: {path} 格式不正确")
                    return False
            else:
                self.successes.append(f"✅ {desc}: {path}")
                return True
                
        except json.JSONDecodeError as e:
            self.issues.append(f"❌ {desc}: {path} JSON格式错误 - {e}")
            return False
        except Exception as e:
            self.issues.append(f"❌ {desc}: {path} 读取失败 - {e}")
            return False
    
    def check_directory_structure(self, path, desc):
        """检查目录结构"""
        full_path = self.root / path
        if full_path.exists() and full_path.is_dir():
            # 统计节点数量
            node_dirs = [d for d in full_path.iterdir() if d.is_dir() and d.name.startswith('Node_')]
            self.successes.append(f"✅ {desc}: {path} ({len(node_dirs)} 个节点目录)")
            return len(node_dirs)
        else:
            self.issues.append(f"❌ {desc}: {path} 不存在")
            return 0
    
    def check_python_deps(self):
        """检查Python依赖"""
        required_packages = [
            'fastapi',
            'uvicorn',
            'websockets',
            'python-dotenv',
            'pydantic',
            'aiohttp',
            'asyncssh',
        ]
        
        missing_packages = []
        for package in required_packages:
            spec = importlib.util.find_spec(package.replace('-', '_'))
            if spec is None:
                missing_packages.append(package)
                self.warnings.append(f"⚠️  缺少依赖: {package}")
            else:
                self.successes.append(f"✅ 依赖: {package}")
        
        return len(missing_packages) == 0
    
    def check_node_modules(self):
        """检查节点模块"""
        nodes_dir = self.root / 'nodes'
        if not nodes_dir.exists():
            return
        
        # 检查核心节点
        core_nodes = [
            'Node_00_StateMachine',
            'Node_01_OneAPI', 
            'Node_02_Tasker',
            'Node_03_SecretVault',
            'Node_04_Router'
        ]
        
        for node in core_nodes:
            node_dir = nodes_dir / node
            main_py = node_dir / 'main.py'
            
            if main_py.exists():
                self.successes.append(f"✅ 核心节点: {node}")
            else:
                self.warnings.append(f"⚠️  核心节点不完整: {node}")
    
    def check_startup_consistency(self):
        """检查启动文件一致性"""
        main_py = self.root / 'main.py'
        unified_launcher = self.root / 'unified_launcher.py'
        
        if not main_py.exists():
            self.issues.append("❌ 主启动文件 main.py 不存在")
            return False
        
        if not unified_launcher.exists():
            self.issues.append("❌ 统一启动器 unified_launcher.py 不存在")
            return False
        
        # 检查 main.py 是否导入了 unified_launcher
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            if 'unified_launcher' in main_content or 'UFOGalaxyUnified' in main_content:
                self.successes.append("✅ main.py 使用统一启动器")
                return True
            else:
                self.warnings.append("⚠️  main.py 可能没有使用统一启动器")
                return False
        except Exception as e:
            self.issues.append(f"❌ 无法读取 main.py: {e}")
            return False
    
    def run_full_audit(self):
        """运行完整审计"""
        print("=" * 70)
        print("UFO Galaxy 系统完整性审计")
        print("=" * 70)
        
        # 检查关键文件
        print("\n📁 文件系统检查:")
        self.check_file_exists('.env', '环境配置文件')
        self.check_file_exists('.env.example', '环境配置示例')
        self.check_file_exists('requirements.txt', '依赖文件')
        
        # 检查配置文件
        print("\n⚙️  配置检查:")
        self.check_json_format('node_dependencies.json', '节点依赖配置')
        self.check_json_format('config/node_registry.json', '节点注册表')
        self.check_json_format('config/unified_config.json', '统一配置')
        
        # 检查目录结构
        print("\n📂 目录结构检查:")
        node_count = self.check_directory_structure('nodes', '节点目录')
        
        # 检查启动文件
        print("\n🚀 启动文件检查:")
        self.check_file_exists('main.py', '主启动文件')
        self.check_file_exists('unified_launcher.py', '统一启动器')
        self.check_startup_consistency()
        
        # 检查依赖
        print("\n📦 Python依赖检查:")
        self.check_python_deps()
        
        # 检查节点模块
        if node_count > 0:
            print("\n🔧 核心节点检查:")
            self.check_node_modules()
        
        # 打印结果
        print("\n" + "=" * 70)
        print("审计结果汇总")
        print("=" * 70)
        
        for success in self.successes:
            print(success)
        
        for warning in self.warnings:
            print(warning)
        
        for issue in self.issues:
            print(issue)
        
        print("\n" + "=" * 70)
        if len(self.issues) == 0:
            print("✅ 系统完整性检查通过")
            if len(self.warnings) > 0:
                print(f"⚠️  有 {len(self.warnings)} 个警告需要注意")
            return True
        else:
            print(f"❌ 发现 {len(self.issues)} 个问题需要修复")
            return False

def main():
    """主函数"""
    auditor = SystemAuditor('.')
    if auditor.run_full_audit():
        print("\n✅ 建议操作:")
        print("1. 运行: python main.py              # 启动系统")
        print("2. 或运行: python fix_system.py      # 一键修复")
        return 0
    else:
        print("\n❌ 需要先修复上述问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
