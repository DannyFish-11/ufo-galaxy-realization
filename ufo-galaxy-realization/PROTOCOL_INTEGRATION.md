# UFO Galaxy 多协议整合架构 (Multi-Protocol Integration Architecture)

**版本**: v1.0
**日期**: 2026-02-07

## 1. 核心理念：统一网关 (Unified Gateway)

为了实现“多协议整合”，UFO Galaxy 采用 **Unified Gateway** 模式。无论设备通过何种物理协议（WebSocket, ADB, BLE, HTTP）连接，所有数据最终都会被标准化为内部的 `UniversalMessage` 格式，由 `unified_launcher.py` 进行统一路由和分发。

## 2. 协议分层架构

### 2.1 接入层 (Access Layer)
负责处理不同物理协议的连接维持和原始数据接收。

| 协议 | 端口/方式 | 适用场景 | 状态 |
| :--- | :--- | :--- | :--- |
| **WebSocket** | 8768 | **主干协议**。用于 Android/iOS 移动端、Web 前端的实时双向通信。 | ✅ 已就绪 |
| **ADB** | USB/TCP 5555 | **有线控制**。用于对 Android 设备进行高权限的底层控制（无需安装 App）。 | ✅ 已集成 |
| **HTTP/REST** | 8000 | **请求/响应**。用于外部系统调用、OneAPI 模型服务、一次性任务提交。 | ✅ 已就绪 |
| **BLE** | 蓝牙适配器 | **近场通信**。用于连接 IoT 传感器、智能穿戴设备。 | ⚠️ 需硬件 |
| **MQTT** | (已废弃) | 原计划用于弱网环境，现已由 WebSocket 取代。 | ❌ 已移除 |

### 2.2 转换层 (Translation Layer)
负责将异构协议的数据转换为标准格式。

*   **输入标准化**:
    *   WebSocket JSON -> `UniversalMessage`
    *   ADB Logcat -> `UniversalMessage` (Log 类型)
    *   HTTP POST Body -> `UniversalMessage` (Task 类型)
*   **输出标准化**:
    *   `UniversalMessage` -> WebSocket JSON
    *   `UniversalMessage` -> ADB Shell Command

### 2.3 路由层 (Routing Layer)
核心组件：`unified_launcher.py` 中的 `MessageRouter`。
*   根据 `target_id` 将消息分发给指定的节点 (Node) 或设备 (Device)。
*   支持广播 (Broadcast) 和组播 (Multicast)。

## 3. 整合现状与配置

### 3.1 Android 客户端
*   **当前模式**: 纯 WebSocket (端口 8768)。
*   **整合点**:
    *   启动时发送 `device_register` 消息。
    *   维持心跳 `heartbeat`。
    *   接收后端 `task` 指令（如 `click`, `screenshot`）。
    *   上报 `task_result`。

### 3.2 后端服务
*   **WebSocket Server**: 监听 8768，处理所有长连接。
*   **API Server**: 监听 8000，处理 HTTP 请求。
*   **Node System**: 内部通过 Python 对象调用或事件总线交互。

## 4. 未来扩展：WebRTC 整合
为了实现低延迟的屏幕流传输，计划在 WebSocket 通道建立后，通过 SDP 协商建立 WebRTC P2P 连接。
*   **信令通道**: 复用现有的 WebSocket (8768)。
*   **数据通道**: UDP 动态端口。

---
**Manus AI**
*构建万物互联的智能中枢*
