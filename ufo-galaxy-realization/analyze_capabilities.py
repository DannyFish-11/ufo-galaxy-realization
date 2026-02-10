import json
from pathlib import Path
from collections import defaultdict

def analyze_capabilities():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    config_file = root_dir / "node_dependencies.json"
    
    if not config_file.exists():
        print("Config file not found!")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    nodes = config.get("nodes", {})
    
    # 1. Capability Categorization
    categories = defaultdict(list)
    
    # Keywords for categorization
    keywords = {
        "AI/LLM": ["llm", "gpt", "claude", "qwen", "deepseek", "model", "inference", "embedding", "rag", "vector"],
        "Perception": ["ocr", "vision", "camera", "audio", "speech", "tts", "stt", "listen", "watch"],
        "Control/Action": ["adb", "serial", "mouse", "keyboard", "click", "type", "automation", "control"],
        "Knowledge/Data": ["search", "knowledge", "graph", "memory", "database", "sql", "file", "notion"],
        "Dev/Tools": ["git", "github", "code", "debug", "shell", "docker", "sandbox", "api"],
        "System/Core": ["router", "auth", "config", "monitor", "schedule", "state", "orchestrator"]
    }
    
    print("=== UFO Galaxy Capability Analysis ===")
    
    for name, info in nodes.items():
        desc = info.get("description", "").lower()
        name_lower = name.lower()
        
        assigned = False
        for cat, keys in keywords.items():
            if any(k in desc or k in name_lower for k in keys):
                categories[cat].append(name)
                assigned = True
                # Don't break, a node can belong to multiple categories
        
        if not assigned:
            categories["Other/Utility"].append(name)

    # 2. Report Capabilities
    for cat, node_list in sorted(categories.items()):
        print(f"\n[{cat}] ({len(node_list)} Nodes)")
        for node in sorted(node_list):
            desc = nodes[node].get("description", "No description")
            # Truncate description
            if len(desc) > 60: desc = desc[:57] + "..."
            print(f"  - {node:<30} : {desc}")

    # 3. Connectivity (Dependency Graph)
    print("\n=== Core Connectivity Hubs ===")
    # Find nodes that are dependencies of many other nodes
    dependency_counts = defaultdict(int)
    for name, info in nodes.items():
        for dep in info.get("dependencies", []):
            dependency_counts[dep] += 1
            
    sorted_hubs = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)
    for hub, count in sorted_hubs[:5]:
        print(f"  - {hub}: Used by {count} nodes (Central Hub)")

if __name__ == "__main__":
    analyze_capabilities()
