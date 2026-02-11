# -*- coding: utf-8 -*-
import os
from pathlib import Path

def fix_ghost_references():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    
    # Mapping: Old Name -> New Name
    replacements = {
        "Node_125_Time": "Node_125_Time",
        "Node_126_Serial": "Node_126_Serial",
        "Node_127_Planning": "Node_127_Planning",
        "Node_120_File": "Node_120_File",
        "Node_121_Web": "Node_121_Web",
        "Node_122_Shell": "Node_122_Shell",
        "Node_123_AutonomousLearning": "Node_123_AutonomousLearning",
        "Node_124_MultiDeviceCoordination": "Node_124_MultiDeviceCoordination"
    }
    
    print("=== Fixing Ghost References ===")
    
    count = 0
    for py_file in root_dir.rglob("*.py"):
        if "venv" in str(py_file): continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            modified = False
            
            for old, new in replacements.items():
                if old in new_content:
                    new_content = new_content.replace(old, new)
                    modified = True
                    print(f"Fixed {old} -> {new} in {py_file.name}")
            
            if modified:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
            
    print(f"Fixed references in {count} files.")

if __name__ == "__main__":
    fix_ghost_references()
