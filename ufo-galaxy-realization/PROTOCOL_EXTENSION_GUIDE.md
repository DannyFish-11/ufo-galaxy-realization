# UFO Galaxy 协议扩展白皮书 (Protocol Extension Whitepaper)

**版本**: v1.0
**日期**: 2026-02-07

## 1. 为什么需要协议扩展？

物联网世界是碎片化的。除了标准的 WebSocket 和 HTTP，您可能会遇到：
*   **工业现场**: Modbus, CAN Bus, PLC 协议
*   **智能家居**: Zigbee, Z-Wave, Matter
*   **老旧设备**: RS232/RS485 串口通信
*   **私有硬件**: 厂商自定义的二进制协议

UFO Galaxy 不可能预置所有协议，因此我们提供了 **Protocol-as-a-Node (PaaN)** 架构，让您能够像搭积木一样添加新协议。

## 2. 核心架构：BaseProtocolNode

所有新协议适配器都继承自 `nodes/BaseProtocolNode.py`。您只需要实现三个核心方法：

1.  `connect(config)`: 如何建立物理连接（打开串口、连接蓝牙等）。
2.  `send(target, data)`: 如何将 JSON 指令打包成设备的二进制格式并发送。
3.  `receive()`: 如何从设备读取数据。
4.  `normalize_message(raw)`: **(关键)** 如何将设备的“方言”翻译成系统的“普通话” (UniversalMessage)。

## 3. 实战示例：添加一个自定义串口设备

假设您有一个通过 USB 串口连接的温度传感器，它每秒发送格式为 `TEMP:25.5\n` 的 ASCII 字符串。

### 步骤 1: 创建节点文件
在 `nodes/` 目录下创建 `Node_99_SerialTemp.py`：

```python
from .BaseProtocolNode import BaseProtocolNode
import serial

class Node_99_SerialTemp(BaseProtocolNode):
    def __init__(self):
        super().__init__("99", "SerialTemp")
        self.ser = None

    def connect(self, config):
        port = config.get("port", "/dev/ttyUSB0")
        baud = config.get("baud", 9600)
        try:
            self.ser = serial.Serial(port, baud)
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def receive(self):
        if self.ser and self.ser.in_waiting:
            line = self.ser.readline()
            return line # 返回原始字节
        return None

    def normalize_message(self, raw_data):
        # 重写解析逻辑
        try:
            text = raw_data.decode('utf-8').strip()
            if text.startswith("TEMP:"):
                temp_val = float(text.split(":")[1])
                return {
                    "type": "sensor_data",
                    "sensor": "temperature",
                    "value": temp_val,
                    "unit": "C"
                }
        except:
            pass
        return {"type": "unknown", "raw": str(raw_data)}
```

### 步骤 2: 注册节点
在 `unified_launcher.py` 的节点列表中添加 `Node_99_SerialTemp`。

### 步骤 3: 运行
系统会自动启动该节点，您将在控制台看到标准化的温度数据流：
`{"type": "sensor_data", "value": 25.5, ...}`

## 4. AI 驱动的未知协议解析 (AI-Powered Parsing)

如果您面对的是一个完全未知的二进制协议，可以使用 `ai_parse_unknown_protocol` 方法。
系统会将截获的 Hex 数据流发送给内置的 LLM（如 DeepSeek/GPT-4），让 AI 尝试逆向分析协议结构。

**示例调用**:
```python
# 在 normalize_message 中
if unknown_format:
    return self.ai_parse_unknown_protocol(raw_bytes, context_hint="Smart Light Bulb Control")
```

---
**Manus AI**
*连接未知的世界*
