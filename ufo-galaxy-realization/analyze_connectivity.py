import json
import re
from pathlib import Path
from collections import defaultdict

def analyze_connectivity():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    nodes_dir = root_dir / "nodes"
    
    print("=== Connectivity & Workflow Analysis ===")
    
    # 1. Scan for cross-node calls (e.g., requests to other ports or node names)
    # Heuristic: Look for "localhost:8xxx" or "Node_XX" in code
    
    calls = defaultdict(set)
    
    for py_file in nodes_dir.rglob("*.py"):
        node_name = py_file.parent.name
        if not node_name.startswith("Node_"): continue
        
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Find port calls (8000-8200)
            ports = re.findall(r'localhost:(\d{4})', content)
            for p in ports:
                if 8000 <= int(p) <= 8200:
                    calls[node_name].add(f"Port {p}")
            
            # Find explicit node references
            refs = re.findall(r'(Node_\d{2,3}_[a-zA-Z0-9_]+)', content)
            for r in refs:
                if r != node_name:
                    calls[node_name].add(r)

    # 2. Report Connectivity
    print(f"\n[Active Inter-Node Connections] ({len(calls)} Nodes initiating calls)")
    for src, targets in sorted(calls.items()):
        if not targets: continue
        print(f"  {src} calls:")
        for t in sorted(targets):
            print(f"    -> {t}")

    # 3. Check Router Logic
    router_path = nodes_dir / "Node_04_Router" / "main.py"
    if router_path.exists():
        print("\n[Router Configuration]")
        with open(router_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "routes" in content or "dispatch" in content:
                print("  ✅ Router has dispatch logic.")
            else:
                print("  ⚠️ Router logic seems empty.")
    else:
        print("\n[Router Configuration]\n  ❌ Node_04_Router not found!")

if __name__ == "__main__":
    analyze_connectivity()
