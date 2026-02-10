# UFO Galaxy 系统 - 克隆和启动指南

## 📦 两个核心仓库

### 1. UFO Galaxy Integrated (完整系统)
**仓库地址：** https://github.com/DannyFish-11/ufo-galaxy-integrated

这是集成了 UFO 核心和 Galaxy 分布式架构的完整系统。

```bash
# 克隆仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-integrated.git
cd ufo-galaxy-integrated

# 进入主目录
cd ufo-galaxy-realization

# 查看目录结构
ls -la
```

**包含内容：**
- ✅ Windows UFO 客户端 (`windows_client/`)
- ✅ Android 客户端 (`android_client/`)
- ✅ 108 个功能节点 (`nodes/`)
- ✅ 后端核心 (`core/`)
- ✅ 前端仪表板 (`dashboard/`)
- ✅ 启动脚本和配置

---

### 2. UFO Galaxy Realization (原始实现)
**仓库地址：** https://github.com/DannyFish-11/ufo-galaxy-realization

这是原始的 Galaxy 实现仓库（如果您需要参考原始版本）。

```bash
# 克隆仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization

# 查看目录结构
ls -la
```

---

## 🚀 快速启动步骤

### 步骤 1: 克隆和安装依赖

```bash
# 克隆主仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-integrated.git
cd ufo-galaxy-integrated/ufo-galaxy-realization

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python3 -c "import fastapi; import websockets; print('✅ 核心依赖已安装')"
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的 API Key
# 使用您喜欢的编辑器打开 .env
nano .env  # 或 vim .env 或其他编辑器
```

**必需配置（至少选一个）：**
```
# 选项 A: 使用 OpenAI
OPENAI_API_KEY=sk-your-key-here

# 选项 B: 使用 Gemini
GEMINI_API_KEY=your-gemini-key-here

# 选项 C: 使用 DeepSeek
DEEPSEEK_API_KEY=your-deepseek-key-here

# 选项 D: 使用 OneAPI 网关（推荐）
ONEAPI_URL=http://oneapi:3000
ONEAPI_API_KEY=your-oneapi-key-here
```

**可选配置（如果使用本地模型）：**
```
# Neo4j 图数据库
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123

# Qdrant 向量数据库
QDRANT_URL=http://qdrant:6333

# Ollama 本地模型
OLLAMA_URL=http://ollama:11434
```

### 步骤 3: 启动后端服务

```bash
# 启动统一启动器（会启动所有 108 个节点）
python unified_launcher.py

# 或者启动主服务
python main.py

# 或者使用智能启动器
python smart_launcher.py
```

**预期输出：**
```
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     ██╗   ██╗███████╗ ██████╗      ██████╗  █████╗ ██╗      ██╗  ║
    ║     ██║   ██║██╔════╝██╔═══██╗    ██╔════╝ ██╔══██╗██║      ██║  ║
    ║     ██║   ██║█████╗  ██║   ██║    ██║  ███╗███████║██║      ██║  ║
    ║     ██║   ██║██╔══╝  ██║   ██║    ██║   ██║██╔══██║██║      ██║  ║
    ║     ╚██████╔╝██║     ╚██████╔╝    ╚██████╔╝██║  ██║███████╗ ██║  ║
    ║      ╚═════╝ ╚═╝      ╚═════╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═╝  ║
    ║                                                                   ║
    ║                  L4 级自主性智能系统 v2.0                         ║
    ║                     统一融合版                                    ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝

✅ 系统启动成功
```

### 步骤 4: 启动 Windows 客户端（可选）

```bash
# 在 Windows 机器上
cd windows_client
python main.py

# 或者运行批处理文件
START_CLIENT.bat
```

### 步骤 5: 构建 Android APK（可选）

```bash
# 在 Android 客户端目录
cd android_client

# 构建 APK
./build_apk.sh

# 或使用 Gradle
./gradlew build
```

---

## 📋 完整克隆命令速查表

```bash
# ========== 仓库 1: UFO Galaxy Integrated ==========
git clone https://github.com/DannyFish-11/ufo-galaxy-integrated.git
cd ufo-galaxy-integrated/ufo-galaxy-realization

# ========== 仓库 2: UFO Galaxy Realization (可选) ==========
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization

# ========== 通用启动流程 ==========
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
python unified_launcher.py
```

---

## 🔍 验证安装

```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 检查关键依赖
python3 << 'EOF'
import sys
print("✓ 检查依赖...")
for pkg in ['fastapi', 'websockets', 'pydantic', 'uvicorn']:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} 未安装")
        sys.exit(1)
print("✅ 所有依赖已安装")
EOF

# 检查项目结构
ls -d nodes/Node_* | wc -l  # 应该输出 108
```

---

## 🆘 常见问题

**Q: 启动时提示 "ModuleNotFoundError"？**
A: 运行 `pip install -r requirements.txt` 重新安装依赖

**Q: 无法连接到数据库？**
A: 检查 `.env` 中的数据库配置，确保服务已启动

**Q: Windows 客户端无法启动？**
A: 需要在 Windows 环境上运行，并确保已安装 Python 3.8+

**Q: Android APK 构建失败？**
A: 需要安装 Android SDK 和 Gradle

---

## 📚 相关文档

- `README.md` - 项目概述
- `QUICKSTART.md` - 快速开始指南
- `DEPLOYMENT_GUIDE.md` - 部署指南
- `CAPABILITY_MATRIX.md` - 能力矩阵
- `COMPLETENESS_CHECK.md` - 完整性检查报告
- `STARTUP_DIAGNOSIS.md` - 启动诊断报告

---

**最后更新：** 2026-02-07
**作者：** Manus AI
