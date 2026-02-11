#!/usr/bin/env python3
"""
UFO³ Galaxy 智能启动器 (已弃用)
================================

⚠️  DEPRECATION WARNING - 弃用警告
-----------------------------------
此文件已被弃用，请使用统一启动入口。

推荐使用:
    python unified_launcher.py

或使用启动脚本:
    ./start.sh (Linux/Mac)
    start.bat (Windows)

此 wrapper 将调用统一启动器以保持向后兼容。
"""

import sys
import warnings
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """主函数 - 重定向到统一启动器"""
    # 打印弃用警告
    print("\n" + "=" * 70)
    print("⚠️  DEPRECATION WARNING - 弃用警告")
    print("=" * 70)
    print("galaxy_launcher.py 已被弃用，请使用统一启动入口。")
    print("\n推荐使用:")
    print("  python unified_launcher.py")
    print("\n或使用启动脚本:")
    print("  ./start.sh (Linux/Mac)")
    print("  start.bat (Windows)")
    print("=" * 70)
    print("\n正在重定向到统一启动器...\n")
    
    # 导入并调用统一启动器
    try:
        from unified_launcher import main as unified_main
        unified_main()
    except ImportError as e:
        print(f"错误: 无法导入统一启动器: {e}")
        print("请确保 unified_launcher.py 文件存在。")
        sys.exit(1)


if __name__ == "__main__":
    main()
