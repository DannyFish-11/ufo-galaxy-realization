# UFO Galaxy - L4 级自主性智能系统

UFO Galaxy 是一个 L4 级自主性智能系统，具备物理设备控制、Android 集成和系统级 AI 交互层。本系统整合了 108+ 节点，支持跨设备协同、自主决策和智能推理。

## 🚀 快速启动

### 方式 1: 使用统一启动器（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动系统（使用统一启动器）
python unified_launcher.py

# 或使用启动脚本
./start.sh           # Linux/Mac
start.bat            # Windows
```

### 方式 2: Docker Compose

```bash
docker-compose up -d
```

## 📖 启动说明

**重要提示：** 从 v2.0 开始，所有启动入口已统一到 `unified_launcher.py`。

- ✅ **推荐使用**: `python unified_launcher.py` 或启动脚本 `./start.sh` / `start.bat`
- ⚠️  **已弃用**: `main.py`, `galaxy_launcher.py`, `smart_launcher.py`, `galaxy_main_loop*.py`, `start_l4.py` 等文件已改为 thin-wrapper，会自动重定向到统一启动器。

### 启动选项

```bash
python unified_launcher.py              # 默认启动（完整模式）
python unified_launcher.py --minimal    # 最小启动
python unified_launcher.py --no-l4      # 不启动 L4 模块
python unified_launcher.py --no-ui      # 不启动 Web UI
python unified_launcher.py --status     # 查看系统状态
python unified_launcher.py --port 8080  # 指定 Web UI 端口
```

## 📱 Android 客户端

**Android 独立仓库**: [DannyFish-11/ufo-galaxy-android](https://github.com/DannyFish-11/ufo-galaxy-android)

本仓库中的 `android_client/` 目录包含旧版/示例代码，主要用于参考。推荐使用独立的 Android 仓库进行开发和部署。

## 🔧 系统架构

本系统包含以下核心组件：

1. **核心服务层** - Device Agent、设备状态管理、UFO 集成
2. **节点系统** - 108+ 功能节点（详见下方节点列表）
3. **L4 增强模块** - 感知、推理、学习、执行
4. **Web UI 和 API 服务** - 管理界面和 RESTful API

## 已实现的节点列表

### 第一优先级 - 基础服务节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_02_Tasker | 任务调度器 | 8002 | 任务队列、定时任务、状态跟踪 |
| Node_03_SecretVault | 密钥管理 | 8003 | 密钥存储、加密解密、密钥轮换 |
| Node_05_Auth | 认证服务 | 8005 | 用户认证、JWT令牌、权限控制 |
| Node_06_Filesystem | 文件系统 | 8006 | 文件读写、目录管理、压缩解压 |

### 第二优先级 - 数据库节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_12_Postgres | PostgreSQL | 8012 | PostgreSQL连接、查询、事务 |
| Node_13_SQLite | SQLite | 8013 | SQLite数据库操作 |
| Node_20_Qdrant | 向量数据库 | 8020 | 向量存储、相似度搜索 |

### 第三优先级 - 工具节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_14_FFmpeg | 视频处理 | 8014 | 视频转码、剪辑、截图 |
| Node_16_Email | 邮件服务 | 8016 | SMTP邮件发送、模板 |
| Node_17_EdgeTTS | 语音合成 | 8017 | 文本转语音 |
| Node_18_DeepL | 翻译服务 | 8018 | 文本翻译 |
| Node_19_Crypto | 加密服务 | 8019 | 加密解密、哈希、签名 |

### 第四优先级 - 搜索节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_22_BraveSearch | Brave搜索 | 8022 | 网页搜索、图片搜索 |
| Node_25_GoogleSearch | Google搜索 | 8025 | Google搜索 |

### 第五优先级 - 时间和天气节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_23_Calendar | 日历服务 | 8023 | 日历管理、事件创建 |
| Node_23_Time | 时间服务 | 8123 | 时间查询、时区转换 |
| Node_24_Weather | 天气查询 | 8024 | 天气查询、预报 |

### 第六优先级 - 设备控制节点

| 节点 | 名称 | 端口 | 功能 |
|------|------|------|------|
| Node_39_SSH | SSH连接 | 8039 | SSH连接、命令执行 |
| Node_41_MQTT | MQTT消息队列 | 8041 | MQTT发布订阅 |

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行节点

```bash
# 进入节点目录
cd nodes/Node_02_Tasker

# 运行节点
python main.py
```

### 环境变量配置

```bash
# Node 03: SecretVault
export SECRETVAULT_MASTER_KEY="your-master-key"

# Node 05: Auth
export AUTH_JWT_SECRET="your-jwt-secret"

# Node 12: PostgreSQL
export POSTGRES_HOST="localhost"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="your-password"
export POSTGRES_DATABASE="postgres"

# Node 16: Email
export SMTP_HOST="smtp.gmail.com"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-password"

# Node 18: DeepL
export DEEPL_API_KEY="your-api-key"

# Node 22: BraveSearch
export BRAVE_API_KEY="your-api-key"

# Node 24: Weather
export OPENWEATHER_API_KEY="your-api-key"

# Node 25: GoogleSearch
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CSE_ID="your-cse-id"

# Node 41: MQTT
export MQTT_BROKER="localhost"
export MQTT_PORT="1883"
```

## API文档

每个节点都提供以下标准端点：

- `GET /health` - 健康检查
- 各节点特有的功能端点

启动节点后，访问 `http://localhost:{port}/docs` 查看完整的API文档（Swagger UI）。

## 节点结构

每个节点包含以下文件：

```
Node_XX_Name/
├── main.py          # 主要业务逻辑
├── fusion_entry.py  # 融合入口文件
└── README.md        # 节点说明（可选）
```

## 依赖说明

- **必需依赖**: fastapi, uvicorn, pydantic
- **数据库节点**: asyncpg (PostgreSQL), qdrant-client (Qdrant)
- **加密节点**: cryptography
- **语音节点**: edge-tts
- **SSH节点**: asyncssh
- **MQTT节点**: paho-mqtt

## 许可证

MIT License
