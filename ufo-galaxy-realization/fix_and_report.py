# -*- coding: utf-8 -*-
import os
import json
import shutil
from pathlib import Path

def fix_and_report():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    nodes_dir = root_dir / "nodes"
    config_file = root_dir / "node_dependencies.json"
    
    print("=== Executing Final Fixes ===")

    # 1. Fix ID Conflicts
    conflicts = {
        "Node_125_Time": "Node_125_Time",
        "Node_126_Serial": "Node_126_Serial",
        "Node_127_Planning": "Node_127_Planning"
    }
    
    fixed_count = 0
    for old_name, new_name in conflicts.items():
        old_path = nodes_dir / old_name
        new_path = nodes_dir / new_name
        
        if old_path.exists():
            print(f"Renaming {old_name} -> {new_name}")
            shutil.move(str(old_path), str(new_path))
            fixed_count += 1
            
            # Update Config
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if old_name in config["nodes"]:
                config["nodes"][new_name] = config["nodes"].pop(old_name)
                # Update port if needed (simple increment for now)
                config["nodes"][new_name]["port"] = 8100 + int(new_name.split('_')[1])
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed {fixed_count} ID conflicts.")

    # 2. Generate requirements.txt
    # (Using the list from previous audit)
    missing_deps = [
        'sentence_transformers', 'qdrant_client', 'networkx', 'vosk', 'edge_tts', 
        'ollama', 'jieba', 'pymilvus', 'ultralytics', 'einops', 'azure-identity', 
        'azure-cognitiveservices-speech', 'alibabacloud_tea_openapi', 'volcengine', 
        'dashscope', 'msal', 'oss2', 'pywinauto', 'keyboard', 'PyQt6', 'pika', 
        'psycopg2-binary', 'paho-mqtt', 'tenacity', 'cachetools', 'html2text', 
        'schedule', 'icecream', 'PyJWT', 'requests', 'fastapi', 'uvicorn', 
        'websockets', 'pydantic', 'python-dotenv', 'numpy', 'pandas', 'pillow', 
        'beautifulsoup4', 'openai', 'anthropic', 'groq', 'zhipuai'
    ]
    
    req_path = root_dir / "requirements.txt"
    with open(req_path, 'w') as f:
        for dep in sorted(missing_deps):
            f.write(f"{dep}\n")
            
    print(f"Generated requirements.txt with {len(missing_deps)} dependencies.")

if __name__ == "__main__":
    fix_and_report()
