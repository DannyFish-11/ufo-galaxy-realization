# UFO Galaxy 开发者指南

**版本**: 1.0.0  
**最后更新**: 2026-02-11  

---

## 📚 目录

1. [开发环境设置](#开发环境设置)
2. [项目结构](#项目结构)
3. [开发工作流](#开发工作流)
4. [编码规范](#编码规范)
5. [测试指南](#测试指南)
6. [调试技巧](#调试技巧)
7. [提交指南](#提交指南)

---

## 开发环境设置

### 前置要求

- Python 3.8+
- Git
- 代码编辑器（推荐 VS Code）
- 虚拟环境工具（venv 或 conda）

### 环境配置

```bash
# 1. 克隆仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行测试
python test_all_fixes.py
```

---

## 项目结构

```
ufo-galaxy-realization/
├── nodes/                      # 108 个功能节点
│   ├── Node_00_StateMachine/
│   ├── Node_01_OneAPI/
│   └── ... (106 个其他节点)
├── core/                       # 核心模块
│   ├── api_routes.py
│   ├── cache.py
│   ├── device_agent_manager.py
│   ├── health_check.py
│   ├── message_router.py
│   ├── node_communication.py
│   ├── node_protocol.py
│   ├── node_registry.py
│   ├── system_load_monitor.py
│   ├── unified_node_manager.py
│   └── vision_pipeline.py
├── launcher/                   # 启动器
│   ├── unified_launcher.py
│   ├── galaxy_launcher.py
│   └── smart_launcher.py
├── ui/                         # Web UI
│   ├── static/
│   ├── templates/
│   └── ...
├── data/                       # 数据存储
├── docs/                       # 文档
├── main_fixed.py               # 主启动脚本
├── config.yaml                 # 系统配置
├── node_dependencies.json      # 节点依赖
└── ... (其他文件)
```

---

## 开发工作流

### 1. 创建新功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 开发代码

遵循编码规范（见下文）

### 3. 运行测试

```bash
python test_all_fixes.py
python code_quality_audit.py
```

### 4. 提交代码

```bash
git add .
git commit -m "feat: 描述你的功能"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

在 GitHub 上创建 PR，等待审查

---

## 编码规范

### Python 编码规范

#### 1. 文件头

所有 Python 文件都应该有编码声明和文档字符串：

```python
# -*- coding: utf-8 -*-
"""
模块名称
========
模块描述

作者: 你的名字
日期: 2026-02-11
"""
```

#### 2. 导入顺序

```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
import requests
import numpy as np

# 本地库
from core.api_routes import APIRouter
from core.cache import Cache
```

#### 3. 命名规范

- 类名：PascalCase（如 `ConfigValidator`）
- 函数名：snake_case（如 `validate_config`）
- 常量名：UPPER_SNAKE_CASE（如 `MAX_RETRIES`）
- 私有方法：_leading_underscore（如 `_internal_method`）

#### 4. 文档字符串

```python
def validate_config(config_path: str) -> bool:
    """
    验证配置文件
    
    参数:
        config_path: 配置文件路径
    
    返回:
        True 如果配置有效，否则 False
    
    异常:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置格式无效
    """
    pass
```

#### 5. 类型提示

```python
from typing import Dict, List, Optional

def process_nodes(nodes: List[str], config: Dict[str, any]) -> Optional[Dict]:
    """处理节点"""
    pass
```

#### 6. 错误处理

```python
try:
    result = process_data()
except ValueError as e:
    logger.error(f"数据处理失败: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    raise
```

---

## 测试指南

### 运行所有测试

```bash
python test_all_fixes.py
```

### 运行特定测试

```bash
python -m pytest tests/test_config_validator.py
```

### 代码覆盖率

```bash
python -m pytest --cov=core tests/
```

### 编写测试

```python
import unittest
from core.config_validator import ConfigValidator

class TestConfigValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ConfigValidator()
    
    def test_valid_config(self):
        result = self.validator.validate("config.yaml")
        self.assertTrue(result)
    
    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            self.validator.validate("invalid.yaml")

if __name__ == '__main__':
    unittest.main()
```

---

## 调试技巧

### 1. 启用调试模式

在 `config.yaml` 中：

```yaml
development:
  debug: true
  logging_level: DEBUG
```

### 2. 使用日志

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 3. 使用 Python 调试器

```python
import pdb

def problematic_function():
    pdb.set_trace()  # 在这里暂停
    # 你的代码
```

### 4. 查看日志

```bash
# 实时查看日志
tail -f logs/system.log

# 查看特定错误
grep "ERROR" logs/system.log
```

---

## 提交指南

### 提交信息格式

```
<type>: <subject>

<body>

<footer>
```

### 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码风格（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 添加或修改测试
- `chore`: 构建、依赖等变更

### 示例

```
feat: 添加配置验证工具

- 实现了配置文件的完整验证
- 支持 YAML 和 JSON 格式
- 添加了详细的错误报告

Closes #123
```

---

## 常见问题

### Q: 如何添加新节点？

**A**: 
1. 在 `nodes/` 目录创建 `Node_XX_YourName/`
2. 创建 `main.py` 和 `config.json`
3. 更新 `node_dependencies.json`
4. 运行 `python config_validator.py` 验证

### Q: 如何修改系统配置？

**A**: 
1. 编辑 `config.yaml`
2. 运行 `python config_validator.py` 验证
3. 重启系统

### Q: 如何调试节点通信？

**A**: 
1. 启用调试模式
2. 查看 `logs/node_communication.log`
3. 使用 `python -m pdb` 调试

### Q: 如何提交代码？

**A**: 
1. 创建功能分支
2. 开发并测试
3. 提交 Pull Request
4. 等待审查

---

## 资源

- [Python 编码规范 (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Git 工作流](https://git-scm.com/book/en/v2)
- [单元测试最佳实践](https://docs.python.org/3/library/unittest.html)

---

**最后更新**: 2026-02-11  
**维护者**: UFO Galaxy Team
