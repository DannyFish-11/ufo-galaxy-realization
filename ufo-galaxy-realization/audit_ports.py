# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import defaultdict

def audit_ports():
    config_file = Path("/home/ubuntu/delivery/ufo-galaxy-realization/node_dependencies.json")
    
    if not config_file.exists():
        print("Config file not found!")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    port_map = defaultdict(list)
    id_map = defaultdict(list)
    
    print("=== Scanning for Port and ID Conflicts ===")
    
    for node_name, info in config.get("nodes", {}).items():
        port = info.get("port")
        
        # Check 1: Port Conflict
        if port:
            port_map[port].append(node_name)
        else:
            print(f"[WARNING] Node {node_name} has NO port defined!")

        # Check 2: ID Logic (Node_XX)
        try:
            node_id = int(node_name.split('_')[1])
            id_map[node_id].append(node_name)
        except (IndexError, ValueError):
            print(f"[WARNING] Node {node_name} does not follow Node_XX naming convention!")

    # Report Port Conflicts
    conflict_found = False
    for port, nodes in port_map.items():
        if len(nodes) > 1:
            print(f"[CRITICAL] Port {port} is used by multiple nodes: {nodes}")
            conflict_found = True
            
    if not conflict_found:
        print("✅ No port conflicts found.")

    # Report ID Conflicts (Logical)
    id_conflict_found = False
    for nid, nodes in id_map.items():
        if len(nodes) > 1:
            print(f"[CRITICAL] ID {nid} is used by multiple nodes: {nodes}")
            id_conflict_found = True
            
    if not id_conflict_found:
        print("✅ No ID conflicts found.")

if __name__ == "__main__":
    audit_ports()
