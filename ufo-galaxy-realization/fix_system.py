# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
UFO Galaxy 系统一键修复脚本
自动修复编码问题、配置问题、依赖问题等
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path

class SystemFixer:
    """系统修复器"""
    
    def __init__(self, project_root='.'):
        self.root = Path(project_root)
        self.fixed_count = 0
        self.error_count = 0
    
    def fix_encoding_issues(self):
        """修复编码问题"""
        print("\n🔧 修复编码问题...")
        
        python_files = list(self.root.rglob('*.py'))
        fixed = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 修复 open() 调用
                original_content = content
                
                # 模式1: with open(..., 'r', encoding='utf-8') as f:
                content = re.sub(
                    r"with\s+open\(([^)]+),\s*['\"]r['\"]\s*\)\s+as\s+",
                    r"with open(\1, 'r', encoding='utf-8') as ",
                    content
                )
                
                # 模式2: open(..., 'r', encoding='utf-8')
                content = re.sub(
                    r"open\(([^)]+),\s*['\"]r['\"]\s*\)",
                    r"open(\1, 'r', encoding='utf-8')",
                    content
                )
                
                # 模式3: open(...) 默认为 'r'
                content = re.sub(
                    r"open\(([^,)]+)\)\s*(?=\.|\.read|\.write)",
                    r"open(\1, 'r', encoding='utf-8')",
                    content
                )
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed += 1
                    
            except Exception as e:
                print(f"  ⚠️  {py_file}: {e}")
        
        print(f"  ✅ 修复了 {fixed} 个文件的编码问题")
        self.fixed_count += fixed
        return fixed
    
    def fix_json_files(self):
        """修复JSON文件格式"""
        print("\n🔧 验证JSON文件...")
        
        json_files = list(self.root.rglob('*.json'))
        fixed = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 重新写入以确保格式正确
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                fixed += 1
                
            except json.JSONDecodeError as e:
                print(f"  ❌ {json_file}: JSON格式错误 - {e}")
                self.error_count += 1
            except Exception as e:
                print(f"  ⚠️  {json_file}: {e}")
        
        print(f"  ✅ 验证了 {fixed} 个JSON文件")
        return fixed
    
    def fix_requirements(self):
        """修复requirements.txt"""
        print("\n🔧 检查依赖...")
        
        req_file = self.root / 'requirements.txt'
        if not req_file.exists():
            print("  ⚠️  requirements.txt 不存在，跳过")
            return 0
        
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 移除重复和空行
            unique_lines = []
            seen = set()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if pkg_name not in seen:
                        seen.add(pkg_name)
                        unique_lines.append(line + '\n')
                elif line.startswith('#'):
                    unique_lines.append(line + '\n')
            
            with open(req_file, 'w', encoding='utf-8') as f:
                f.writelines(unique_lines)
            
            print(f"  ✅ 清理了 requirements.txt")
            return 1
            
        except Exception as e:
            print(f"  ❌ 无法修复 requirements.txt: {e}")
            self.error_count += 1
            return 0
    
    def create_env_file(self):
        """创建.env文件"""
        print("\n🔧 创建环境配置...")
        
        env_file = self.root / '.env'
        env_example = self.root / '.env.example'
        
        if env_file.exists():
            print("  ✅ .env 文件已存在")
            return 0
        
        if env_example.exists():
            try:
                with open(env_example, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("  ✅ 从 .env.example 创建了 .env")
                return 1
                
            except Exception as e:
                print(f"  ⚠️  无法创建 .env: {e}")
                return 0
        else:
            print("  ⚠️  .env.example 不存在，无法创建 .env")
            return 0
    
    def verify_node_structure(self):
        """验证节点结构"""
        print("\n🔧 验证节点结构...")
        
        nodes_dir = self.root / 'nodes'
        if not nodes_dir.exists():
            print("  ❌ nodes 目录不存在")
            self.error_count += 1
            return 0
        
        node_dirs = [d for d in nodes_dir.iterdir() if d.is_dir() and d.name.startswith('Node_')]
        
        fixed = 0
        for node_dir in node_dirs:
            main_py = node_dir / 'main.py'
            if not main_py.exists():
                print(f"  ⚠️  {node_dir.name} 缺少 main.py")
            else:
                fixed += 1
        
        print(f"  ✅ 验证了 {len(node_dirs)} 个节点，{fixed} 个完整")
        return fixed
    
    def run_full_fix(self):
        """运行完整修复"""
        print("=" * 70)
        print("UFO Galaxy 系统一键修复")
        print("=" * 70)
        
        # 执行修复步骤
        self.fix_encoding_issues()
        self.fix_json_files()
        self.fix_requirements()
        self.create_env_file()
        self.verify_node_structure()
        
        # 打印总结
        print("\n" + "=" * 70)
        print("修复完成")
        print("=" * 70)
        print(f"✅ 修复项: {self.fixed_count}")
        print(f"❌ 错误数: {self.error_count}")
        
        if self.error_count == 0:
            print("\n✅ 系统修复完成，可以启动了")
            print("\n建议操作:")
            print("1. python main.py                    # 启动系统")
            print("2. python system_audit.py            # 再次审计系统")
            return 0
        else:
            print(f"\n⚠️  还有 {self.error_count} 个错误需要手动修复")
            return 1

def main():
    """主函数"""
    fixer = SystemFixer('.')
    return fixer.run_full_fix()

if __name__ == '__main__':
    sys.exit(main())
