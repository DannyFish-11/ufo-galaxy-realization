# -*- coding: utf-8 -*-
from typing import Dict, Any

class BaseNode:
    """模拟 BaseNode，防止导入错误"""
    def __init__(self, node_id: str):
        self.node_id = node_id

class DummyNode(BaseNode):
    """
    通用占位符节点：用于填充尚未实现的节点，防止系统启动报错。
    """
    def __init__(self, node_id: str = "unknown"):
        self.node_id = node_id

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": False,
            "error": "Not Implemented",
            "message": f"Node {self.node_id} is currently a placeholder."
        }
