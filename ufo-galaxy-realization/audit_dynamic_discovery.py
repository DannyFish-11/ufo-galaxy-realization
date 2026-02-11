# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

def audit_dynamic_discovery():
    print("=== Audit: Dynamic Node Discovery & Capability Registration ===")
    
    backend_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    
    # 1. Check if Orchestrator supports dynamic registration
    orchestrator_path = backend_root / "nodes/Node_110_SmartOrchestrator/main.py"
    api_routes_path = backend_root / "core/api_routes.py"
    
    print("\n1. Checking Dynamic Registration Logic:")
    
    if api_routes_path.exists():
        with open(api_routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for device_register handling
            if "device_register" in content and "capabilities" in content:
                print("  ✅ api_routes.py handles 'device_register' and extracts 'capabilities'.")
                
                # Check if it stores this info in a global registry
                if "connected_devices" in content or "device_registry" in content:
                    print("  ✅ Device registry mechanism found.")
                else:
                    print("  ⚠️ Device registry mechanism NOT clearly found in api_routes.py.")
            else:
                print("  ❌ api_routes.py missing 'device_register' or 'capabilities' extraction.")
    else:
        print("  ❌ api_routes.py NOT found.")

    # 2. Check if Orchestrator uses these capabilities
    if orchestrator_path.exists():
        with open(orchestrator_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check if it queries the registry
            if "get_device_capabilities" in content or "select_device" in content:
                print("  ✅ Orchestrator has logic to query device capabilities.")
            else:
                print("  ⚠️ Orchestrator might not be using dynamic capabilities for routing (needs manual check).")
    else:
        print("  ❌ SmartOrchestrator NOT found.")

    # 3. Check Android Capability Declaration
    print("\n2. Checking Android Capability Declaration:")
    android_ws_client = Path("/home/ubuntu/delivery/ufo-galaxy-android/app/src/main/java/com/ufo/galaxy/network/WebSocketClient.kt")
    
    if android_ws_client.exists():
        with open(android_ws_client, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check what capabilities are sent
            caps_match = re.search(r'put\("capabilities",\s*JSONObject\(\)\.apply\s*\{(.*?)\}\)', content, re.DOTALL)
            if caps_match:
                caps = caps_match.group(1)
                print(f"  ✅ Android declares capabilities:\n{caps}")
                
                # Check for dynamic capability detection (e.g., isTablet, hasCamera)
                if "isTablet" in content or "screenSize" in content:
                    print("  ✅ Android sends device form factor info.")
                else:
                    print("  ⚠️ Android sends HARDCODED capabilities. Does not distinguish Phone vs Tablet dynamically.")
            else:
                print("  ❌ Android does NOT send capabilities object.")
    else:
        print("  ❌ Android WebSocketClient.kt NOT found.")

if __name__ == "__main__":
    audit_dynamic_discovery()
