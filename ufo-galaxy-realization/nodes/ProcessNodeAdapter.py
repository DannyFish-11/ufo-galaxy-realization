import subprocess
import sys
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("ProcessNodeAdapter")

class ProcessNodeAdapter:
    """
    适配器：将独立进程节点（如 Node 00, Node 33）适配为 unified_launcher 可管理的节点。
    """
    def __init__(self, node_path: str, node_id: str):
        self.node_path = node_path
        self.node_id = node_id
        self.process = None

    def start(self):
        """启动独立节点进程"""
        main_py = os.path.join(self.node_path, "main.py")
        if not os.path.exists(main_py):
            logger.error(f"Node {self.node_id} main.py not found at {main_py}")
            return False

        try:
            self.process = subprocess.Popen(
                [sys.executable, main_py],
                cwd=self.node_path,
                env={**os.environ, "PYTHONPATH": os.getcwd()}
            )
            logger.info(f"Node {self.node_id} started (PID: {self.process.pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to start Node {self.node_id}: {e}")
            return False

    def stop(self):
        """停止节点进程"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            logger.info(f"Node {self.node_id} stopped")

    def handle(self, message: Dict[str, Any]):
        """
        转发消息到节点（通常通过 HTTP 或 IPC，这里简化为日志）
        注意：独立节点通常有自己的 API，不通过 handle 调用。
        """
        logger.warning(f"Node {self.node_id} is a standalone process. Use its API directly.")
        return {"error": "Use node API directly"}
