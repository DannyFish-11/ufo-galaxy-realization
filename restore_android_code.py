import shutil
from pathlib import Path

def restore_android():
    print("=== Restoring Android Code from Embedded to Standalone ===")
    
    # Source: Embedded Android Client
    src_root = Path("/home/ubuntu/delivery/ufo-galaxy-realization/android_client/app/src/main/java/com/ufo/galaxy")
    
    # Target: Standalone Android Client
    dst_root = Path("/home/ubuntu/delivery/ufo-galaxy-android/app/src/main/java/com/ufo/galaxy")
    
    if not src_root.exists():
        print(f"❌ Source directory not found: {src_root}")
        return
        
    if not dst_root.exists():
        print(f"❌ Target directory not found: {dst_root}")
        # Try to create it if parent exists
        if dst_root.parent.parent.parent.exists():
             dst_root.mkdir(parents=True, exist_ok=True)
             print("  Created target directory.")
        else:
             return

    # Files to restore
    files_to_copy = [
        "ui/MainActivity.kt",
        "ui/theme/Theme.kt",
        "ui/theme/Color.kt",
        "ui/theme/Type.kt",
        "network/WebSocketClient.kt", # Overwrite to ensure latest version
        "service/UFOAccessibilityService.kt"
    ]
    
    for rel_path in files_to_copy:
        src_file = src_root / rel_path
        dst_file = dst_root / rel_path
        
        if src_file.exists():
            # Ensure target dir exists
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_file, dst_file)
            print(f"✅ Restored: {rel_path}")
        else:
            print(f"⚠️ Source file missing: {rel_path}")

    print("\n=== Restoration Complete ===")

if __name__ == "__main__":
    restore_android()
