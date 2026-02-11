# -*- coding: utf-8 -*-
import os
import ast
import sys

def get_imports_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
            
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def check_dependencies(nodes_dir="nodes", req_file="requirements.txt"):
    print(f"--- Starting Dependency Audit ---")
    
    # 1. Collect all imports from nodes
    all_imports = set()
    for root, dirs, files in os.walk(nodes_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                all_imports.update(get_imports_from_file(filepath))
                
    # Filter out standard library modules (approximate list)
    std_lib = sys.stdlib_module_names
    third_party_imports = {imp for imp in all_imports if imp not in std_lib}
    
    print(f"Found {len(third_party_imports)} potential third-party imports: {third_party_imports}")
    
    # 2. Read requirements.txt
    if not os.path.exists(req_file):
        print(f"❌ Missing requirements.txt")
        return
        
    with open(req_file, 'r', encoding='utf-8') as f:
        requirements = {line.strip().split('==')[0].split('>=')[0].lower() for line in f if line.strip() and not line.startswith('#')}
        
    # 3. Compare
    missing = []
    # Map import names to package names (common differences)
    package_map = {
        "PIL": "pillow",
        "cv2": "opencv-python",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4",
        "sklearn": "scikit-learn",
        "dotenv": "python-dotenv"
    }
    
    for imp in third_party_imports:
        pkg_name = package_map.get(imp, imp).lower()
        if pkg_name not in requirements:
            missing.append(f"{imp} (package: {pkg_name})")
            
    if missing:
        print(f"❌ Missing dependencies in requirements.txt:")
        for m in missing:
            print(f"  - {m}")
        
        # Auto-fix suggestion
        print("\nSuggested addition to requirements.txt:")
        for m in missing:
            pkg = m.split(": ")[1].replace(")", "") if ":" in m else m.split(" ")[0] # simple extraction
            # clean up
            if "package:" in m:
                 pkg = m.split("package: ")[1].replace(")", "")
            print(pkg)
    else:
        print("✅ All dependencies appear to be covered.")

if __name__ == "__main__":
    check_dependencies()
