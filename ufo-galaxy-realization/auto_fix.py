# -*- coding: utf-8 -*-
"""
自动修复工具 (Auto-Fix Tool)
============================
自动检测和修复常见的配置问题：
1. 依赖引用格式不一致
2. 无效的节点分组
3. 缺失的配置字段
4. 编码问题
5. 端口冲突

使用方法：
    python auto_fix.py              # 运行自动修复
    python auto_fix.py --dry-run    # 预览修复（不实际修改）
    python auto_fix.py --report     # 生成修复报告

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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("AutoFix")


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


class AutoFixer:
    """自动修复工具"""
    
    VALID_GROUPS = {"core", "development", "extended", "academic"}
    REQUIRED_NODE_FIELDS = ["port", "group", "priority", "dependencies"]
    
    def __init__(self, project_root: Path = None, dry_run: bool = False):
        """初始化修复工具"""
        self.project_root = project_root or Path(__file__).parent
        self.config_file = self.project_root / "node_dependencies.json"
        self.env_file = self.project_root / ".env"
        self.dry_run = dry_run
        
        self.fixes_applied = []
        self.issues_found = []
        
    def run_all_fixes(self) -> bool:
        """运行所有修复"""
        print_header("UFO Galaxy 自动修复工具")
        
        if self.dry_run:
            print_warning("运行模式: 预览（不实际修改）")
        
        all_ok = True
        
        # 1. 修复依赖引用格式
        if not self._fix_dependency_references():
            all_ok = False
        
        # 2. 修复无效的节点分组
        if not self._fix_invalid_groups():
            all_ok = False
        
        # 3. 修复缺失的配置字段
        if not self._fix_missing_fields():
            all_ok = False
        
        # 4. 修复端口冲突
        if not self._fix_port_conflicts():
            all_ok = False
        
        # 5. 修复编码问题
        if not self._fix_encoding_issues():
            all_ok = False
        
        # 打印总结
        self._print_summary(all_ok)
        
        return all_ok
    
    def _fix_dependency_references(self) -> bool:
        """修复依赖引用格式"""
        print_info("检查依赖引用格式...")
        
        if not self.config_file.exists():
            print_error(f"配置文件不存在: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed_count = 0
            nodes = data.get('nodes', {})
            
            for node_name, node_config in nodes.items():
                deps = node_config.get('dependencies', [])
                new_deps = []
                
                for dep in deps:
                    if isinstance(dep, str):
                        # 如果是完整节点名称，提取 ID
                        if dep.startswith("Node_"):
                            parts = dep.split("_")
                            if len(parts) >= 2:
                                dep_id = parts[1]
                                if dep_id != dep:
                                    self.fixes_applied.append(
                                        f"修复依赖引用: {node_name}: {dep} -> {dep_id}"
                                    )
                                    fixed_count += 1
                                new_deps.append(dep_id)
                            else:
                                new_deps.append(dep)
                        else:
                            new_deps.append(dep)
                
                if new_deps != deps:
                    node_config['dependencies'] = new_deps
            
            if fixed_count > 0:
                if not self.dry_run:
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                print_success(f"修复了 {fixed_count} 个依赖引用")
            else:
                print_success("依赖引用格式正确")
            
            return True
        
        except Exception as e:
            print_error(f"修复依赖引用失败: {e}")
            self.issues_found.append(f"修复依赖引用失败: {e}")
            return False
    
    def _fix_invalid_groups(self) -> bool:
        """修复无效的节点分组"""
        print_info("检查节点分组...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed_count = 0
            nodes = data.get('nodes', {})
            
            for node_name, node_config in nodes.items():
                group = node_config.get('group', 'optional')
                
                if group not in self.VALID_GROUPS:
                    # 推断合适的分组
                    new_group = self._infer_group(node_name, group)
                    self.fixes_applied.append(
                        f"修复分组: {node_name}: {group} -> {new_group}"
                    )
                    node_config['group'] = new_group
                    fixed_count += 1
            
            if fixed_count > 0:
                if not self.dry_run:
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                print_success(f"修复了 {fixed_count} 个无效分组")
            else:
                print_success("所有节点分组都有效")
            
            return True
        
        except Exception as e:
            print_error(f"修复节点分组失败: {e}")
            self.issues_found.append(f"修复节点分组失败: {e}")
            return False
    
    def _infer_group(self, node_name: str, invalid_group: str) -> str:
        """推断合适的分组"""
        keywords = {
            "core": ["StateMachine", "OneAPI", "Tasker", "Router", "Auth"],
            "development": ["Git", "Filesystem", "Fetch", "Sandbox", "GitHub"],
            "extended": ["Android", "VLM", "ADB", "Scrcpy", "Camera", "Audio", "Media"],
            "academic": ["Knowledge", "Learning", "Search", "Academic"],
        }
        
        for group, kws in keywords.items():
            for kw in kws:
                if kw in node_name:
                    return group
        
        # 默认分组
        if "Node_0" in node_name or "Node_1" in node_name:
            return "core"
        elif "Node_2" in node_name or "Node_3" in node_name:
            return "development"
        else:
            return "extended"
    
    def _fix_missing_fields(self) -> bool:
        """修复缺失的配置字段"""
        print_info("检查缺失的配置字段...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed_count = 0
            nodes = data.get('nodes', {})
            
            for node_name, node_config in nodes.items():
                # 检查必需字段
                for field in self.REQUIRED_NODE_FIELDS:
                    if field not in node_config:
                        # 添加默认值
                        if field == "port":
                            # 从节点 ID 推断端口
                            parts = node_name.split("_")
                            if len(parts) >= 2 and parts[1].isdigit():
                                node_config[field] = 8000 + int(parts[1])
                            else:
                                node_config[field] = 8000
                        elif field == "group":
                            node_config[field] = "extended"
                        elif field == "priority":
                            node_config[field] = 50
                        elif field == "dependencies":
                            node_config[field] = []
                        
                        self.fixes_applied.append(
                            f"添加缺失字段: {node_name}.{field} = {node_config[field]}"
                        )
                        fixed_count += 1
            
            if fixed_count > 0:
                if not self.dry_run:
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                print_success(f"添加了 {fixed_count} 个缺失字段")
            else:
                print_success("所有必需字段都存在")
            
            return True
        
        except Exception as e:
            print_error(f"修复缺失字段失败: {e}")
            self.issues_found.append(f"修复缺失字段失败: {e}")
            return False
    
    def _fix_port_conflicts(self) -> bool:
        """修复端口冲突"""
        print_info("检查端口冲突...")
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nodes = data.get('nodes', {})
            ports = defaultdict(list)
            
            # 收集所有端口
            for node_name, node_config in nodes.items():
                port = node_config.get('port')
                if port:
                    ports[port].append(node_name)
            
            # 检查冲突
            conflicts = {port: node_list for port, node_list in ports.items() 
                        if len(node_list) > 1}
            
            if conflicts:
                print_warning(f"发现 {len(conflicts)} 个端口冲突")
                
                # 修复冲突
                fixed_count = 0
                used_ports = set(ports.keys())
                
                for port, node_list in conflicts.items():
                    # 保留第一个节点，其他节点分配新端口
                    for node_name in node_list[1:]:
                        new_port = self._find_free_port(used_ports)
                        nodes[node_name]['port'] = new_port
                        used_ports.add(new_port)
                        self.fixes_applied.append(
                            f"修复端口冲突: {node_name}: {port} -> {new_port}"
                        )
                        fixed_count += 1
                
                if fixed_count > 0:
                    if not self.dry_run:
                        with open(self.config_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    print_success(f"修复了 {fixed_count} 个端口冲突")
            else:
                print_success("没有端口冲突")
            
            return True
        
        except Exception as e:
            print_error(f"修复端口冲突失败: {e}")
            self.issues_found.append(f"修复端口冲突失败: {e}")
            return False
    
    def _find_free_port(self, used_ports: Set[int], start: int = 8000) -> int:
        """找到一个未使用的端口"""
        port = start
        while port in used_ports:
            port += 1
        return port
    
    def _fix_encoding_issues(self) -> bool:
        """修复编码问题"""
        print_info("检查编码问题...")
        
        fixed_count = 0
        
        # 检查 Python 文件的编码声明
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有编码声明
                if not content.startswith("# -*- coding: utf-8 -*-"):
                    # 添加编码声明
                    if not self.dry_run:
                        new_content = "# -*- coding: utf-8 -*-\n" + content
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    self.fixes_applied.append(f"添加编码声明: {py_file.name}")
                    fixed_count += 1
            except Exception as e:
                logger.debug(f"检查 {py_file} 失败: {e}")
        
        if fixed_count > 0:
            print_success(f"修复了 {fixed_count} 个编码问题")
        else:
            print_success("没有编码问题")
        
        return True
    
    def _print_summary(self, all_ok: bool):
        """打印总结"""
        print_header("修复总结")
        
        if all_ok:
            print_success("所有修复完成！")
        else:
            print_error("修复过程中遇到错误")
        
        if self.fixes_applied:
            print_info(f"共应用 {len(self.fixes_applied)} 个修复:")
            for fix in self.fixes_applied[:10]:
                print(f"  - {fix}")
            if len(self.fixes_applied) > 10:
                print(f"  ... 还有 {len(self.fixes_applied) - 10} 个修复")
        
        if self.issues_found:
            print_error(f"共发现 {len(self.issues_found)} 个问题:")
            for issue in self.issues_found:
                print(f"  - {issue}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="UFO Galaxy 自动修复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python auto_fix.py              # 运行自动修复
    python auto_fix.py --dry-run    # 预览修复
        """
    )
    parser.add_argument("--dry-run", "-d", action="store_true", help="预览修复（不实际修改）")
    
    args = parser.parse_args()
    
    fixer = AutoFixer(dry_run=args.dry_run)
    passed = fixer.run_all_fixes()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
