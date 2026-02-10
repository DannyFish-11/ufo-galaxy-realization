import os
from pathlib import Path

def audit_android():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-android")
    print(f"=== Deep Audit: Android Client ({root_dir}) ===")
    
    # 1. Project Structure
    if (root_dir / "build.gradle.kts").exists() or (root_dir / "build.gradle").exists():
        print("✅ Gradle build file exists.")
    else:
        print("❌ Gradle build file MISSING!")
        
    app_dir = root_dir / "app"
    if app_dir.exists():
        print("✅ 'app' module exists.")
    else:
        print("❌ 'app' module MISSING!")

    # 2. Core Code Check
    src_main = app_dir / "src/main/java/com/ufo/galaxy"
    if not src_main.exists():
        # Try finding where the package is
        src_main = list(app_dir.rglob("MainActivity.kt"))
        if src_main:
            src_main = src_main[0].parent
            print(f"⚠️ Found source code at non-standard path: {src_main}")
        else:
            print("❌ Source code directory not found!")
            return

    main_activity = src_main / "ui/MainActivity.kt"
    if main_activity.exists():
        print("✅ 'MainActivity.kt' exists.")
    else:
        print("❌ 'MainActivity.kt' MISSING!")

    ws_client = src_main / "network/WebSocketClient.kt"
    if ws_client.exists():
        print("✅ 'WebSocketClient.kt' exists.")
    else:
        print("❌ 'WebSocketClient.kt' MISSING!")
        
    service = src_main / "service/UFOAccessibilityService.kt"
    if service.exists():
        print("✅ 'UFOAccessibilityService.kt' exists.")
    else:
        print("❌ 'UFOAccessibilityService.kt' MISSING!")

    # 3. Manifest Check
    manifest = app_dir / "src/main/AndroidManifest.xml"
    if manifest.exists():
        print("✅ 'AndroidManifest.xml' exists.")
        with open(manifest, 'r') as f:
            content = f.read()
            if "android.permission.INTERNET" in content:
                print("  ✅ INTERNET permission declared.")
            else:
                print("  ⚠️ INTERNET permission MISSING!")
            
            if "BIND_ACCESSIBILITY_SERVICE" in content:
                print("  ✅ Accessibility Service declared.")
            else:
                print("  ⚠️ Accessibility Service declaration MISSING!")
    else:
        print("❌ 'AndroidManifest.xml' MISSING!")

if __name__ == "__main__":
    audit_android()
