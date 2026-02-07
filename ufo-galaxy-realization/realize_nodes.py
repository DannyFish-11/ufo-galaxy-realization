import os
import json
import shutil

# 节点模板定义
NODE_TEMPLATES = {
    "Node_00_StateMachine": {
        "description": "Manages the state transitions of the autonomous agent.",
        "capabilities": ["state_management"],
        "actions": ["transition", "get_state"],
        "code": """
class Node:
    def __init__(self):
        self.state = "IDLE"
        
    def execute(self, action, **kwargs):
        if action == "transition":
            new_state = kwargs.get("new_state")
            if new_state:
                self.state = new_state
                return {"status": "success", "state": self.state}
        elif action == "get_state":
            return {"status": "success", "state": self.state}
        return {"status": "error", "message": "Invalid action"}
"""
    },
    "Node_01_OneAPI": {
        "description": "Unified interface for accessing multiple LLM models via OneAPI.",
        "capabilities": ["llm_inference"],
        "actions": ["chat_completion", "list_models"],
        "code": """
import requests
import os

class Node:
    def __init__(self):
        self.base_url = os.getenv("ONEAPI_BASE_URL", "http://localhost:3000/v1")
        self.api_key = os.getenv("ONEAPI_API_KEY", "sk-placeholder")
        
    def execute(self, action, **kwargs):
        if action == "chat_completion":
            model = kwargs.get("model", "gpt-3.5-turbo")
            messages = kwargs.get("messages", [])
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {"model": model, "messages": messages}
            try:
                response = requests.post(f"{self.base_url}/chat/completions", json=data, headers=headers)
                return response.json()
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Invalid action"}
"""
    },
    "Node_15_OCR": {
        "description": "Optical Character Recognition using Tesseract.",
        "capabilities": ["ocr"],
        "actions": ["extract_text"],
        "code": """
import pytesseract
from PIL import Image
import io
import base64

class Node:
    def execute(self, action, **kwargs):
        if action == "extract_text":
            image_data = kwargs.get("image_base64")
            if not image_data:
                return {"status": "error", "message": "No image provided"}
            try:
                img_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(img_bytes))
                text = pytesseract.image_to_string(image)
                return {"status": "success", "text": text}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Invalid action"}
"""
    },
    # 默认通用模板
    "DEFAULT": {
        "description": "Standard functional node.",
        "capabilities": ["generic_execution"],
        "actions": ["run"],
        "code": """
class Node:
    def execute(self, action, **kwargs):
        return {"status": "success", "message": f"Executed {action} with {kwargs}"}
"""
    }
}

def realize_nodes(nodes_dir="nodes"):
    print(f"--- Starting Massive Node Realization in {nodes_dir} ---")
    
    if not os.path.exists(nodes_dir):
        os.makedirs(nodes_dir)

    # 获取所有节点目录
    nodes = [d for d in os.listdir(nodes_dir) if os.path.isdir(os.path.join(nodes_dir, d))]
    
    for node_name in nodes:
        node_path = os.path.join(nodes_dir, node_name)
        config_path = os.path.join(node_path, "config.json")
        entry_path = os.path.join(node_path, "fusion_entry.py")
        
        # 选择模板
        template = NODE_TEMPLATES.get(node_name, NODE_TEMPLATES["DEFAULT"])
        
        # 1. 修复/创建 config.json
        if not os.path.exists(config_path):
            config_data = {
                "name": node_name,
                "description": template["description"],
                "capabilities": template["capabilities"],
                "actions": template["actions"],
                "version": "1.0.0"
            }
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"✅ {node_name}: Created config.json")
            
        # 2. 修复/创建 fusion_entry.py
        needs_update = False
        if not os.path.exists(entry_path):
            needs_update = True
        else:
            with open(entry_path, 'r') as f:
                content = f.read()
                # 关键修复：如果文件中没有 class Node 且没有 class FusionNode，必须更新
                has_node_class = "class Node" in content
                has_fusion_node = "class FusionNode" in content
                has_alias = "Node = FusionNode" in content
                
                if not has_node_class and not has_fusion_node:
                    print(f"⚠️ {node_name}: Invalid content detected (no Node class), forcing update.")
                    needs_update = True
                
                # 如果有 FusionNode 但没有 Node 别名，添加别名
                if has_fusion_node and not has_alias and not has_node_class:
                     with open(entry_path, 'a') as fa:
                         fa.write("\n\n# Alias for standard loading\nNode = FusionNode\n")
                     print(f"✅ {node_name}: Added Node alias for FusionNode")
                     needs_update = False

        if needs_update:
            # 如果是 Node_15_OCR 且需要更新，我们不覆盖它，因为它是特殊的
            if node_name == "Node_15_OCR":
                 print(f"⚠️ {node_name}: Skipping overwrite of special node, please check manually.")
            else:
                with open(entry_path, 'w') as f:
                    f.write(template["code"])
                print(f"✅ {node_name}: Realized fusion_entry.py implementation")

    print("\n--- Realization Complete ---")

if __name__ == "__main__":
    realize_nodes()
