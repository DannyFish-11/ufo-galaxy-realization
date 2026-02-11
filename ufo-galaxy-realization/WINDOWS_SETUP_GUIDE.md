# UFO Galaxy - Windows 完整安装和启动指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [详细安装步骤](#详细安装步骤)
4. [配置和启动](#配置和启动)
5. [常见问题](#常见问题)
6. [故障排查](#故障排查)

---

## 🖥️ 系统要求

### 硬件要求
- **CPU**: Intel i5 或更高 / AMD Ryzen 5 或更高
- **内存**: 8GB 或以上（推荐 16GB）
- **存储**: 10GB 可用空间
- **网络**: 互联网连接

### 软件要求
- **操作系统**: Windows 10/11 64位
- **Python**: 3.8 或更高版本
- **Git**: （可选，用于克隆仓库）

---

## ⚡ 快速开始

### 方法 1：使用 PowerShell（推荐）

1. **打开 PowerShell**
   - 按 `Win + X`，选择 "Windows PowerShell (管理员)"

2. **导航到项目目录**
   ```powershell
   cd D:\ufo-galaxy-realization
   ```

3. **允许脚本执行**（首次运行）
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **运行启动脚本**
   ```powershell
   .\start_windows.ps1
   ```

### 方法 2：使用命令提示符

1. **打开命令提示符**
   - 按 `Win + R`，输入 `cmd`，按 Enter

2. **导航到项目目录**
   ```cmd
   cd D:\ufo-galaxy-realization
   ```

3. **运行启动脚本**
   ```cmd
   start_windows.bat
   ```

---

## 📦 详细安装步骤

### 步骤 1：安装 Python

1. **下载 Python**
   - 访问 https://www.python.org/downloads/
   - 下载 Python 3.11 或更高版本

2. **安装 Python**
   - 运行安装程序
   - **重要**：勾选 "Add Python to PATH"
   - 选择 "Install Now"

3. **验证安装**
   ```cmd
   python --version
   pip --version
   ```

### 步骤 2：克隆或下载项目

#### 方法 A：使用 Git 克隆（推荐）

```cmd
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization
```

#### 方法 B：手动下载

1. 访问 https://github.com/DannyFish-11/ufo-galaxy-realization
2. 点击 "Code" → "Download ZIP"
3. 解压到本地目录（例如 `D:\ufo-galaxy-realization`）

### 步骤 3：安装依赖

```cmd
pip install -r requirements.txt
```

**注意**：如果遇到权限问题，使用：
```cmd
python -m pip install --user -r requirements.txt
```

### 步骤 4：配置环境变量

1. **创建 `.env` 文件**
   - 在项目根目录创建文件 `.env`
   - 添加以下内容：

   ```env
   # LLM API 密钥
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   XAI_API_KEY=your_xai_key_here
   
   # 其他服务
   GITHUB_TOKEN=your_github_token_here
   OPENWEATHERMAP_API_KEY=your_weather_key_here
   BRAVE_API_KEY=your_brave_key_here
   ```

2. **获取 API 密钥**
   - OpenAI: https://platform.openai.com/api-keys
   - Google Gemini: https://ai.google.dev/
   - OpenRouter: https://openrouter.ai/
   - xAI Grok: https://docs.x.ai/

---

## 🚀 配置和启动

### 验证配置

在启动前，验证配置是否正确：

```cmd
python config_validator.py
```

**预期输出**：
```
✅ 配置文件存在
✅ 节点目录存在
✅ 配置文件格式正确，包含 108 个节点定义
✅ 配置定义与节点目录完全同步 (108 个节点)
✅ 依赖关系验证通过
✅ 端口检查通过，108 个端口无冲突
✅ 所有验证通过！系统配置正确。
```

### 自动修复配置

如果验证失败，运行自动修复工具：

```cmd
python auto_fix.py
```

### 启动系统

#### 使用启动脚本（推荐）

**PowerShell**：
```powershell
.\start_windows.ps1
```

**命令提示符**：
```cmd
start_windows.bat
```

#### 直接使用 Python

```cmd
python main_fixed.py
```

### 启动选项

| 选项 | 说明 | 命令 |
|------|------|------|
| 默认启动 | 启动完整系统 | `python main_fixed.py` |
| 仅验证 | 只验证配置，不启动 | `python main_fixed.py --validate` |
| 最小启动 | 只启动核心节点 | `python main_fixed.py --minimal` |
| 无 UI 启动 | 启动但不开启 Web UI | `python main_fixed.py --no-ui` |
| 查看状态 | 显示系统状态 | `python main_fixed.py --status` |

---

## ❓ 常见问题

### Q1：Python 未被识别

**问题**：`'python' 不是内部或外部命令`

**解决方案**：
1. 重新安装 Python，勾选 "Add Python to PATH"
2. 重启命令提示符
3. 使用完整路径：`C:\Python311\python.exe main_fixed.py`

### Q2：权限被拒绝

**问题**：`PermissionError: [Errno 13] Permission denied`

**解决方案**：
1. 使用管理员模式运行命令提示符
2. 或使用 `python -m pip install --user` 安装

### Q3：编码错误

**问题**：`UnicodeDecodeError: 'gbk' codec can't decode byte`

**解决方案**：
1. 设置环境变量：`set PYTHONUTF8=1`
2. 使用启动脚本（已自动设置）
3. 在 PowerShell 中运行：`$env:PYTHONUTF8 = 1`

### Q4：端口已被占用

**问题**：`[Errno 10048] 通常每个套接字地址只允许使用一次`

**解决方案**：
1. 查找占用端口的进程：
   ```cmd
   netstat -ano | findstr :8080
   ```
2. 结束进程：
   ```cmd
   taskkill /PID <PID> /F
   ```

### Q5：依赖安装失败

**问题**：`ERROR: Could not find a version that satisfies the requirement`

**解决方案**：
1. 升级 pip：
   ```cmd
   python -m pip install --upgrade pip
   ```
2. 使用国内源：
   ```cmd
   pip install -r requirements.txt -i https://pypi.tsinghua.edu.cn/simple
   ```

---

## 🔧 故障排查

### 完整诊断流程

1. **检查 Python 环境**
   ```cmd
   python --version
   pip --version
   python -c "import sys; print(sys.path)"
   ```

2. **验证依赖**
   ```cmd
   pip list
   ```

3. **验证配置**
   ```cmd
   python config_validator.py
   ```

4. **自动修复**
   ```cmd
   python auto_fix.py
   ```

5. **查看系统状态**
   ```cmd
   python main_fixed.py --status
   ```

### 查看日志

系统会在控制台输出详细日志。如果需要保存日志：

```cmd
python main_fixed.py > log.txt 2>&1
```

### 获取帮助

1. **查看帮助信息**
   ```cmd
   python main_fixed.py --help
   python config_validator.py --help
   python auto_fix.py --help
   ```

2. **查看项目文档**
   - 主文档：`UFO_GALAXY_COMPLETE_GUIDE.md`
   - 克隆说明：`CLONE_INSTRUCTIONS.md`

---

## 🌐 访问 Web UI

系统启动后，打开浏览器访问：

```
http://localhost:8080
```

### Web UI 功能

- 📊 系统状态监控
- 🔧 节点管理
- 📈 性能统计
- ⚙️ 配置管理

---

## 📞 支持和反馈

如遇到问题，请：

1. 查看本指南的 [常见问题](#常见问题) 和 [故障排查](#故障排查) 部分
2. 查看项目 GitHub Issues：https://github.com/DannyFish-11/ufo-galaxy-realization/issues
3. 提交新 Issue 时，请包含：
   - Windows 版本
   - Python 版本
   - 完整错误信息
   - 运行的命令

---

## 📝 更新日志

### v1.0 (2026-02-11)
- ✅ 修复了节点配置加载问题
- ✅ 修复了依赖引用格式不一致
- ✅ 修复了节点分组类型不统一
- ✅ 创建了自动修复工具
- ✅ 创建了 Windows 启动脚本
- ✅ 完善了配置验证工具

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**最后更新**：2026-02-11
**作者**：UFO Galaxy 修复系统
