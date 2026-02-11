# -*- coding: utf-8 -*-
"""
配置验证工具 (Configuration Validator)
======================================
系统性检查节点配置的完整性和一致性：
1. 配置文件格式验证
2. 节点定义与实际目录同步检查
3. 依赖关系验证
4. 端口冲突检测
5. 环境变量检查
6. 自动修复建议

使用方法：
    python config_validator.py                # 运行验证
    python config_validator.py --fix          # 自动修复
    python config_validator.py --report       # 生成报告

作者：UFO Galaxy 修复系统
日期：2026-02-11
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ConfigValidator")


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


def print_header(title: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}\n")


def print_success(msg: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg: str):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def print_info(msg: str):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, project_root: Path = None):
        """初始化验证器"""
        self.project_root = project_root or Path(__file__).parent
        self.nodes_dir = self.project_root / "nodes"
        self.config_file = self.project_root / "node_dependencies.json"
        self.env_file = self.project_root / ".env"
        
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.fixes: List[Tuple[str, str]] = []  # (问题, 修复方案)
        
    def validate_all(self) -> bool:
        """执行所有验证"""
        print_header("UFO Galaxy 配置验证")
        
        all_passed = True
        
        # 1. 验证配置文件存在
        if not self._check_config_files_exist():
            all_passed = False
        
        # 2. 验证配置文件格式
        if not self._check_config_format():
            all_passed = False
        
        # 3. 验证节点目录
        if not self._check_node_directories():
            all_passed = False
        
        # 4. 验证节点定义与目录同步
        if not self._check_config_node_sync():
            all_passed = False
        
        # 5. 验证依赖关系
        if not self._check_dependencies():
            all_passed = False
        
        # 6. 验证端口
        if not self._check_ports():
            all_passed = False
        
        # 7. 验证环境变量
        if not self._check_env_vars():
            all_passed = False
        
        # 8. 打印总结
        self._print_summary(all_passed)
        
        return all_passed
    
    def _check_config_files_exist(self) -> bool:
        """检查配置文件是否存在"""
        print_info("检查配置文件存在性...")
        
        passed = True
        
        if not self.config_file.exists():
            print_error(f"配置文件不存在: {self.config_file}")
            self.errors.append(f"缺少配置文件: {self.config_file}")
            passed = False
        else:
            print_success(f"配置文件存在: {self.config_file}")
        
        if not self.nodes_dir.exists():
            print_error(f"节点目录不存在: {self.nodes_dir}")
            self.errors.append(f"缺少节点目录: {self.nodes_dir}")
            passed = False
        else:
            print_success(f"节点目录存在: {self.nodes_dir}")
        
        return passed
    
    def _check_config_format(self) -> bool:
        """检查配置文件格式"""
        print_info("检查配置文件格式...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查必要字段
            if "nodes" not in data:
                print_warning("配置文件缺少 'nodes' 字段")
                self.warnings.append("配置文件缺少 'nodes' 字段")
            else:
                print_success(f"配置文件格式正确，包含 {len(data['nodes'])} 个节点定义")
            
            if "groups" not in data:
                print_warning("配置文件缺少 'groups' 字段")
                self.warnings.append("配置文件缺少 'groups' 字段")
            else:
                print_success(f"配置文件包含 {len(data['groups'])} 个分组定义")
            
            return True
        
        except json.JSONDecodeError as e:
            print_error(f"JSON 格式错误: {e}")
            self.errors.append(f"JSON 格式错误: {e}")
            return False
        except Exception as e:
            print_error(f"读取配置文件失败: {e}")
            self.errors.append(f"读取配置文件失败: {e}")
            return False
    
    def _check_node_directories(self) -> bool:
        """检查节点目录"""
        print_info("检查节点目录...")
        
        if not self.nodes_dir.exists():
            return False
        
        try:
            node_dirs = []
            for item in self.nodes_dir.iterdir():
                if item.is_dir() and item.name.startswith("Node_"):
                    node_dirs.append(item.name)
                    
                    # 检查 main.py
                    main_py = item / "main.py"
                    if not main_py.exists():
                        print_warning(f"节点目录缺少 main.py: {item.name}")
                        self.warnings.append(f"节点目录缺少 main.py: {item.name}")
            
            print_success(f"找到 {len(node_dirs)} 个节点目录")
            return True
        
        except Exception as e:
            print_error(f"扫描节点目录失败: {e}")
            self.errors.append(f"扫描节点目录失败: {e}")
            return False
    
    def _check_config_node_sync(self) -> bool:
        """检查配置定义与节点目录同步"""
        print_info("检查配置定义与节点目录同步...")
        
        if not self.config_file.exists() or not self.nodes_dir.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config_nodes = set(config_data.get("nodes", {}).keys())
            
            # 扫描实际节点
            actual_nodes = set()
            for item in self.nodes_dir.iterdir():
                if item.is_dir() and item.name.startswith("Node_"):
                    actual_nodes.add(item.name)
            
            # 检查配置中有但实际没有的
            missing_dirs = config_nodes - actual_nodes
            if missing_dirs:
                for node in sorted(missing_dirs):
                    print_warning(f"配置定义存在但无实际目录: {node}")
                    self.warnings.append(f"配置定义存在但无实际目录: {node}")
            
            # 检查实际有但配置中没有的
            missing_configs = actual_nodes - config_nodes
            if missing_configs:
                for node in sorted(missing_configs):
                    print_warning(f"实际目录存在但无配置定义: {node}")
                    self.warnings.append(f"实际目录存在但无配置定义: {node}")
                    self.fixes.append((
                        f"缺少配置: {node}",
                        f"需要在 node_dependencies.json 中添加 {node} 的配置"
                    ))
            
            if not missing_dirs and not missing_configs:
                print_success(f"配置定义与节点目录完全同步 ({len(config_nodes)} 个节点)")
                return True
            else:
                return False
        
        except Exception as e:
            print_error(f"检查同步性失败: {e}")
            self.errors.append(f"检查同步性失败: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """检查依赖关系"""
        print_info("检查依赖关系...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            nodes = config_data.get("nodes", {})
            
            # 收集所有节点 ID
            node_ids = set()
            for node_name, node_config in nodes.items():
                node_id = node_config.get("id", node_name.split("_")[1])
                node_ids.add(node_id)
            
            # 检查依赖
            invalid_deps = []
            for node_name, node_config in nodes.items():
                deps = node_config.get("dependencies", [])
                for dep_id in deps:
                    if dep_id not in node_ids:
                        invalid_deps.append((node_name, dep_id))
                        print_warning(f"节点 {node_name} 的依赖 {dep_id} 不存在")
                        self.warnings.append(f"节点 {node_name} 的依赖 {dep_id} 不存在")
            
            if not invalid_deps:
                print_success(f"依赖关系验证通过")
                return True
            else:
                self.errors.append(f"发现 {len(invalid_deps)} 个无效依赖")
                return False
        
        except Exception as e:
            print_error(f"检查依赖关系失败: {e}")
            self.errors.append(f"检查依赖关系失败: {e}")
            return False
    
    def _check_ports(self) -> bool:
        """检查端口"""
        print_info("检查端口...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            nodes = config_data.get("nodes", {})
            
            # 收集端口
            ports = defaultdict(list)
            for node_name, node_config in nodes.items():
                port = node_config.get("port")
                if port:
                    ports[port].append(node_name)
            
            # 检查冲突
            conflicts = {port: nodes for port, nodes in ports.items() if len(nodes) > 1}
            
            if conflicts:
                for port, node_list in conflicts.items():
                    print_error(f"端口冲突: {port} 被多个节点使用: {', '.join(node_list)}")
                    self.errors.append(f"端口冲突: {port}")
                return False
            else:
                print_success(f"端口检查通过，{len(ports)} 个端口无冲突")
                return True
        
        except Exception as e:
            print_error(f"检查端口失败: {e}")
            self.errors.append(f"检查端口失败: {e}")
            return False
    
    def _check_env_vars(self) -> bool:
        """检查环境变量"""
        print_info("检查环境变量...")
        
        required_vars = [
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
            "XAI_API_KEY",
        ]
        
        found_vars = []
        missing_vars = []
        
        for var in required_vars:
            if os.environ.get(var):
                found_vars.append(var)
            else:
                missing_vars.append(var)
        
        if found_vars:
            print_success(f"检测到 {len(found_vars)} 个 API 密钥: {', '.join(found_vars)}")
        
        if missing_vars:
            print_warning(f"缺少 {len(missing_vars)} 个 API 密钥: {', '.join(missing_vars)}")
            self.warnings.append(f"缺少 API 密钥: {', '.join(missing_vars)}")
        
        return len(found_vars) > 0
    
    def _print_summary(self, passed: bool):
        """打印总结"""
        print_header("验证总结")
        
        if passed:
            print_success("所有验证通过！系统配置正确。")
        else:
            print_error(f"验证失败！共 {len(self.errors)} 个错误。")
        
        if self.warnings:
            print_warning(f"共 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.fixes:
            print_info(f"共 {len(self.fixes)} 个修复建议:")
            for problem, fix in self.fixes:
                print(f"  - 问题: {problem}")
                print(f"    修复: {fix}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="UFO Galaxy 配置验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python config_validator.py              # 运行验证
    python config_validator.py --report     # 生成详细报告
        """
    )
    parser.add_argument("--report", "-r", action="store_true", help="生成详细报告")
    
    args = parser.parse_args()
    
    validator = ConfigValidator()
    passed = validator.validate_all()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
