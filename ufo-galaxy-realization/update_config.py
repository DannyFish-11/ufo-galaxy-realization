# -*- coding: utf-8 -*-
import json
from pathlib import Path

def update_config():
    config_file = Path("/home/ubuntu/delivery/ufo-galaxy-realization/node_dependencies.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    new_nodes = {
        "Node_27_SmartHome": {"port": 8027, "group": "extended", "priority": 4, "description": "智能家居控制节点"},
        "Node_108_MetaCognition": {"port": 8108, "group": "academic", "priority": 5, "description": "元认知监控节点"},
        "Node_109_ProactiveSensing": {"port": 8109, "group": "academic", "priority": 5, "description": "主动感知节点"},
        "Node_116_ExternalToolWrapper": {"port": 8116, "group": "extended", "priority": 4, "description": "外部工具封装器"},
        "Node_117_OpenCode": {"port": 8117, "group": "development", "priority": 3, "description": "代码解释器节点"},
        "Node_118_NodeFactory": {"port": 8118, "group": "core", "priority": 2, "description": "节点工厂"},
        "Node_120_File": {"port": 8120, "group": "core", "priority": 2, "description": "文件系统操作节点 (Renamed from Node_12)"},
        "Node_121_Web": {"port": 8121, "group": "development", "priority": 3, "description": "Web服务节点 (Renamed from Node_13)"},
        "Node_122_Shell": {"port": 8122, "group": "development", "priority": 3, "description": "Shell命令执行节点 (Renamed from Node_14)"},
        "Node_123_AutonomousLearning": {"port": 8123, "group": "academic", "priority": 5, "description": "自主学习节点 (Renamed from Node_70)"},
        "Node_124_MultiDeviceCoordination": {"port": 8124, "group": "extended", "priority": 4, "description": "多设备协同节点 (Renamed from Node_71)"}
    }
    
    added_count = 0
    for name, info in new_nodes.items():
        if name not in config["nodes"]:
            # 补充默认字段
            info["dependencies"] = ["Node_01_OneAPI"]
            info["optional_dependencies"] = []
            config["nodes"][name] = info
            added_count += 1
            print(f"Added {name}")
            
    if added_count > 0:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Successfully added {added_count} nodes to config.")
    else:
        print("No new nodes to add.")

if __name__ == "__main__":
    update_config()
