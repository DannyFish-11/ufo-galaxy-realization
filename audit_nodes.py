import os
import ast
import sys

NODES_DIR = "/home/ubuntu/delivery/ufo-galaxy-realization/nodes"

def check_node(node_path):
    """检查单个节点的完整性"""
    node_id = os.path.basename(node_path)
    main_py = os.path.join(node_path, "main.py")
    
    if not os.path.exists(main_py):
        return {"status": "error", "msg": "Missing main.py"}
    
    try:
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
            
        has_class = False
        has_handle = False
        is_empty_shell = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "handle":
                        has_handle = True
                        # 检查 handle 是否为空壳 (仅包含 pass, return, docstring)
                        if len(item.body) <= 1:
                            if isinstance(item.body[0], (ast.Pass, ast.Return)):
                                is_empty_shell = True
                            elif isinstance(item.body[0], ast.Expr) and isinstance(item.body[0].value, ast.Constant):
                                is_empty_shell = True # Only docstring
                        
        if not has_class:
            return {"status": "error", "msg": "No class definition found"}
        if not has_handle:
            return {"status": "error", "msg": "No handle method found"}
        if is_empty_shell:
            return {"status": "warning", "msg": "Potential empty shell (handle method is trivial)"}
            
        return {"status": "ok", "msg": "Valid"}
        
    except Exception as e:
        return {"status": "error", "msg": f"Parse error: {str(e)}"}

def main():
    print(f"Scanning nodes in {NODES_DIR}...")
    if not os.path.exists(NODES_DIR):
        print(f"Error: {NODES_DIR} does not exist")
        return

    results = {"ok": [], "warning": [], "error": []}
    
    nodes = sorted([d for d in os.listdir(NODES_DIR) if os.path.isdir(os.path.join(NODES_DIR, d)) and d.startswith("Node_")])
    
    for node_dir in nodes:
        full_path = os.path.join(NODES_DIR, node_dir)
        res = check_node(full_path)
        results[res["status"]].append(f"{node_dir}: {res['msg']}")
        
    print("\n=== Audit Results ===")
    print(f"Total Nodes: {len(nodes)}")
    print(f"OK: {len(results['ok'])}")
    print(f"Warnings: {len(results['warning'])}")
    print(f"Errors: {len(results['error'])}")
    
    if results["error"]:
        print("\n[ERRORS]")
        for item in results["error"]:
            print(f"  - {item}")
            
    if results["warning"]:
        print("\n[WARNINGS]")
        for item in results["warning"]:
            print(f"  - {item}")

if __name__ == "__main__":
    main()
