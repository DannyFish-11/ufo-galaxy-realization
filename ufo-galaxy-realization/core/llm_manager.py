import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from datetime import datetime

# 假设使用 OpenAI SDK 兼容接口
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

logger = logging.getLogger("llm_manager")

class TokenUsage(BaseModel):
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_cost: float
    timestamp: str

class HybridLLMManager:
    """
    混合架构 LLM 管理器
    支持同时挂载 OneAPI、本地 Ollama、直连 API 等多个 Provider
    根据路由规则动态分发请求
    """
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.clients: Dict[str, AsyncOpenAI] = {} # provider_name -> client
        self.provider_configs: Dict[str, Dict] = {}
        self.routing_rules: Dict[str, List[str]] = {}
        self.usage_log: List[TokenUsage] = []
        self.default_model = "gpt-4o"
        self._load_config()

    def _load_config(self):
        """加载混合架构配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 1. 加载 Providers
                    providers = config.get("model_providers", {})
                    for name, p_conf in providers.items():
                        if p_conf.get("enabled", False) and AsyncOpenAI:
                            try:
                                client = AsyncOpenAI(
                                    api_key=p_conf.get("api_key", "dummy"),
                                    base_url=p_conf.get("base_url")
                                )
                                self.clients[name] = client
                                self.provider_configs[name] = p_conf
                                logger.info(f"LLM Provider 已激活: {name} ({p_conf.get('base_url')})")
                            except Exception as e:
                                logger.error(f"初始化 Provider {name} 失败: {e}")

                    # 2. 加载路由规则
                    self.routing_rules = config.get("model_routing_rules", {})
                    
                    # 3. 默认模型 (格式: provider/model_name 或 model_name)
                    self.default_model = config.get("default_llm_model", "oneapi/gpt-4o")
                    
            except Exception as e:
                logger.error(f"加载 LLM 配置失败: {e}")

    def _resolve_model_route(self, model_alias: str, task_type: str = None) -> tuple[str, str, AsyncOpenAI]:
        """
        解析模型路由
        返回: (provider_name, actual_model_name, client)
        """
        # 1. 如果指定了 task_type，优先查路由表
        if task_type and task_type in self.routing_rules:
            candidates = self.routing_rules[task_type]
            for candidate in candidates:
                # 格式: provider/model
                if "/" in candidate:
                    p_name, m_name = candidate.split("/", 1)
                    if p_name in self.clients:
                        return p_name, m_name, self.clients[p_name]
        
        # 2. 如果 model_alias 包含 provider 前缀 (e.g. "local_ollama/llama3")
        if model_alias and "/" in model_alias:
            p_name, m_name = model_alias.split("/", 1)
            if p_name in self.clients:
                return p_name, m_name, self.clients[p_name]
        
        # 3. 默认回退到 OneAPI (如果存在)
        if "oneapi" in self.clients:
            return "oneapi", model_alias or "gpt-4o", self.clients["oneapi"]
            
        # 4. 最后的救命稻草：返回第一个可用的 client
        if self.clients:
            p_name = list(self.clients.keys())[0]
            return p_name, model_alias or "gpt-3.5-turbo", self.clients[p_name]
            
        raise ValueError("没有可用的 LLM Provider，请检查 config.json")

    async def chat_completion(self, messages: List[Dict], tools: List[Dict] = None, model_alias: str = None, task_type: str = None, **kwargs) -> Any:
        """
        混合架构 Chat 接口
        :param task_type: 任务类型 (e.g. "coding", "privacy_sensitive")，用于路由决策
        """
        try:
            provider_name, target_model, client = self._resolve_model_route(model_alias, task_type)
            
            start_time = datetime.now()
            logger.info(f"LLM 请求路由: [{task_type or 'general'}] -> {provider_name}/{target_model}")
            
            response = await client.chat.completions.create(
                model=target_model,
                messages=messages,
                tools=tools,
                **kwargs
            )
            
            # Token 审计
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                cost = 0.0 # 暂不计算复杂费率
                
                usage_record = TokenUsage(
                    model=target_model,
                    provider=provider_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_cost=cost,
                    timestamp=start_time.isoformat()
                )
                self.usage_log.append(usage_record)
                
            return response
            
        except Exception as e:
            logger.error(f"LLM 调用失败 (Target: {model_alias}): {e}")
            raise

    def get_usage_summary(self) -> Dict[str, Any]:
        """获取多 Provider 的使用统计"""
        by_provider = {}
        for u in self.usage_log:
            if u.provider not in by_provider:
                by_provider[u.provider] = {"input": 0, "output": 0, "calls": 0}
            by_provider[u.provider]["input"] += u.input_tokens
            by_provider[u.provider]["output"] += u.output_tokens
            by_provider[u.provider]["calls"] += 1
            
        return {
            "total_calls": len(self.usage_log),
            "by_provider": by_provider
        }

# 兼容旧代码的别名
LLMManager = HybridLLMManager
