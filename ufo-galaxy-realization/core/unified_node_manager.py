# -*- coding: utf-8 -*-
"""
统一节点管理器 (Unified Node Manager)
=====================================
修复节点结构管理问题，确保：
1. 配置定义与实际节点目录同步
2. 依赖关系正确验证
3. 启动顺序按优先级排序
4. 端口冲突检测
5. 节点健康检查

作者：UFO Galaxy 修复系统
日期：2026-02-11
"""

import os
import sys
import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class NodeGroup(str, Enum):
    """节点分组"""
    CORE = "core"              # 核心节点（必须启动）
    DEVELOPMENT = "development"  # 开发工具
    EXTENDED = "extended"      # 扩展功能
    ACADEMIC = "academic"      # 学术研究
    OPTIONAL = "optional"      # 可选节点


@dataclass
class NodeConfig:
    """节点配置"""
    id: str                          # 节点 ID (e.g., "00", "01")
    name: str                        # 节点名称 (e.g., "StateMachine")
    group: NodeGroup                 # 节点分组
    port: int                        # 监听端口
    description: str = ""            # 描述
    dependencies: List[str] = field(default_factory=list)  # 依赖的节点 ID
    priority: int = 50               # 优先级（越低越优先）
    auto_start: bool = True          # 是否自动启动
    restart_policy: str = "always"   # 重启策略
    max_restarts: int = 3            # 最大重启次数
    health_check_url: str = ""       # 健康检查 URL
    health_check_interval: int = 30  # 健康检查间隔（秒）
    startup_timeout: int = 30        # 启动超时（秒）
    env_vars: Dict[str, str] = field(default_factory=dict)  # 环境变量
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.health_check_url:
            self.health_check_url = f"http://localhost:{self.port}/health"


