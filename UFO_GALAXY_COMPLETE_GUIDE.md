# UFO Galaxy 系统完整使用指南

## 第一部分：系统架构和核心概念

### 什么是 UFO Galaxy 系统？

UFO Galaxy 是一个**分布式智能自动化系统**，它的核心目标是让您的电脑和手机能够**协同工作**，自动完成各种复杂的任务。

**核心理念：** 一个"大脑"（后端系统）+ 多个"手臂"（Windows、Android 等客户端）+ 108 个"技能节点"（各种功能模块）

### 系统的三层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     第一层：智能大脑（后端）                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  核心服务 (Core Services)                                │   │
│  │  ├── 统一启动器 (Unified Launcher)                      │   │
│  │  ├── 任务编排器 (Orchestrator)                          │   │
│  │  ├── 网关服务 (Gateway Service v5)                      │   │
│  │  └── 多协议支持 (WebSocket, ADB, HTTP, BLE)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  108 个功能节点 (Function Nodes)                         │   │
│  │  ├── Node_00: 状态机                                    │   │
│  │  ├── Node_01: 多模型 API 路由                           │   │
│  │  ├── Node_02: 任务管理                                  │   │
│  │  ├── Node_50: 视觉转换                                  │   │
│  │  ├── Node_110: 智能编排                                 │   │
│  │  ├── Node_124: 多设备协同                               │   │
│  │  ├── Node_127: 高级规划                                 │   │
│  │  └── ... 其他 101 个节点                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                    ▲
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
┌─────────────────▼──────┐ ┌────────▼──────────┐ ┌───▼──────────────┐
│   第二层：Windows 端    │ │   第二层：Android 端 │ │  第二层：Web 端   │
│                        │ │                  │ │                  │
│ ┌────────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │ Windows 客户端     │ │ │ │ Android APK  │ │ │ │ Web 界面     │ │
│ │ ├── UI 自动化      │ │ │ │ ├── 浮窗 UI  │ │ │ │ ├── 仪表板   │ │
│ │ ├── 桌面控制       │ │ │ │ ├── 语音输入 │ │ │ │ ├── 任务管理 │ │
│ │ ├── 截图和分析    │ │ │ │ ├── 设备控制 │ │ │ │ └── 监控     │ │
│ │ └── WebSocket 通信 │ │ │ │ └── 跨设备协同 │ │ │ └──────────────┘ │
│ └────────────────────┘ │ │ └──────────────┘ │ │                  │
└────────────────────────┘ └──────────────────┘ └──────────────────┘
```

### 核心概念解释

#### 1. **节点（Node）**

节点是系统中最小的功能单元。每个节点负责一个特定的功能：

| 节点类型 | 功能 | 示例 |
|--------|------|------|
| **感知节点** | 获取信息 | OCR（文字识别）、视觉理解、语音识别 |
| **决策节点** | 分析和规划 | 任务规划、意图理解、路由决策 |
| **执行节点** | 执行操作 | UI 自动化、文件操作、API 调用 |
| **协调节点** | 多设备协同 | 多设备协调、任务分发、状态同步 |

#### 2. **任务（Task）**

任务是用户的需求，可以是简单的（点击一个按钮）或复杂的（完成一个多步骤的工作流）。

**任务的生命周期：**
```
用户输入 → 意图理解 → 任务规划 → 任务分解 → 节点执行 → 结果反馈
```

#### 3. **设备（Device）**

系统支持多种设备类型：

- **Windows PC** - 主要工作设备
- **Android 手机** - 移动设备，可以进行手机操作
- **Web 浏览器** - 远程控制和监控
- **其他设备** - 可扩展支持

#### 4. **协议（Protocol）**

系统支持多种通信协议，确保不同设备间的无缝通信：

| 协议 | 用途 | 设备 |
|------|------|------|
| **WebSocket** | 实时双向通信 | Windows、Web |
| **ADB** | Android 设备通信 | Android 手机 |
| **HTTP/REST** | 标准 Web 通信 | 所有设备 |
| **BLE** | 蓝牙通信 | 可穿戴设备 |

---

## 第二部分：手机和电脑的集成方式

### 工作流程图

```
┌─────────────┐
│  用户说话   │  "帮我在电脑上打开 Word，然后在手机上发个邮件"
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Android 浮窗 (语音输入)                │
│  ├── 语音识别 (Speech to Text)          │
│  └── 发送到后端                         │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  后端处理 (Backend)                     │
│  ├── Node_01: 意图理解                  │
│  │   → 识别出两个任务：                  │
│  │     1. 在电脑上打开 Word              │
│  │     2. 在手机上发邮件                 │
│  │                                      │
│  ├── Node_127: 任务规划                 │
│  │   → 规划执行顺序和依赖关系            │
│  │                                      │
│  └── Node_124: 多设备协调                │
│      → 分配任务到不同设备                │
└──────┬──────────────────────────────────┘
       │
       ├─────────────┬──────────────┐
       │             │              │
       ▼             ▼              ▼
   ┌────────┐  ┌────────┐  ┌────────────┐
   │Windows │  │Android │  │ 其他设备   │
   │ PC     │  │ 手机   │  │            │
   │        │  │        │  │            │
   │执行：  │  │执行：  │  │            │
   │打开    │  │发送    │  │            │
   │Word    │  │邮件    │  │            │
   └────┬───┘  └───┬────┘  └────────────┘
        │          │
        └────┬─────┘
             │
             ▼
        ┌─────────────┐
        │ 结果反馈    │
        │ 两个任务都  │
        │ 已完成      │
        └─────────────┘
