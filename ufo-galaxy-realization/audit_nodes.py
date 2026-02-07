import os
import json
import importlib.util
import sys

def audit_nodes(nodes_dir="nodes"):
    print(f"--- Starting De-Hallucination Audit on {nodes_dir} ---")
    
    if not os.path.exists(nodes_dir):
        print(f"❌ CRITICAL: Nodes directory '{nodes_dir}' does not exist!")
        return

    nodes = [d for d in os.listdir(nodes_dir) if os.path.isdir(os.path.join(nodes_dir, d))]
    print(f"Found {len(nodes)} node directories.")
    
    issues = []
    
    for node in nodes:
        node_path = os.path.join(nodes_dir, node)
        config_path = os.path.join(node_path, "config.json")
        entry_path = os.path.join(node_path, "fusion_entry.py")
        
        # 1. Check config.json
        if not os.path.exists(config_path):
            issues.append(f"❌ {node}: Missing config.json")
            continue
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "capabilities" not in config or "actions" not in config:
                    issues.append(f"⚠️ {node}: Invalid config.json structure")
        except json.JSONDecodeError:
            issues.append(f"❌ {node}: Corrupted config.json")
            
        # 2. Check fusion_entry.py existence
        if not os.path.exists(entry_path):
            issues.append(f"❌ {node}: Missing fusion_entry.py")
            continue
            
        # 3. Check code validity (Syntax Check)
        try:
            with open(entry_path, 'r') as f:
                source = f.read()
            compile(source, entry_path, 'exec')
        except SyntaxError as e:
            issues.append(f"❌ {node}: Syntax Error in fusion_entry.py: {e}")
            continue
            
        # 4. Check for "pass" implementation (Hallucination Check)
        if "pass" in source and "def execute" in source and len(source.splitlines()) < 10:
             issues.append(f"⚠️ {node}: Suspicious 'pass' implementation (Possible Hallucination)")

    print("\n--- Audit Results ---")
    if not issues:
        print("✅ All nodes passed basic structural audit.")
    else:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(issue)

if __name__ == "__main__":
    audit_nodes()
