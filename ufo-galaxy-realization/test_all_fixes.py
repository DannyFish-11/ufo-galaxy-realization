# -*- coding: utf-8 -*-
"""
完整测试脚本 - 验证所有修复
============================
测试项目：
1. 配置验证
2. 自动修复
3. 启动流程
4. 节点管理
5. 依赖关系
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.unified_node_manager import UnifiedNodeManager, NodeGroup

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str, passed: bool):
    """打印测试结果"""
    status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if passed else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
    print(f"{status} | {name}")

def test_config_validator():
    """测试配置验证工具"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 1: 配置验证工具{Colors.ENDC}")
    result = subprocess.run(
        [sys.executable, "config_validator.py"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    passed = result.returncode == 0
    print_test("config_validator.py", passed)
    return passed

def test_auto_fix():
    """测试自动修复工具"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 2: 自动修复工具{Colors.ENDC}")
    result = subprocess.run(
        [sys.executable, "auto_fix.py", "--dry-run"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    passed = "✅ 所有修复完成" in result.stdout
    print_test("auto_fix.py --dry-run", passed)
    return passed

def test_unified_node_manager():
    """测试统一节点管理器"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 3: 统一节点管理器{Colors.ENDC}")
    
    try:
        manager = UnifiedNodeManager(PROJECT_ROOT)
        
        # 测试配置加载
        passed1 = manager.load_configurations()
        print_test("加载节点配置", passed1)
        
        # 测试节点统计
        all_nodes = manager.get_all_nodes()
        passed2 = len(all_nodes) == 108
        print_test(f"节点总数验证 ({len(all_nodes)}/108)", passed2)
        
        # 测试核心节点
        core_nodes = manager.get_core_nodes()
        passed3 = len(core_nodes) == 15
        print_test(f"核心节点验证 ({len(core_nodes)}/15)", passed3)
        
        # 测试启动顺序
        startup_order = manager.get_startup_order()
        passed4 = len(startup_order) > 0
        print_test(f"启动顺序生成 ({len(startup_order)} 个节点)", passed4)
        
        # 测试分组
        for group in NodeGroup:
            nodes = manager.get_nodes_by_group(group)
            if nodes:
                print_test(f"分组验证: {group.value} ({len(nodes)} 个)", True)
        
        return passed1 and passed2 and passed3 and passed4
    
    except Exception as e:
        print_test(f"统一节点管理器", False)
        print(f"  错误: {e}")
        return False

def test_main_fixed():
    """测试修复版启动文件"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 4: 修复版启动文件{Colors.ENDC}")
    
    result = subprocess.run(
        [sys.executable, "main_fixed.py", "--validate"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=30
    )
    
    passed = "配置验证完成，系统已准备就绪" in result.stdout
    print_test("main_fixed.py --validate", passed)
    
    # 检查启动流程
    checks = [
        ("第一步：检查依赖", "第一步：检查依赖" in result.stdout),
        ("第二步：加载环境变量", "第二步：加载环境变量" in result.stdout),
        ("第三步：加载节点配置", "第三步：加载节点配置" in result.stdout),
        ("第四步：节点统计", "第四步：节点统计" in result.stdout),
        ("验证完成", "验证完成" in result.stdout),
    ]
    
    for check_name, check_result in checks:
        print_test(f"  {check_name}", check_result)
    
    return passed

def test_dependencies():
    """测试依赖关系"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 5: 依赖关系{Colors.ENDC}")
    
    try:
        config_file = PROJECT_ROOT / "node_dependencies.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', {})
        
        # 检查所有依赖都是 ID 格式
        all_valid = True
        for node_name, node_config in nodes.items():
            deps = node_config.get('dependencies', [])
            for dep in deps:
                if dep.startswith("Node_"):
                    all_valid = False
                    print_test(f"  依赖格式检查: {node_name} -> {dep}", False)
                    break
        
        if all_valid:
            print_test("所有依赖格式正确", True)
        
        # 检查所有分组都有效
        valid_groups = {"core", "development", "extended", "academic"}
        invalid_groups = set()
        for node_name, node_config in nodes.items():
            group = node_config.get('group', 'optional')
            if group not in valid_groups:
                invalid_groups.add(group)
        
        if not invalid_groups:
            print_test("所有节点分组有效", True)
        else:
            print_test(f"无效分组: {invalid_groups}", False)
            all_valid = False
        
        return all_valid
    
    except Exception as e:
        print_test("依赖关系检查", False)
        print(f"  错误: {e}")
        return False

def test_windows_scripts():
    """测试 Windows 脚本存在性"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 6: Windows 脚本{Colors.ENDC}")
    
    scripts = [
        "start_windows.bat",
        "start_windows.ps1",
    ]
    
    all_exist = True
    for script in scripts:
        script_path = PROJECT_ROOT / script
        exists = script_path.exists()
        print_test(f"{script} 存在", exists)
        all_exist = all_exist and exists
    
    return all_exist

def test_documentation():
    """测试文档存在性"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}测试 7: 文档{Colors.ENDC}")
    
    docs = [
        "WINDOWS_SETUP_GUIDE.md",
        "FIXES_SUMMARY.md",
        "UFO_GALAXY_COMPLETE_GUIDE.md",
    ]
    
    all_exist = True
    for doc in docs:
        doc_path = PROJECT_ROOT / doc
        exists = doc_path.exists()
        print_test(f"{doc} 存在", exists)
        all_exist = all_exist and exists
    
    return all_exist

def main():
    """主测试函数"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}UFO Galaxy 完整测试{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
    
    results = []
    
    # 运行所有测试
    results.append(("配置验证工具", test_config_validator()))
    results.append(("自动修复工具", test_auto_fix()))
    results.append(("统一节点管理器", test_unified_node_manager()))
    results.append(("修复版启动文件", test_main_fixed()))
    results.append(("依赖关系", test_dependencies()))
    results.append(("Windows 脚本", test_windows_scripts()))
    results.append(("文档", test_documentation()))
    
    # 打印总结
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}测试总结{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = f"{Colors.GREEN}✅{Colors.ENDC}" if passed else f"{Colors.RED}❌{Colors.ENDC}"
        print(f"{status} {name}")
    
    print(f"\n总体结果: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ 所有测试通过！系统已准备就绪。{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ 部分测试失败，请检查。{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