```

### 具体集成步骤

#### 步骤 1：启动后端系统

在您的电脑上运行：

```bash
# 进入项目目录
cd ufo-galaxy-realization

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动系统
python main.py
```

系统会输出：
```
✅ 统一启动器已启动
✅ 108 个节点已加载
✅ 网关服务运行在 http://localhost:8000
✅ WebSocket 服务运行在 ws://localhost:8768
```

#### 步骤 2：连接 Windows 客户端

Windows 客户端会**自动启动**，您会看到：

- **隐形侧边栏** - 在屏幕右侧，默认隐藏
- **唤醒方式** - 按 **F12** 键（或模拟 Fn 键）唤醒
- **界面** - 显示系统状态、任务列表、设备连接状态

#### 步骤 3：安装并启动 Android 应用

在您的 Android 手机上：

```bash
# 在项目根目录构建 APK
cd ufo-galaxy-android
./gradlew build

# 或者直接安装预编译的 APK
adb install app/build/outputs/apk/release/app-release.apk
```

启动应用后，您会看到：

- **浮窗 UI** - 一个小的悬浮窗，显示在屏幕上
- **语音输入** - 点击麦克风图标，说出您的命令
- **文本输入** - 也可以输入文字命令

#### 步骤 4：配置设备连接

在 `.env` 文件中配置：

```env
# 后端地址
BACKEND_URL=http://localhost:8000
WEBSOCKET_URL=ws://localhost:8768

# 设备名称
WINDOWS_DEVICE_NAME=MyComputer
ANDROID_DEVICE_NAME=MyPhone

# API Key（用于安全通信）
API_KEY=your-secret-key-here
```

#### 步骤 5：验证连接

打开 Android 应用，您应该看到：

```
✅ 已连接到后端
✅ 设备已注册
✅ 可以开始使用
```

---

## 第三部分：节点系统工作原理

### 节点的分类和功能

#### 第一类：感知节点（Perception Nodes）

这些节点负责**获取信息**：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **Node_15_OCR** | 文字识别 | 图片 | 识别的文字 |
| **Node_50_Transformer** | 视觉转换 | 截图 | 视觉理解结果 |
| **Node_60_SpeechRecognition** | 语音识别 | 音频 | 文字 |
| **Node_70_WebScraper** | 网页爬取 | URL | 网页内容 |

#### 第二类：决策节点（Decision Nodes）

这些节点负责**分析和规划**：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **Node_01_OneAPI** | 多模型路由 | 任务描述 | 最优模型选择 |
| **Node_02_Tasker** | 任务管理 | 用户需求 | 任务列表 |
| **Node_110_SmartOrchestrator** | 智能编排 | 任务 | 执行计划 |
| **Node_127_Planning** | 高级规划 | 复杂任务 | 详细计划 |

#### 第三类：执行节点（Execution Nodes）

这些节点负责**执行操作**：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **Node_03_SecretVault** | 密钥管理 | 密钥名称 | 密钥值 |
| **Node_04_Router** | 路由决策 | 任务 | 目标设备 |
| **Node_05_UIAutomation** | UI 自动化 | 操作指令 | 执行结果 |
| **Node_06_FileOperations** | 文件操作 | 文件路径 | 操作结果 |

#### 第四类：协调节点（Coordination Nodes）

这些节点负责**多设备协同**：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **Node_124_MultiDeviceCoordination** | 多设备协调 | 任务 | 分配方案 |
| **Node_125_DeviceHeartbeat** | 设备心跳 | 设备状态 | 健康检查 |
| **Node_126_CrossDeviceSync** | 跨设备同步 | 数据 | 同步结果 |

### 节点的执行流程

```
┌──────────────────────────────────────────────────────────┐
│ 用户输入：                                                │
│ "帮我在 Word 中写一份报告，然后保存到 OneDrive"          │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Node_02_Tasker     │
        │ 任务分解           │
        │ ↓                  │
        │ Task 1: 打开 Word  │
        │ Task 2: 写报告     │
        │ Task 3: 保存文件   │
        │ Task 4: 上传云端   │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Node_127_Planning  │
        │ 任务规划           │
        │ ↓                  │
        │ 生成执行计划：      │
        │ 1. 在 Windows 执行  │
        │ 2. 需要 Office API  │
        │ 3. 需要 OneDrive    │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Node_01_OneAPI     │
        │ 模型选择           │
        │ ↓                  │
        │ 选择 GPT-4 生成    │
        │ 报告内容           │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Node_124_Multi     │
        │ DeviceCoordination │
        │ ↓                  │
        │ 分配任务：          │
        │ Windows: 执行所有   │
        │ 操作                │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Node_05_UIAuto     │
        │ 执行操作           │
        │ ↓                  │
        │ 1. 打开 Word       │
        │ 2. 输入文字        │
        │ 3. 保存文件        │
        │ 4. 上传到云端      │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ 任务完成           │
        │ 返回结果给用户     │
        └────────────────────┘
