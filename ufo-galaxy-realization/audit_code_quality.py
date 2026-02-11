# -*- coding: utf-8 -*-
import os
import ast
import sys

def check_file_quality(filepath):
    """
    检查单个文件的代码质量：
    1. 是否包含 'pass' 或 '...' 作为函数体的唯一内容（假实现）
    2. 是否包含 'TODO' 或 'FIXME' 注释
    3. 是否有语法错误
    """
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 语法检查
        tree = ast.parse(content)
        
        # 遍历 AST 查找空函数
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.body) == 1:
                    stmt = node.body[0]
                    if isinstance(stmt, ast.Pass) or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value == ...):
                        issues.append(f"Empty function body found: {node.name}")
                        
        # 查找 TODO/FIXME
        for i, line in enumerate(content.splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                issues.append(f"TODO/FIXME found at line {i}: {line.strip()}")
                
    except SyntaxError as e:
        issues.append(f"Syntax Error: {e}")
    except Exception as e:
        issues.append(f"Read Error: {e}")
        
    return issues

def audit_all_files(root_dir):
    """遍历所有 .py 文件进行审计"""
    report = {}
    for root, dirs, files in os.walk(root_dir):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                issues = check_file_quality(path)
                if issues:
                    report[path] = issues
    return report

if __name__ == "__main__":
    root_dir = os.getcwd()
    print(f"Starting nuclear-level audit in {root_dir}...")
    report = audit_all_files(root_dir)
    
    if report:
        print("\n[AUDIT FAILED] Issues found:")
        for path, issues in report.items():
            print(f"\nFile: {path}")
            for issue in issues:
                print(f"  - {issue}")
        sys.exit(1)
    else:
        print("\n[AUDIT PASSED] No empty shells or syntax errors found.")
        sys.exit(0)
