import json
import os
from pathlib import Path

def check_nodes():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    config_file = root_dir / "node_dependencies.json"
    nodes_dir = root_dir / "nodes"

    # 1. 读取配置
    if not config_file.exists():
        print(f"Error: Config file not found at {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    expected_nodes = set(config.get("nodes", {}).keys())
    print(f"Expected Nodes (from config): {len(expected_nodes)}")

    # 2. 扫描实际目录
    if not nodes_dir.exists():
        print(f"Error: Nodes directory not found at {nodes_dir}")
        return

    actual_dirs = set()
    valid_nodes = set()
    empty_nodes = set()

    for item in nodes_dir.iterdir():
        if item.is_dir() and item.name.startswith("Node_"):
            actual_dirs.add(item.name)
            if (item / "main.py").exists():
                valid_nodes.add(item.name)
            else:
                empty_nodes.add(item.name)

    print(f"Actual Node Directories: {len(actual_dirs)}")
    print(f"Valid Nodes (with main.py): {len(valid_nodes)}")

    # 3. 比对差异
    missing_nodes = expected_nodes - actual_dirs
    extra_nodes = actual_dirs - expected_nodes

    print("\n=== Missing Nodes (Configured but not found) ===")
    if missing_nodes:
        for node in sorted(missing_nodes):
            print(f"- {node}")
    else:
        print("None")

    print("\n=== Extra Nodes (Found but not configured) ===")
    if extra_nodes:
        for node in sorted(extra_nodes):
            print(f"- {node}")
    else:
        print("None")

    print("\n=== Empty Nodes (Found but no main.py) ===")
    if empty_nodes:
        for node in sorted(empty_nodes):
            print(f"- {node}")
    else:
        print("None")

if __name__ == "__main__":
    check_nodes()
