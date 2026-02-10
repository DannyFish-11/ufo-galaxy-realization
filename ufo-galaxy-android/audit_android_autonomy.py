import os
import re

def audit_android_autonomy():
    print("=== Audit: Android Autonomy & Reverse Control ===")
    
    android_root = "/home/ubuntu/delivery/ufo-galaxy-android/app/src/main/java/com/ufo/galaxy"
    
    # 1. Check for User Input Interface (Chat/Command Input)
    # Does the UI allow the user to type commands?
    print("\n1. Checking for Command Input UI:")
    ui_files = []
    for root, dirs, files in os.walk(android_root):
        for file in files:
            if file.endswith(".kt") and "ui" in root:
                ui_files.append(os.path.join(root, file))
    
    has_input = False
    for f in ui_files:
        with open(f, 'r') as file:
            content = file.read()
            if "TextField" in content or "EditText" in content:
                print(f"  ✅ Found text input in {os.path.basename(f)}")
                has_input = True
    
    if not has_input:
        print("  ❌ No text input field found in UI. User cannot send commands.")

    # 2. Check for Reverse Control Logic (Sending Commands to PC)
    # Does the WebSocket client have a method to send 'task' or 'command'?
    print("\n2. Checking for Reverse Control Logic:")
    ws_file = os.path.join(android_root, "network/WebSocketClient.kt")
    try:
        with open(ws_file, 'r') as f:
            content = f.read()
            if 'send(' in content and ('"type": "command"' in content or '"type": "task"' in content):
                print("  ✅ Found logic to send commands/tasks to PC.")
            else:
                print("  ❌ No logic found to send 'command' or 'task' messages to PC.")
    except:
        print("  ❌ WebSocketClient.kt not found.")

    # 3. Check for Local Agent Logic (Autonomous Decision Making)
    # Is there any local LLM call or rule engine?
    print("\n3. Checking for Local Autonomy (Local Agent):")
    has_local_agent = False
    for root, dirs, files in os.walk(android_root):
        for file in files:
            if file.endswith(".kt"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    if "LLM" in content or "Agent" in content or "decision" in content:
                        print(f"  ⚠️ Found potential agent keyword in {file}, needs manual verification.")
                        has_local_agent = True
    
    if not has_local_agent:
        print("  ❌ No obvious local agent/decision logic found. It's likely a dumb terminal.")

if __name__ == "__main__":
    audit_android_autonomy()
