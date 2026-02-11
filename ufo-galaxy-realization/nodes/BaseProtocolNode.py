# -*- coding: utf-8 -*-
import abc
import json
import logging
from typing import Any, Dict, Optional

class BaseProtocolNode(abc.ABC):
    """
    万能协议适配节点基类 (Universal Protocol Adapter Node)
    
    所有新协议（如 Bluetooth, Zigbee, Serial, Modbus）都应继承此类。
    该类负责将特定协议的原始数据转换为系统通用的 UniversalMessage。
    """
    
    def __init__(self, node_id: str, protocol_name: str):
        self.node_id = node_id
        self.protocol_name = protocol_name
        self.logger = logging.getLogger(f"ProtocolNode_{protocol_name}")
        self.is_active = False

    @abc.abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到物理设备或协议网关
        :param config: 连接配置（如 IP, 端口, 波特率, UUID）
        :return: 连接是否成功
        """
        pass

    @abc.abstractmethod
    def send(self, target_id: str, data: Any) -> bool:
        """
        发送数据到设备
        :param target_id: 目标设备 ID
        :param data: 要发送的数据（通常是 UniversalMessage 的 payload）
        :return: 发送是否成功
        """
        pass

    @abc.abstractmethod
    def receive(self) -> Optional[Dict[str, Any]]:
        """
        从设备接收数据（阻塞或轮询）
        :return: 接收到的原始数据，如果无数据则返回 None
        """
        pass

    def normalize_message(self, raw_data: Any) -> Dict[str, Any]:
        """
        将协议特定的原始数据转换为 UniversalMessage 格式
        默认实现假设 raw_data 已经是 JSON 兼容的字典，子类应重写此方法以处理二进制流。
        """
        try:
            if isinstance(raw_data, bytes):
                # 尝试解码为 UTF-8 字符串
                decoded = raw_data.decode('utf-8')
                return json.loads(decoded)
            return raw_data
        except Exception as e:
            self.logger.error(f"Failed to normalize message: {e}")
            return {
                "type": "raw_error",
                "protocol": self.protocol_name,
                "raw_hex": raw_data.hex() if isinstance(raw_data, bytes) else str(raw_data)
            }

    def ai_parse_unknown_protocol(self, raw_bytes: bytes, context_hint: str = "") -> Dict[str, Any]:
        """
        [高级功能] 使用 AI 解析未知协议的二进制流
        当遇到无法解析的私有协议时，调用此方法将 Hex 流发送给 LLM 进行分析。
        """
        # 这里是伪代码，实际集成时会调用 OneAPI 节点
        prompt = f"""
        Analyze this raw hex stream from a {self.protocol_name} device: {raw_bytes.hex()}
        Context: {context_hint}
        Extract meaningful fields (e.g., temperature, status, error code) into JSON.
        """
        self.logger.info(f"Delegating protocol parsing to AI: {prompt}")
        # TODO: Call Node_58_ModelRouter
        return {"type": "ai_parsing_pending", "raw": raw_bytes.hex()}

    def start_listening(self, message_router_callback):
        """
        启动监听循环，将接收到的数据标准化后转发给 MessageRouter
        """
        self.is_active = True
        while self.is_active:
            raw_data = self.receive()
            if raw_data:
                universal_msg = self.normalize_message(raw_data)
                # 注入源信息
                universal_msg["source_protocol"] = self.protocol_name
                universal_msg["source_node"] = self.node_id
                message_router_callback(universal_msg)