```

### 节点间的通信

节点之间通过**消息队列**进行通信：

```python
# 节点 A 发送消息
message = {
    "source": "Node_02_Tasker",
    "target": "Node_127_Planning",
    "type": "task_plan_request",
    "data": {
        "tasks": [
            {"id": 1, "description": "打开 Word"},
            {"id": 2, "description": "写报告"}
        ]
    }
}

# 节点 B 接收并处理
def handle_task_plan_request(message):
    tasks = message["data"]["tasks"]
    plan = generate_plan(tasks)
    
    response = {
        "source": "Node_127_Planning",
        "target": "Node_02_Tasker",
        "type": "task_plan_response",
        "data": plan
    }
    
    return response
```

---

## 第四部分：完整使用流程和实际案例

### 案例 1：简单任务 - 在电脑上打开浏览器

#### 流程：

1. **用户操作**
   - 在 Android 手机上说：**"打开浏览器"**

2. **系统处理**
   ```
   Android 浮窗 → 语音识别 → "打开浏览器"
                                    ↓
                            后端意图理解
                                    ↓
                            识别为：打开应用
                                    ↓
                            路由到 Windows
                                    ↓
                            执行 UI 自动化
                                    ↓
                            浏览器打开
   ```

3. **结果反馈**
   - Android 手机显示：**"✅ 浏览器已打开"**

#### 代码示例：

```python
# 在 Android 应用中
def on_voice_input(text):
    # 1. 发送到后端
    response = send_to_backend({
        "type": "command",
        "content": text,
        "device": "android"
    })
    
    # 2. 显示结果
    show_result(response["message"])

# 在后端中
def handle_command(command):
    # 1. 理解意图
    intent = understand_intent(command["content"])  # "打开浏览器"
    
    # 2. 路由到正确的设备
    if intent["device"] == "windows":
        result = execute_on_windows(intent)
    elif intent["device"] == "android":
        result = execute_on_android(intent)
    
    # 3. 返回结果
    return {"status": "success", "message": "浏览器已打开"}
```

### 案例 2：复杂任务 - 跨设备工作流

#### 场景：

您想要：
1. 在电脑上打开一个 Excel 文件
2. 在手机上拍照
3. 将照片插入 Excel
4. 保存文件到云端

#### 流程：

```
用户命令：
"在电脑上打开 sales.xlsx，用手机拍个产品照，
 插入到 Excel 中，保存到 OneDrive"

                    ↓
        
后端处理（Node_127_Planning）：
┌─────────────────────────────────────┐
│ 任务分解：                          │
│ 1. Windows: 打开 Excel              │
│ 2. Android: 拍照                    │
│ 3. Windows: 插入图片                │
│ 4. Windows: 保存到云端              │
│                                     │
│ 执行顺序：1 → 2 → 3 → 4            │
│ 依赖关系：2 完成后才能执行 3        │
└─────────────────────────────────────┘

                    ↓

设备执行（Node_124_MultiDeviceCoordination）：

Windows PC                  Android Phone
│                          │
├─ 打开 Excel              │
│  ✅ 完成                  │
│                          │
│                          ├─ 启动相机
│                          │  ✅ 拍照完成
│                          │
├─ 等待照片                │
│  ✅ 接收照片              │
│                          │
├─ 插入图片                │
│  ✅ 完成                  │
│                          │
├─ 保存到 OneDrive         │
│  ✅ 完成                  │
│                          │
└─ 返回结果                │
   ✅ 任务完成              │
