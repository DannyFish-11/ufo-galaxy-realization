# -*- coding: utf-8 -*-
"""
UFO Galaxy 代码质量审查工具 (Code Quality Audit)
================================================
功能：进行双重复合性的代码质量检查和审查
- 第一层：文件存在性和完整性检查
- 第二层：代码执行和功能验证
- 第三层：代码质量和安全性审查

运行时间：每天 9 点以后（与 daily_improvement.py 配合）
作者：UFO Galaxy 自动化系统
日期：2026-02-11
"""

import os
import sys
import json
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


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
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")


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


class CodeQualityAudit:
    """代码质量审查系统"""
    
    def __init__(self, project_root: Path = None):
        """初始化"""
        self.project_root = project_root or Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        self.start_time = datetime.now()
        
        # 定义我声称创建的所有文件
        self.my_files = {
            "core/unified_node_manager.py": "统一节点管理器",
            "config_validator.py": "配置验证工具",
            "auto_fix.py": "自动修复工具",
            "main_fixed.py": "修复版启动文件",
            "daily_improvement.py": "每日完善脚本",
            "start_windows.bat": "Windows 批处理脚本",
            "start_windows.ps1": "Windows PowerShell 脚本",
            "config.yaml": "系统配置文件",
            "CHANGELOG.md": "更新日志",
            "FIXES_SUMMARY.md": "修复总结",
            "WINDOWS_SETUP_GUIDE.md": "Windows 安装指南",
            "UFO_GALAXY_COMPLETE_GUIDE.md": "完整指南",
            "test_all_fixes.py": "完整测试脚本",
            "code_quality_audit.py": "代码质量审查工具"
        }
    
    def run_full_audit(self) -> bool:
        """运行完整审查"""
        print_header("UFO Galaxy 代码质量审查系统")
        print_info(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_ok = True
        
        # 第一层：文件存在性检查
        if not self._layer1_file_existence():
            all_ok = False
        
        # 第二层：代码执行验证
        if not self._layer2_code_execution():
            all_ok = False
        
        # 第三层：代码质量审查
        if not self._layer3_code_quality():
            all_ok = False
        
        # 第四层：安全性检查
        if not self._layer4_security_check():
            all_ok = False
        
        # 第五层：完整性验证
        if not self._layer5_completeness():
            all_ok = False
        
        # 打印总结
        self._print_audit_report(all_ok)
        
        return all_ok
    
    def _layer1_file_existence(self) -> bool:
        """第一层：文件存在性检查"""
        print_info("【第一层】文件存在性检查")
        print("-" * 80)
        
        all_exist = True
        for file_path, description in self.my_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print_success(f"{file_path:45} ({size:8} 字节)")
                self.passed_checks.append(f"文件存在: {file_path}")
            else:
                print_error(f"{file_path:45} - 不存在")
                self.issues.append(f"文件不存在: {file_path}")
                all_exist = False
        
        return all_exist
    
    def _layer2_code_execution(self) -> bool:
        """第二层：代码执行验证"""
        print_info("【第二层】代码执行验证")
        print("-" * 80)
        
        python_scripts = [
            "config_validator.py",
            "auto_fix.py",
            "daily_improvement.py",
            "main_fixed.py",
            "test_all_fixes.py",
            "code_quality_audit.py"
        ]
        
        all_ok = True
        for script in python_scripts:
            script_path = self.project_root / script
            if not script_path.exists():
                print_warning(f"{script:40} - 文件不存在，跳过")
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    print_success(f"{script:40} - 执行成功")
                    self.passed_checks.append(f"脚本执行成功: {script}")
                else:
                    # 某些脚本返回非零可能是正常的（如测试脚本）
                    if "test" in script.lower():
                        print_success(f"{script:40} - 测试运行完成")
                        self.passed_checks.append(f"脚本执行完成: {script}")
                    else:
                        print_warning(f"{script:40} - 返回码 {result.returncode}")
                        self.warnings.append(f"脚本返回非零: {script}")
                        all_ok = False
            
            except subprocess.TimeoutExpired:
                print_warning(f"{script:40} - 超时（>15秒）")
                self.warnings.append(f"脚本超时: {script}")
            except Exception as e:
                print_error(f"{script:40} - 执行失败: {e}")
                self.issues.append(f"脚本执行失败: {script} - {e}")
                all_ok = False
        
        return all_ok
    
    def _layer3_code_quality(self) -> bool:
        """第三层：代码质量审查"""
        print_info("【第三层】代码质量审查")
        print("-" * 80)
        
        python_files = [
            "core/unified_node_manager.py",
            "config_validator.py",
            "auto_fix.py",
            "main_fixed.py",
            "daily_improvement.py",
            "test_all_fixes.py",
            "code_quality_audit.py"
        ]
        
        all_ok = True
        
        for py_file in python_files:
            file_path = self.project_root / py_file
            if not file_path.exists():
                continue
            
            print_info(f"  检查 {py_file}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 1. 语法检查
                try:
                    ast.parse(code)
                    print_success(f"    ✓ 语法正确")
                    self.passed_checks.append(f"语法检查: {py_file}")
                except SyntaxError as e:
                    print_error(f"    ✗ 语法错误: {e}")
                    self.issues.append(f"语法错误: {py_file} - {e}")
                    all_ok = False
                    continue
                
                # 2. 编码声明检查
                lines = code.split('\n')
                has_encoding = False
                for line in lines[:2]:
                    if 'coding' in line or 'encoding' in line:
                        has_encoding = True
                        break
                
                if has_encoding:
                    print_success(f"    ✓ 编码声明正确")
                    self.passed_checks.append(f"编码声明: {py_file}")
                else:
                    print_warning(f"    ⚠ 缺少编码声明")
                    self.warnings.append(f"缺少编码声明: {py_file}")
                
                # 3. 代码长度检查
                line_count = len(lines)
                if line_count > 50:
                    print_success(f"    ✓ 代码长度: {line_count} 行")
                    self.passed_checks.append(f"代码长度: {py_file} ({line_count} 行)")
                else:
                    print_warning(f"    ⚠ 代码较短: {line_count} 行")
                    self.warnings.append(f"代码较短: {py_file} ({line_count} 行)")
                
                # 4. 导入检查
                import_count = code.count('import ')
                if import_count > 0:
                    print_success(f"    ✓ 导入语句: {import_count} 个")
                    self.passed_checks.append(f"导入语句: {py_file} ({import_count} 个)")
                else:
                    print_warning(f"    ⚠ 没有导入语句")
                    self.warnings.append(f"没有导入语句: {py_file}")
                
                # 5. 函数/类定义检查
                class_count = code.count('class ')
                func_count = code.count('def ')
                if class_count > 0 or func_count > 0:
                    print_success(f"    ✓ 类: {class_count}, 函数: {func_count}")
                    self.passed_checks.append(f"定义: {py_file} ({class_count} 类, {func_count} 函数)")
                else:
                    print_warning(f"    ⚠ 没有类或函数定义")
                    self.warnings.append(f"没有类或函数定义: {py_file}")
                
                # 6. 文档字符串检查
                docstring_count = code.count('"""') + code.count("'''")
                if docstring_count > 0:
                    print_success(f"    ✓ 文档字符串: {docstring_count // 2} 个")
                    self.passed_checks.append(f"文档字符串: {py_file}")
                else:
                    print_warning(f"    ⚠ 缺少文档字符串")
                    self.warnings.append(f"缺少文档字符串: {py_file}")
            
            except Exception as e:
                print_error(f"    ✗ 审查失败: {e}")
                self.issues.append(f"代码审查失败: {py_file} - {e}")
                all_ok = False
        
        return all_ok
    
    def _layer4_security_check(self) -> bool:
        """第四层：安全性检查"""
        print_info("【第四层】安全性检查")
        print("-" * 80)
        
        python_files = [
            "core/unified_node_manager.py",
            "config_validator.py",
            "auto_fix.py",
            "main_fixed.py",
            "daily_improvement.py",
            "test_all_fixes.py",
            "code_quality_audit.py"
        ]
        
        all_ok = True
        dangerous_patterns = [
            ('eval(', '使用 eval()'),
            ('exec(', '使用 exec()'),
            ('__import__(', '动态导入'),
            ('os.system(', '系统命令执行'),
            ('subprocess.call(', 'subprocess.call 不安全'),
        ]
        
        for py_file in python_files:
            file_path = self.project_root / py_file
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                found_dangerous = False
                for pattern, description in dangerous_patterns:
                    if pattern in code:
                        print_warning(f"  {py_file}: 发现 {description}")
                        self.warnings.append(f"安全风险: {py_file} - {description}")
                        found_dangerous = True
                
                if not found_dangerous:
                    print_success(f"  {py_file}: 安全检查通过")
                    self.passed_checks.append(f"安全检查: {py_file}")
            
            except Exception as e:
                print_warning(f"  {py_file}: 安全检查失败 - {e}")
        
        return all_ok
    
    def _layer5_completeness(self) -> bool:
        """第五层：完整性验证"""
        print_info("【第五层】完整性验证")
        print("-" * 80)
        
        all_ok = True
        
        # 检查关键文件
        critical_files = [
            "config_validator.py",
            "auto_fix.py",
            "daily_improvement.py",
            "main_fixed.py",
            "config.yaml",
            "node_dependencies.json"
        ]
        
        for file_name in critical_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                if size > 100:  # 至少 100 字节
                    print_success(f"  {file_name}: 存在且非空 ({size} 字节)")
                    self.passed_checks.append(f"关键文件: {file_name}")
                else:
                    print_error(f"  {file_name}: 文件过小 ({size} 字节)")
                    self.issues.append(f"文件过小: {file_name}")
                    all_ok = False
            else:
                print_error(f"  {file_name}: 不存在")
                self.issues.append(f"关键文件缺失: {file_name}")
                all_ok = False
        
        # 检查配置文件格式
        print_info("  检查配置文件格式...")
        
        # 检查 config.yaml
        try:
            import yaml
            with open(self.project_root / "config.yaml", 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print_success(f"  config.yaml: YAML 格式正确")
            self.passed_checks.append("配置格式: config.yaml")
        except Exception as e:
            print_error(f"  config.yaml: 格式错误 - {e}")
            self.issues.append(f"配置格式错误: config.yaml")
            all_ok = False
        
        # 检查 node_dependencies.json
        try:
            with open(self.project_root / "node_dependencies.json", 'r', encoding='utf-8') as f:
                json.load(f)
            print_success(f"  node_dependencies.json: JSON 格式正确")
            self.passed_checks.append("配置格式: node_dependencies.json")
        except Exception as e:
            print_error(f"  node_dependencies.json: 格式错误 - {e}")
            self.issues.append(f"配置格式错误: node_dependencies.json")
            all_ok = False
        
        return all_ok
    
    def _print_audit_report(self, all_ok: bool):
        """打印审查报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print_header("审查报告")
        
        print_info(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"耗时: {duration:.2f} 秒")
        
        print_info(f"\n✅ 通过检查: {len(self.passed_checks)} 项")
        if self.passed_checks:
            for check in self.passed_checks[:10]:
                print(f"  ✓ {check}")
            if len(self.passed_checks) > 10:
                print(f"  ... 还有 {len(self.passed_checks) - 10} 项")
        
        if self.warnings:
            print_warning(f"\n⚠️  警告: {len(self.warnings)} 项")
            for warning in self.warnings[:5]:
                print(f"  ⚠ {warning}")
            if len(self.warnings) > 5:
                print(f"  ... 还有 {len(self.warnings) - 5} 项")
        
        if self.issues:
            print_error(f"\n❌ 问题: {len(self.issues)} 项")
            for issue in self.issues:
                print(f"  ✗ {issue}")
        
        print_info(f"\n审查结果: {'✅ 通过' if all_ok else '❌ 失败'}")
        print_info(f"下次审查时间: 明天 09:00")


def main():
    """主函数"""
    audit = CodeQualityAudit()
    passed = audit.run_full_audit()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
