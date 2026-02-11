# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

def audit_task_routing():
    print("=== Audit: Distributed Task Routing Logic ===")
    
    backend_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    orchestrator_path = backend_root / "nodes/Node_110_SmartOrchestrator/main.py"
    
    if not orchestrator_path.exists():
        print("❌ SmartOrchestrator NOT found.")
        return

    with open(orchestrator_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        print("\n1. Checking for Device Selection Logic:")
        # Look for logic that iterates over connected devices
        if "connected_devices" in content or "device_registry" in content:
            print("  ✅ Orchestrator references a device list.")
        else:
            print("  ⚠️ Orchestrator does NOT seem to reference a device list directly.")

        print("\n2. Checking for Capability-based Routing:")
        # Look for capability checks
        if "capabilities.get" in content or "['is_tablet']" in content:
            print("  ✅ Orchestrator checks specific capabilities (e.g., is_tablet).")
        else:
            print("  ⚠️ Orchestrator does NOT seem to filter devices by capability (e.g., is_tablet).")
            
        print("\n3. Checking for Task Dispatch:")
        # Look for sending commands to devices
        if "send_command" in content or "dispatch_task" in content:
            print("  ✅ Orchestrator has task dispatch logic.")
        else:
            print("  ⚠️ Orchestrator task dispatch logic is unclear.")

if __name__ == "__main__":
    audit_task_routing()
