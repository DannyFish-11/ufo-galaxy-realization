# -*- coding: utf-8 -*-
import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger("scheduler")

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class AutonomousScheduler:
    def __init__(self, llm_manager: Any, nodes_dir: str = "nodes"):
        self.llm_manager = llm_manager
        self.nodes_dir = nodes_dir
        self.tools_cache: List[Dict[str, Any]] = []
        self._load_tools()

    def register_tool(self, name: str, node_instance: Any):
        """手动注册工具（用于测试或动态添加）"""
        description = f"Execute actions on node {name}"
        # 尝试从节点实例获取描述
        if hasattr(node_instance, "description"):
             description = node_instance.description
        
        tool = {
            "type": "function",
            "function": {
                "name": f"call_{name}",
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform"
                        },
                        "params": {
                            "type": "object",
                            "description": "Parameters for the action"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
        self.tools_cache.append(tool)

    def _load_tools(self):
        """从节点配置中加载工具定义"""
        self.tools_cache = []
        if not os.path.isdir(self.nodes_dir):
            logger.warning(f"节点目录不存在: {self.nodes_dir}")
            return

        for name in sorted(os.listdir(self.nodes_dir)):
            node_dir = os.path.join(self.nodes_dir, name)
            config_file = os.path.join(node_dir, "config.json")
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        
                    # 提取节点能力作为工具
                    description = config.get("description", f"Execute actions on node {name}")
                    
                    tool = {
                        "type": "function",
                        "function": {
                            "name": f"call_{name}",
                            "description": description,
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "description": "The action to perform"
                                    },
                                    "params": {
                                        "type": "object",
                                        "description": "Parameters for the action"
                                    }
                                },
                                "required": ["action"]
                            }
                        }
                    }
                    self.tools_cache.append(tool)
                except Exception as e:
                    logger.error(f"加载节点 {name} 配置失败: {e}")

    def get_tools(self) -> List[Dict[str, Any]]:
        return self.tools_cache

    async def plan_and_execute(self, instruction: str, context: Dict[str, Any] = None, max_turns: int = 5) -> Dict[str, Any]:
        """
        核心调度逻辑 (ReAct Loop)
        """
        # 1. 构建动态设备上下文
        device_context = "No devices connected."
        if context and "devices" in context:
            devices = context["devices"]
            if devices:
                device_list_str = "\n".join([
                    f"- Device ID: {d['device_id']}, Name: {d.get('device_name', 'Unknown')}, Type: {d.get('device_type', 'android')}, Capabilities: {d.get('capabilities', [])}"
                    for d in devices.values()
                ])
                device_context = f"Connected Devices (Treat these as available hardware nodes):\n{device_list_str}"

        system_prompt = f"""You are the central scheduler of the UFO Galaxy system. 
Your goal is to satisfy the user's request by autonomously calling the available node tools.
You operate in a ReAct (Reasoning + Acting) loop. You can call tools, observe their output, and then decide the next step.

CRITICAL: "Device-as-Node" Protocol
You have access to real-time connected hardware devices. 
When the user's instruction implies using a specific device (e.g., "use the phone", "take a photo", "check battery"), 
you MUST:
1. Analyze the 'Connected Devices' list below.
2. Select the most appropriate 'device_id' based on capabilities and name.
3. Use the 'call_Node_82_NetworkGuard' or generic 'send_task' tool to target that specific device.

{device_context}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        executed_steps = []
        final_reply = ""

        try:
            for turn in range(max_turns):
                logger.info(f"ReAct Loop Turn {turn+1}/{max_turns}")
                
                # 调用 LLM Manager
                response = await self.llm_manager.chat_completion(
                    messages=messages,
                    tools=self.tools_cache,
                    tool_choice="auto"
                )
                
                # 处理 Mock 返回或真实返回
                if isinstance(response, dict):
                     # Mock response structure handling if needed
                     pass
                
                message = response.choices[0].message
                messages.append(message) # 将 LLM 的回复追加到历史
                
                tool_calls = message.tool_calls
                
                if not tool_calls:
                    # LLM 认为任务已完成，或者是纯对话回复
                    final_reply = message.content
                    break
                
                # 执行工具调用
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    node_id = function_name.replace("call_", "")
                    action = function_args.get("action")
                    params = function_args.get("params", {})
                    
                    logger.info(f"自主调度: 执行节点 {node_id}, 动作: {action}")
                    
                    # 执行节点
                    tool_result_content = "Error: Executor not provided in context"
                    if context and "executor" in context:
                        try:
                            # executor 应该是一个 async 函数，接收 node_id, action, params
                            result = await context["executor"](node_id, action, params)
                            tool_result_content = json.dumps(result, ensure_ascii=False)
                        except Exception as exec_err:
                            tool_result_content = f"Execution Error: {str(exec_err)}"
                    
                    # 将执行结果追加到历史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_result_content
                    })
                    
                    executed_steps.append({
                        "node_id": node_id,
                        "action": action,
                        "result": tool_result_content
                    })

            return {
                "success": True,
                "steps": executed_steps,
                "reply": final_reply or "Task completed (no final text reply)."
            }
            
        except Exception as e:
            logger.error(f"调度失败: {e}")
            return {"success": False, "error": str(e)}
