import os

def audit_p2p_control():
    print("=== Audit: Peer-to-Peer (P2P) Control Logic ===")
    
    android_root = "/home/ubuntu/delivery/ufo-galaxy-android/app/src/main/java/com/ufo/galaxy"
    
    # 1. Check for mDNS / NSD (Network Service Discovery)
    # This is the standard way for Android devices to find each other on LAN
    print("\n1. Checking for Device Discovery (mDNS/NSD):")
    has_nsd = False
    for root, dirs, files in os.walk(android_root):
        for file in files:
            if file.endswith(".kt"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    if "NsdManager" in content or "SERVICE_TYPE" in content or "_http._tcp" in content:
                        print(f"  ✅ Found NSD/mDNS logic in {file}")
                        has_nsd = True
    
    if not has_nsd:
        print("  ❌ No Network Service Discovery (NSD) logic found. Devices cannot find each other directly.")

    # 2. Check for Direct Socket/HTTP Server
    # Does the Android app run a server to accept incoming P2P connections?
    print("\n2. Checking for Local Server (ServerSocket/HttpServer):")
    has_server = False
    for root, dirs, files in os.walk(android_root):
        for file in files:
            if file.endswith(".kt"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    if "ServerSocket" in content or "NanoHTTPD" in content or "Ktor" in content:
                        print(f"  ✅ Found local server logic in {file}")
                        has_server = True
    
    if not has_server:
        print("  ❌ No local server logic found. Device cannot accept direct P2P commands.")

if __name__ == "__main__":
    audit_p2p_control()