```

#### 代码实现：

```python
# 在后端中
class CrossDeviceWorkflow:
    def __init__(self):
        self.windows_device = WindowsDevice()
        self.android_device = AndroidDevice()
    
    async def execute_workflow(self, command):
        # 1. 打开 Excel
        excel_result = await self.windows_device.open_file("sales.xlsx")
        
        # 2. 在 Android 上拍照
        photo_result = await self.android_device.take_photo()
        photo_path = photo_result["path"]
        
        # 3. 在 Excel 中插入照片
        insert_result = await self.windows_device.insert_image(
            excel_file="sales.xlsx",
            image_path=photo_path
        )
        
        # 4. 保存到云端
        save_result = await self.windows_device.save_to_cloud(
            file="sales.xlsx",
            destination="OneDrive"
        )
        
        return {
            "status": "success",
            "message": "任务已完成",
            "steps": [excel_result, photo_result, insert_result, save_result]
        }

# 在 Android 应用中
def handle_workflow_step(step):
    if step["action"] == "take_photo":
        # 启动相机
        camera = Camera()
        photo = camera.take_photo()
        
        # 上传到后端
        send_to_backend({
            "type": "workflow_result",
            "step": step["id"],
            "data": photo
        })
```

### 案例 3：自动化工作 - 定时任务

#### 场景：

每天早上 8 点自动：
1. 检查邮件
2. 生成日报
3. 发送到团队

#### 配置：

```json
{
  "task_id": "daily_report",
  "schedule": "0 8 * * *",  // 每天早上 8 点
  "steps": [
    {
      "device": "windows",
      "action": "check_emails",
      "config": {
        "email_account": "work@company.com"
      }
    },
    {
      "device": "windows",
      "action": "generate_report",
      "config": {
        "template": "daily_report.docx",
        "data_source": "database"
      }
    },
    {
      "device": "windows",
      "action": "send_email",
      "config": {
        "recipients": ["team@company.com"],
        "subject": "Daily Report"
      }
    }
  ]
}
```

---

## 第五部分：快速开始指南

### 最简单的启动方式

#### 步骤 1：准备环境

```bash
# 克隆仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-realization.git
cd ufo-galaxy-realization

# 安装依赖
pip install -r requirements.txt

# 创建环境文件
cp .env.example .env
```

#### 步骤 2：启动后端

```bash
# 运行审计（可选）
python system_audit.py

# 启动系统
python main.py
```

#### 步骤 3：连接设备

**Windows：** 自动启动，按 F12 唤醒侧边栏

**Android：** 安装 APK 并启动应用

#### 步骤 4：开始使用

在 Android 应用中说出您的命令，例如：
- **"打开浏览器"**
- **"发送邮件给张三"**
- **"生成一份报告"**
- **"在电脑上打开 Word，然后在手机上拍照"**

### 常见命令

| 命令 | 说明 |
|------|------|
| **"打开 [应用名]"** | 在电脑上打开应用 |
| **"拍照"** | 用手机拍照 |
| **"发送邮件给 [人名]"** | 发送邮件 |
| **"生成 [文档类型]"** | 生成文档 |
| **"保存到 [位置]"** | 保存文件 |
| **"同步数据"** | 在设备间同步 |

---

## 第六部分：故障排除

### 问题 1：Android 无法连接到后端

**症状：** 应用显示"❌ 无法连接"

**解决方案：**
```bash
# 1. 检查后端是否运行
python main.py

# 2. 检查网络连接
ping localhost

# 3. 检查 .env 文件中的 BACKEND_URL 是否正确
# 如果在同一网络，使用电脑 IP 地址而不是 localhost
# BACKEND_URL=http://192.168.1.100:8000
```

### 问题 2：Windows 客户端无法启动

**症状：** 按 F12 没有反应

**解决方案：**
```bash
# 1. 检查后端是否运行
python main.py

# 2. 运行系统审计
python system_audit.py

# 3. 运行一键修复
python fix_system.py

# 4. 重启系统
```

### 问题 3：任务执行失败

**症状：** 命令被理解但执行失败

**解决方案：**
```bash
# 1. 检查日志
tail -f logs/system.log

# 2. 检查设备连接状态
# 在 Android 应用中查看"设备状态"

# 3. 尝试简单命令测试
# 例如："打开浏览器"
```

---

## 总结

UFO Galaxy 系统是一个强大的分布式自动化平台，它通过以下方式将您的电脑和手机联合起来：

1. **统一的后端** - 108 个节点组成的智能大脑
2. **多设备支持** - Windows、Android、Web 等
3. **智能协调** - 自动分配任务到最合适的设备
4. **自然语言交互** - 用语音或文字下达命令
5. **跨设备协同** - 在多个设备间无缝协作

现在您已经了解了系统的架构和使用方法，可以开始体验这个强大的自动化系统了！

**建议下一步：**
1. 按照"快速开始指南"启动系统
2. 尝试简单命令（如"打开浏览器"）
3. 逐步尝试更复杂的任务
4. 根据需要自定义和扩展功能
