import os
import re
from pathlib import Path

def audit_ufo_integration():
    print("=== Audit: Microsoft UFO Framework Integration ===")
    
    backend_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    
    # 1. Check for Core UFO Concepts (AppAgent, WinAgent, Session)
    # We'll scan all python files for these keywords
    
    keywords = ["AppAgent", "WinAgent", "Session", "Step", "ControlInteraction", "HostAgent"]
    found_keywords = {k: [] for k in keywords}
    
    print("\n1. Scanning for UFO Core Concepts:")
    for root, dirs, files in os.walk(backend_root):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for k in keywords:
                            if k in content:
                                found_keywords[k].append(str(path.relative_to(backend_root)))
                except Exception as e:
                    pass

    for k, paths in found_keywords.items():
        if paths:
            print(f"  ✅ Found '{k}' in {len(paths)} files (e.g., {paths[0]})")
        else:
            print(f"  ❌ '{k}' NOT found in any file.")

    # 2. Check for UI Tree Parsing Logic (UFO's core capability)
    print("\n2. Checking for UI Tree Parsing Logic:")
    ui_keywords = ["print_tree", "find_element", "control_info", "uiautomation"]
    found_ui = False
    for root, dirs, files in os.walk(backend_root):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if any(uk in content for uk in ui_keywords):
                            print(f"  ✅ Found UI automation logic in {path.relative_to(backend_root)}")
                            found_ui = True
                            break
                except: pass
        if found_ui: break
    
    if not found_ui:
        print("  ❌ No obvious UI Tree parsing logic found (UFO core missing?).")

    # 3. Check for Session/Step Management
    # UFO manages tasks in Sessions and Steps
    print("\n3. Checking for Session/Step Management:")
    if found_keywords["Session"] and found_keywords["Step"]:
        print("  ✅ Session and Step management logic appears to be present.")
    else:
        print("  ⚠️ Session/Step logic might be missing or renamed.")

if __name__ == "__main__":
    audit_ufo_integration()
