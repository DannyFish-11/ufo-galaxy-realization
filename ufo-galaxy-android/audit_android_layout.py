import os
import re
from pathlib import Path

def audit_android_layout():
    print("=== Audit: Android Phone/Tablet Adaptive Layout ===")
    
    android_root = Path("/home/ubuntu/delivery/ufo-galaxy-android")
    main_activity = android_root / "app/src/main/java/com/ufo/galaxy/ui/MainActivity.kt"
    
    if not main_activity.exists():
        print("❌ MainActivity.kt NOT found.")
        return

    with open(main_activity, 'r') as f:
        content = f.read()
        
        print("\n1. Checking for Window Size Class usage:")
        if "WindowWidthSizeClass" in content or "calculateWindowSizeClass" in content:
            print("  ✅ Uses WindowSizeClass for responsive layout.")
        else:
            print("  ⚠️ No explicit WindowSizeClass usage found.")

        print("\n2. Checking for Split Layouts (Tablet):")
        if "TwoPane" in content or "Row" in content and "Column" in content:
            # Simple heuristic: if it switches between Row and Column based on width
            if "width" in content and "dp" in content:
                 print("  ✅ Likely contains responsive logic (Row/Column switching).")
            else:
                 print("  ⚠️ Contains Row/Column but responsive logic unclear.")
        else:
            print("  ⚠️ No obvious split-pane or responsive layout structure found.")

        print("\n3. Checking for Tablet-specific resources:")
        # Check if there are values-sw600dp or similar folders
        res_dir = android_root / "app/src/main/res"
        tablet_res = list(res_dir.glob("values-sw*dp"))
        if tablet_res:
            print(f"  ✅ Found tablet-specific resource folders: {[d.name for d in tablet_res]}")
        else:
            print("  ⚠️ No 'values-sw600dp' (tablet) resource folders found.")

if __name__ == "__main__":
    audit_android_layout()