class UnifiedNodeManager:
    """统一节点管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """初始化节点管理器"""
        self.project_root = project_root or Path(__file__).parent.parent
        self.nodes_dir = self.project_root / "nodes"
        self.config_file = self.project_root / "node_dependencies.json"
        
        # 节点配置缓存
        self.node_configs: Dict[str, NodeConfig] = {}
        self.node_processes: Dict[str, subprocess.Popen] = {}
        
        # 验证结果
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        
    def load_configurations(self) -> bool:
        """加载所有节点配置"""
        logger.info("开始加载节点配置...")
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # 1. 从 node_dependencies.json 加载配置定义
        config_defs = self._load_config_file()
        if not config_defs:
            self.validation_errors.append("无法加载 node_dependencies.json")
            return False
        
        # 2. 扫描实际节点目录
        actual_nodes = self._scan_node_directories()
        if not actual_nodes:
            self.validation_errors.append("未找到任何节点目录")
            return False
        
        # 3. 合并配置和实际节点
        self._merge_configurations(config_defs, actual_nodes)
        
        # 4. 验证配置完整性
        if not self._validate_configurations():
            return False
        
        logger.info(f"✅ 成功加载 {len(self.node_configs)} 个节点配置")
        return True
    
    def _load_config_file(self) -> Dict[str, Any]:
        """从 JSON 文件加载配置定义"""
        if not self.config_file.exists():
            logger.warning(f"配置文件不存在: {self.config_file}")
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查结构
            if "nodes" not in data:
                logger.error("配置文件缺少 'nodes' 字段")
                return {}
            
            return data.get("nodes", {})
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {e}")
            self.validation_errors.append(f"JSON 解析错误: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.validation_errors.append(f"加载配置文件失败: {e}")
            return {}
    
    def _scan_node_directories(self) -> Set[str]:
        """扫描 nodes 目录，找出所有实际节点"""
        actual_nodes = set()
        
        if not self.nodes_dir.exists():
            logger.warning(f"节点目录不存在: {self.nodes_dir}")
            return actual_nodes
        
        try:
            for item in self.nodes_dir.iterdir():
                if item.is_dir() and item.name.startswith("Node_"):
                    # 检查是否有 main.py
                    main_py = item / "main.py"
                    if main_py.exists():
                        actual_nodes.add(item.name)
                    else:
                        self.validation_warnings.append(
                            f"节点目录缺少 main.py: {item.name}"
                        )
        except Exception as e:
            logger.error(f"扫描节点目录失败: {e}")
            self.validation_errors.append(f"扫描节点目录失败: {e}")
        
        logger.info(f"扫描到 {len(actual_nodes)} 个实际节点目录")
        return actual_nodes
    
    def _merge_configurations(self, config_defs: Dict[str, Any], 
                             actual_nodes: Set[str]) -> None:
        """合并配置定义和实际节点"""
        logger.info("合并配置定义和实际节点...")
        
        # 1. 处理配置定义中的节点
        for node_name, node_def in config_defs.items():
            try:
                # 提取节点 ID 和名称
                # 格式: "Node_00_StateMachine" -> id="00", name="StateMachine"
                parts = node_name.split("_")
                if len(parts) >= 3 and parts[0] == "Node":
                    node_id = parts[1]
                    node_name_part = "_".join(parts[2:])
                else:
                    node_id = node_name
                    node_name_part = node_name
                
                # 创建节点配置
                config = NodeConfig(
                    id=node_id,
                    name=node_name_part,
                    group=NodeGroup(node_def.get("group", "optional")),
                    port=node_def.get("port", 8000 + int(node_id)),
                    description=node_def.get("description", ""),
                    dependencies=node_def.get("dependencies", []),
                    priority=node_def.get("priority", 50),
                    auto_start=node_def.get("auto_start", True),
                    restart_policy=node_def.get("restart_policy", "always"),
                    max_restarts=node_def.get("max_restarts", 3),
                    health_check_url=node_def.get("health_check_url", ""),
                    health_check_interval=node_def.get("health_check_interval", 30),
                    startup_timeout=node_def.get("startup_timeout", 30),
                    env_vars=node_def.get("env_vars", {}),
                )
                
                self.node_configs[node_name] = config
                
                # 检查是否有对应的实际节点
                if node_name not in actual_nodes:
                    self.validation_warnings.append(
                        f"配置定义存在但无实际节点: {node_name}"
                    )
            
            except Exception as e:
                logger.error(f"处理节点配置失败 {node_name}: {e}")
                self.validation_errors.append(f"处理节点配置失败 {node_name}: {e}")
        
        # 2. 检查实际节点是否都有配置定义
        for node_dir in actual_nodes:
            if node_dir not in self.node_configs:
                self.validation_warnings.append(
                    f"实际节点无配置定义: {node_dir}"
                )
    
    def _validate_configurations(self) -> bool:
        """验证配置完整性"""
        logger.info("验证配置完整性...")
        
        # 1. 检查端口冲突
        ports = {}
        for node_name, config in self.node_configs.items():
            if config.port in ports:
                self.validation_errors.append(
                    f"端口冲突: {config.port} 被 {ports[config.port]} 和 {node_name} 使用"
                )
            ports[config.port] = node_name
        
        # 2. 检查依赖关系
        for node_name, config in self.node_configs.items():
            for dep_id in config.dependencies:
                # 查找依赖节点
                dep_found = False
                for other_name, other_config in self.node_configs.items():
                    if other_config.id == dep_id:
                        dep_found = True
                        break
                
                if not dep_found:
                    self.validation_errors.append(
                        f"节点 {node_name} 的依赖 {dep_id} 不存在"
                    )
        
        # 3. 检查循环依赖
        for node_name, config in self.node_configs.items():
            if self._has_circular_dependency(node_name):
                self.validation_errors.append(
                    f"节点 {node_name} 存在循环依赖"
                )
        
        # 4. 检查核心节点
        core_nodes = [
            name for name, config in self.node_configs.items()
            if config.group == NodeGroup.CORE
        ]
        if not core_nodes:
            self.validation_errors.append("未找到任何核心节点")
        
        # 返回结果
        if self.validation_errors:
            logger.error(f"❌ 验证失败，共 {len(self.validation_errors)} 个错误")
            for error in self.validation_errors:
                logger.error(f"  - {error}")
            return False
        
        if self.validation_warnings:
            logger.warning(f"⚠️ 验证警告，共 {len(self.validation_warnings)} 个警告")
            for warning in self.validation_warnings:
                logger.warning(f"  - {warning}")
        
        return True
    
    def _has_circular_dependency(self, node_name: str, 
                                visited: Optional[Set[str]] = None) -> bool:
        """检查是否存在循环依赖"""
        if visited is None:
            visited = set()
        
        if node_name in visited:
            return True
        
        visited.add(node_name)
        
        config = self.node_configs.get(node_name)
        if not config:
            return False
        
        for dep_id in config.dependencies:
            # 查找依赖节点
            for other_name, other_config in self.node_configs.items():
                if other_config.id == dep_id:
                    if self._has_circular_dependency(other_name, visited.copy()):
                        return True
        
        return False
    
    def get_nodes_by_group(self, group: NodeGroup) -> List[NodeConfig]:
        """获取指定分组的节点"""
        nodes = [
            config for config in self.node_configs.values()
            if config.group == group
        ]
        # 按优先级排序
        return sorted(nodes, key=lambda x: x.priority)
    
    def get_startup_order(self) -> List[str]:
        """获取启动顺序（考虑依赖关系）"""
        # 拓扑排序
        order = []
        visited = set()
        visiting = set()
        
        def visit(node_name: str):
            if node_name in visited:
                return
            if node_name in visiting:
                raise ValueError(f"循环依赖: {node_name}")
            
            visiting.add(node_name)
            
            config = self.node_configs.get(node_name)
            if config:
                for dep_id in config.dependencies:
                    # 查找依赖节点
                    for other_name, other_config in self.node_configs.items():
                        if other_config.id == dep_id:
                            visit(other_name)
            
            visiting.remove(node_name)
            visited.add(node_name)
            order.append(node_name)
        
        # 先访问核心节点
        for name, config in sorted(
            self.node_configs.items(),
            key=lambda x: (x[1].priority, x[0])
        ):
            visit(name)
        
        return order
    
    def get_node_by_id(self, node_id: str) -> Optional[NodeConfig]:
        """通过 ID 获取节点配置"""
        for config in self.node_configs.values():
            if config.id == node_id:
                return config
        return None
    
    def get_node_by_name(self, node_name: str) -> Optional[NodeConfig]:
        """通过名称获取节点配置"""
        return self.node_configs.get(node_name)
    
    def get_all_nodes(self) -> List[NodeConfig]:
        """获取所有节点配置"""
        return list(self.node_configs.values())
    
    def get_core_nodes(self) -> List[NodeConfig]:
        """获取核心节点"""
        return self.get_nodes_by_group(NodeGroup.CORE)
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return {
            "total_nodes": len(self.node_configs),
            "core_nodes": len(self.get_core_nodes()),
            "nodes_by_group": {
                group.value: len(self.get_nodes_by_group(group))
                for group in NodeGroup
            },
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "running_nodes": len(self.node_processes),
        }
    
    def print_report(self) -> None:
        """打印节点配置报告"""
        print("\n" + "=" * 70)
        print("节点配置报告")
        print("=" * 70)
        
        # 按分组显示
        for group in NodeGroup:
            nodes = self.get_nodes_by_group(group)
            if nodes:
                print(f"\n【{group.value.upper()}】({len(nodes)} 个节点)")
                print("-" * 70)
                for config in nodes:
                    status = "✅" if config.id in [
                        p.split("_")[1] for p in self.node_processes.keys()
                    ] else "⏹️"
                    deps = ", ".join(config.dependencies) if config.dependencies else "无"
                    print(f"  {status} [{config.id}] {config.name}")
                    print(f"     端口: {config.port}, 优先级: {config.priority}")
                    print(f"     依赖: {deps}")
                    if config.description:
                        print(f"     描述: {config.description}")
        
        # 显示验证结果
        if self.validation_errors:
            print(f"\n❌ 验证错误 ({len(self.validation_errors)} 个)")
            for error in self.validation_errors:
                print(f"  - {error}")
        
        if self.validation_warnings:
            print(f"\n⚠️ 验证警告 ({len(self.validation_warnings)} 个)")
            for warning in self.validation_warnings:
                print(f"  - {warning}")
        
        print("\n" + "=" * 70)


# 导出
__all__ = [
    "UnifiedNodeManager",
    "NodeConfig",
    "NodeGroup",
]
