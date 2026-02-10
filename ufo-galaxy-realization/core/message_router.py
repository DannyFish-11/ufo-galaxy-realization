"""
消息路由器 - 处理节点间的消息路由和分发
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """统一消息格式"""
    id: str
    source: str
    target: str
    type: str
    payload: Dict[str, Any]
    timestamp: str
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(**data)


class MessageRouter:
    """消息路由器"""
    
    def __init__(self):
        self.routes: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """注册消息处理器"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        if isinstance(self.handlers[message_type], list):
            self.handlers[message_type].append(handler)
        else:
            self.handlers[message_type] = [self.handlers[message_type], handler]
        logger.info(f"已注册消息处理器: {message_type}")
    
    def register_route(self, target: str, handler: Callable) -> None:
        """注册路由"""
        if target not in self.routes:
            self.routes[target] = []
        self.routes[target].append(handler)
        logger.info(f"已注册路由: {target}")
    
    async def route_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """路由消息"""
        try:
            # 首先尝试使用特定的路由
            if message.target in self.routes:
                for handler in self.routes[message.target]:
                    result = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                    if result:
                        return result
            
            # 然后尝试使用消息类型处理器
            if message.type in self.handlers:
                handlers = self.handlers[message.type]
                if not isinstance(handlers, list):
                    handlers = [handlers]
                
                for handler in handlers:
                    result = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                    if result:
                        return result
            
            logger.warning(f"未找到消息处理器: {message.type} -> {message.target}")
            return None
        
        except Exception as e:
            logger.error(f"消息路由失败: {e}")
            return None
    
    async def send_message(self, source: str, target: str, message_type: str, 
                          payload: Dict[str, Any], priority: int = 0) -> str:
        """发送消息"""
        message = Message(
            id=str(uuid.uuid4()),
            source=source,
            target=target,
            type=message_type,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            priority=priority
        )
        
        await self.message_queue.put(message)
        logger.debug(f"消息已入队: {message.id}")
        return message.id
    
    async def process_messages(self) -> None:
        """处理消息队列"""
        while True:
            try:
                message = await self.message_queue.get()
                result = await self.route_message(message)
                logger.debug(f"消息已处理: {message.id}")
            except Exception as e:
                logger.error(f"处理消息失败: {e}")


# 全局消息路由器实例
_message_router: Optional[MessageRouter] = None


def get_message_router() -> MessageRouter:
    """获取全局消息路由器"""
    global _message_router
    if _message_router is None:
        _message_router = MessageRouter()
    return _message_router


async def initialize_message_router() -> MessageRouter:
    """初始化消息路由器"""
    router = get_message_router()
    # 启动消息处理循环
    asyncio.create_task(router.process_messages())
    return router
