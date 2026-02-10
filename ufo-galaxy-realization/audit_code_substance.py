import os
from pathlib import Path

def audit_code_substance():
    nodes_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization/nodes")
    
    print("=== Scanning for Hollow/Dummy Code ===")
    print(f"{'Node Name':<35} | {'Lines':<6} | {'Status':<10} | {'Suspicious Markers'}")
    print("-" * 80)
    
    hollow_count = 0
    
    for node_dir in sorted(nodes_dir.iterdir()):
        if not node_dir.is_dir() or not node_dir.name.startswith("Node_"):
            continue
            
        main_py = node_dir / "main.py"
        if not main_py.exists():
            print(f"{node_dir.name:<35} | {'0':<6} | MISSING   | No main.py found")
            continue
            
        with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            content = "".join(lines)
            
        loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        
        markers = []
        if "pass" in content and loc < 20: markers.append("pass_heavy")
        if "NotImplemented" in content: markers.append("NotImplemented")
        if "TODO" in content: markers.append("TODO")
        if "print(" in content and loc < 15: markers.append("print_only")
        
        status = "OK"
        if loc < 10:
            status = "HOLLOW"
            hollow_count += 1
        elif loc < 30 and markers:
            status = "SUSPECT"
        
        if status != "OK":
            print(f"{node_dir.name:<35} | {loc:<6} | {status:<10} | {', '.join(markers)}")

    if hollow_count == 0:
        print("\n✅ No obviously hollow nodes found (all > 10 LOC).")
    else:
        print(f"\n[WARNING] Found {hollow_count} potentially hollow nodes.")

if __name__ == "__main__":
    audit_code_substance()
