# UFO Galaxy Android-Backend 集成指南

本文档详细说明如何将 UFO Galaxy Android 客户端与后端服务器进行集成和测试。

## 1. 架构概览

Android 客户端通过 WebSocket 协议与后端服务器进行实时全双工通信。

*   **协议**: WebSocket (ws/wss)
*   **默认端口**: 8768
*   **数据格式**: JSON (UniversalMessage)

## 2. 后端准备

确保后端服务已启动并监听 WebSocket 端口。

1.  进入后端项目目录：
    ```bash
    cd ufo-galaxy-realization
    ```

2.  启动统一启动器：
    ```bash
    python3 unified_launcher.py
    ```

3.  检查日志，确认 WebSocket 服务器已启动：
    ```
    INFO | UFO-Galaxy | WebSocket 服务器已启动: ws://0.0.0.0:8768
    ```

## 3. Android 客户端配置

1.  安装 APK 到 Android 设备。
2.  打开 App，进入设置页面。
3.  找到 **Gateway URL** 配置项。
4.  输入后端服务器的 IP 地址和端口，例如：
    ```
    ws://192.168.1.100:8768
    ```
    *注意：请确保手机和电脑在同一局域网内，或者服务器有公网 IP。*

5.  点击 **Save** 保存配置。

## 4. 连接测试

1.  在 Android App 主页，点击 **Start Agent Service**。
2.  观察后端控制台日志，应该能看到新的连接接入。
3.  如果连接成功，App 状态栏应显示 "Connected"。

## 5. 功能验证

### 5.1 远程截图
后端发送指令：
```json
{
  "type": "command",
  "target_id": "android_device_id",
  "payload": {
    "command": "capture_screen"
  }
}
```
预期结果：Android 端截取当前屏幕并上传。

### 5.2 自动化操作 (需开启无障碍服务)
后端发送指令：
```json
{
  "type": "task",
  "target_id": "android_device_id",
  "payload": {
    "action": "click",
    "x": 500,
    "y": 1000
  }
}
```
预期结果：Android 设备在坐标 (500, 1000) 处执行点击。

## 6. 故障排除

*   **连接失败**：
    *   检查防火墙是否允许 8768 端口。
    *   检查手机和电脑是否 ping 得通。
    *   尝试使用 `ws://echo.websocket.org` 测试手机网络。

*   **无障碍操作无效**：
    *   确保在 Android 系统设置中已开启 UFO Galaxy 的无障碍权限。
    *   部分国产 ROM (如小米、华为) 可能需要额外开启 "后台弹出界面" 权限。
