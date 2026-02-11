# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

def audit_android_resources():
    android_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization/android_client/app/src/main")
    java_src = android_root / "java"
    res_dir = android_root / "res"
    
    print("=== Scanning for Android Resource Consistency ===")
    
    if not java_src.exists() or not res_dir.exists():
        print("[CRITICAL] Android source or resource directory not found!")
        return

    # 1. Extract R.id.xxx usages from Kotlin/Java files
    used_ids = set()
    for kt_file in java_src.rglob("*.kt"):
        with open(kt_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = re.findall(r'R\.id\.([a-zA-Z0-9_]+)', content)
            used_ids.update(matches)
            
    print(f"Found {len(used_ids)} unique R.id references in code.")

    # 2. Extract android:id="@+id/xxx" definitions from XML files
    defined_ids = set()
    for xml_file in res_dir.rglob("*.xml"):
        with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = re.findall(r'android:id="@\+id/([a-zA-Z0-9_]+)"', content)
            defined_ids.update(matches)
            
    print(f"Found {len(defined_ids)} unique ID definitions in XML.")

    # 3. Compare
    missing_ids = used_ids - defined_ids
    
    if missing_ids:
        print(f"\n[CRITICAL] The following IDs are used in code but NOT defined in XML (Will Crash):")
        for mid in sorted(missing_ids):
            print(f"- {mid}")
    else:
        print("\n✅ All referenced IDs are defined in XML.")

if __name__ == "__main__":
    audit_android_resources()
