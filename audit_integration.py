import os
import re
from pathlib import Path

def audit_integration():
    print("=== Cross-System Integration Assessment ===")
    
    backend_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    android_root = Path("/home/ubuntu/delivery/ufo-galaxy-android")
    
    # 1. Protocol Consistency Check
    print("1. Protocol Consistency Check:")
    
    # Check Backend Protocol
    api_routes = backend_root / "core/api_routes.py"
    backend_msgs = set()
    if api_routes.exists():
        with open(api_routes, 'r') as f:
            content = f.read()
            # Find message types handled in device_websocket
            matches = re.findall(r'msg_type\s*==\s*["\'](\w+)["\']', content)
            backend_msgs.update(matches)
            print(f"  Backend handles: {sorted(list(backend_msgs))}")
    else:
        print("  ❌ Backend api_routes.py MISSING!")

    # Check Android Protocol
    # Note: Android root is missing MainActivity, but we check WebSocketClient
    ws_client = android_root / "app/src/main/java/com/ufo/galaxy/network/WebSocketClient.kt"
    android_msgs = set()
    if ws_client.exists():
        with open(ws_client, 'r') as f:
            content = f.read()
            # Find message types sent or handled
            matches = re.findall(r'type["\']\s*:\s*["\'](\w+)["\']', content) # JSON construction
            matches2 = re.findall(r'type["\']\s*==\s*["\'](\w+)["\']', content) # Handling
            android_msgs.update(matches)
            android_msgs.update(matches2)
            print(f"  Android handles/sends: {sorted(list(android_msgs))}")
    else:
        print("  ❌ Android WebSocketClient.kt MISSING!")

    # Compare
    common = backend_msgs.intersection(android_msgs)
    print(f"  ✅ Common Protocol Messages: {sorted(list(common))}")
    
    missing_in_backend = android_msgs - backend_msgs
    if missing_in_backend:
        print(f"  ⚠️ Android sends/expects these, but Backend might not handle: {missing_in_backend}")
    
    missing_in_android = backend_msgs - android_msgs
    if missing_in_android:
        print(f"  ℹ️ Backend supports these, but Android might not use yet: {missing_in_android}")

    # 2. Port Consistency Check
    print("\n2. Port Consistency Check:")
    # Backend Port
    launcher = backend_root / "unified_launcher.py"
    backend_port = "Unknown"
    if launcher.exists():
        with open(launcher, 'r') as f:
            content = f.read()
            match = re.search(r'port\s*=\s*(\d+)', content)
            if match:
                backend_port = match.group(1)
                print(f"  Backend listens on: {backend_port}")
    
    # Android Port
    # Usually in Constants or MainActivity, let's check WebSocketClient for hardcoded URL or config
    android_port = "Unknown"
    if ws_client.exists():
        with open(ws_client, 'r') as f:
            content = f.read()
            # Look for ws://...:port
            match = re.search(r'ws://[\w\.]+[:](\d+)', content)
            if match:
                android_port = match.group(1)
                print(f"  Android connects to: {android_port}")
            else:
                print("  Android port not hardcoded in WebSocketClient (likely configurable).")

    if backend_port != "Unknown" and android_port != "Unknown":
        if backend_port == android_port:
            print("  ✅ Ports MATCH.")
        else:
            print(f"  ❌ Ports MISMATCH! Backend: {backend_port}, Android: {android_port}")

if __name__ == "__main__":
    audit_integration()
