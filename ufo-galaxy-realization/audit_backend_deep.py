# -*- coding: utf-8 -*-
import os
import json
import re
from pathlib import Path

def audit_backend():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    print(f"=== Deep Audit: Backend ({root_dir}) ===")
    
    # 1. Entry Point Check
    launcher = root_dir / "unified_launcher.py"
    if launcher.exists():
        print("✅ Entry point 'unified_launcher.py' exists.")
        # Check if it imports necessary modules
        with open(launcher, 'r', encoding='utf-8') as f:
            content = f.read()
            if "uvicorn" in content and "FastAPI" in content:
                print("  ✅ Entry point seems to use FastAPI/Uvicorn.")
            else:
                print("  ⚠️ Entry point might be missing web server logic.")
    else:
        print("❌ Entry point 'unified_launcher.py' MISSING!")

    # 2. Node Integrity Check
    nodes_dir = root_dir / "nodes"
    if nodes_dir.exists():
        nodes = [d for d in nodes_dir.iterdir() if d.is_dir() and d.name.startswith("Node_")]
        print(f"✅ Found {len(nodes)} node directories.")
        
        valid_nodes = 0
        for node in nodes:
            main_py = node / "main.py"
            if main_py.exists():
                valid_nodes += 1
            else:
                print(f"  ❌ Node {node.name} is missing main.py!")
        
        if valid_nodes == len(nodes):
            print(f"  ✅ All {valid_nodes} nodes have main.py.")
    else:
        print("❌ 'nodes' directory MISSING!")

    # 3. Dependency Check
    req_file = root_dir / "requirements.txt"
    if req_file.exists():
        print("✅ 'requirements.txt' exists.")
        with open(req_file, 'r', encoding='utf-8') as f:
            reqs = f.read().splitlines()
            print(f"  Found {len(reqs)} dependencies listed.")
    else:
        print("❌ 'requirements.txt' MISSING!")

    # 4. Config Check
    config_file = root_dir / "node_dependencies.json"
    if config_file.exists():
        print("✅ 'node_dependencies.json' exists.")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                node_count = len(config.get("nodes", {}))
                print(f"  Config defines {node_count} nodes.")
        except json.JSONDecodeError:
            print("  ❌ Config file is invalid JSON!")
    else:
        print("❌ 'node_dependencies.json' MISSING!")

if __name__ == "__main__":
    audit_backend()
