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
    def __init__(self, nodes_dir: str):
        self.nodes_dir = nodes_dir
        self.tools_cache: List[Dict[str, Any]] = []
        self._load_tools()

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
                    # 假设 config.json 中有 'actions' 字段描述支持的操作
                    # 如果没有，则生成一个通用的 execute 工具
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

    async def plan_and_execute(self, instruction: str, llm_client: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        核心调度逻辑：
        1. 接收指令
        2. 注入动态设备上下文 (Device-as-Node)
        3. 调用 LLM 进行规划 (Function Calling)
        4. 解析并执行节点调用
        5. 返回结果
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
You can call multiple tools in sequence if needed.

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
        
        # if context: # Context is now integrated into system prompt
        #    messages.append({"role": "system", "content": f"Context: {json.dumps(context)}"})

        try:
            # 模拟 LLM 调用 (实际集成时需要传入真实的 client)
            # 这里我们假设 llm_client 是一个兼容 OpenAI 接口的对象
            response = await llm_client.chat.completions.create(
                model="gpt-4o", # 或配置的模型
                messages=messages,
                tools=self.tools_cache,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            tool_calls = message.tool_calls
            
            results = []
            
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    node_id = function_name.replace("call_", "")
                    action = function_args.get("action")
                    params = function_args.get("params", {})
                    
                    logger.info(f"自主调度: 调用节点 {node_id}, 动作: {action}")
                    
                    # 这里需要回调 api_routes 中的 _execute_node
                    # 为了解耦，我们返回执行计划，由调用者执行
                    results.append({
                        "node_id": node_id,
                        "action": action,
                        "params": params,
                        "tool_call_id": tool_call.id
                    })
            
            return {
                "success": True,
                "plan": results,
                "reply": message.content
            }
            
        except Exception as e:
            logger.error(f"调度失败: {e}")
            return {"success": False, "error": str(e)}
