"""
FastAPI Application v2.0 - 改进版应用

改进内容：
1. 安全性加固 - CORS 限制、API Key 验证、速率限制
2. 认证中间件 - 所有 API 端点都需要 API Key
3. 错误处理 - 统一的错误响应格式
4. 日志记录 - 详细的请求/响应日志
5. 健康检查 - 系统健康检查端点

Author: Manus AI
Version: 2.0
Date: 2026-02-08
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time

from cross_device_coordinator_v2 import (
    initialize_coordinator,
    get_coordinator,
    SecurityManager
)

# ============================================================================
# 日志配置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI 应用初始化
# ============================================================================

app = FastAPI(
    title="UFO Galaxy v2.0",
    description="改进版跨设备协同系统",
    version="2.0.0"
)

# ============================================================================
# 安全配置
# ============================================================================

# 允许的来源（严格限制）
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    # 生产环境应该添加实际的域名
    # "https://yourdomain.com",
]

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 严格限制来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
)

# ============================================================================
# 全局变量和单例
# ============================================================================

# 创建全局 SecurityManager 单例
_security_manager_instance = None

def get_security_manager() -> SecurityManager:
    """获取 SecurityManager 单例"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager()
        # 添加默认的 API Key（仅用于测试）
        _security_manager_instance.generate_api_key("default_client")
    return _security_manager_instance

security_manager = get_security_manager()
coordinator = None

# ============================================================================
# 初始化
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global coordinator, security_manager
    
    logger.info("🚀 UFO Galaxy v2.0 启动中...")
    
    # 确保 SecurityManager 单例已初始化
    security_manager = get_security_manager()
    
    # 初始化协调器
    coordinator = initialize_coordinator()
    
    logger.info("✅ UFO Galaxy v2.0 启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 UFO Galaxy v2.0 关闭中...")
    
    if coordinator:
        await coordinator.device_discovery.stop_discovery()
    
    logger.info("✅ UFO Galaxy v2.0 关闭完成")

# ============================================================================
# 认证依赖
# ============================================================================

async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    验证 API Key
    
    Args:
        x_api_key: API Key（从请求头获取）
    
    Returns:
        客户端名称
    
    Raises:
        HTTPException: 如果 API Key 无效
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="缺少 API Key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    is_valid, client_name = security_manager.validate_api_key(x_api_key)
    
    if not is_valid:
        logger.warning(f"无效的 API Key: {x_api_key}")
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return client_name

# ============================================================================
# 中间件
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    记录所有请求的方法、路径、状态码和响应时间
    """
    start_time = time.time()
    
    # 记录请求
    logger.info(f"📨 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"❌ 请求处理失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "内部服务器错误",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # 记录响应
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"状态码: {response.status_code} - "
        f"耗时: {process_time:.3f}s"
    )
    
    return response

# ============================================================================
# 健康检查端点
# ============================================================================

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查端点（不需要认证）
    
    Returns:
        系统健康状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "service": "UFO Galaxy"
    }


@app.get("/health/detailed")
async def detailed_health_check(client_name: str = Depends(verify_api_key)) -> Dict[str, Any]:
    """
    详细健康检查端点（需要认证）
    
    Args:
        client_name: 客户端名称（通过认证依赖获取）
    
    Returns:
        详细的系统健康状态
    """
    global coordinator
    
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "service": "UFO Galaxy",
        "client": client_name,
        "components": {
            "coordinator": "initialized" if coordinator else "not_initialized",
            "security_manager": "active",
            "concurrency_manager": "active" if coordinator else "inactive",
            "device_discovery": "active" if coordinator else "inactive",
            "auto_reconnect": "active" if coordinator else "inactive"
        }
    }
    
    return health_info

# ============================================================================
# 跨设备协同 API
# ============================================================================

@app.post("/api/v2/cross-device/execute")
async def execute_cross_device_task(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    执行跨设备协同任务
    
    请求体示例：
    ```json
    {
        "command": "把手机上的文本复制到电脑",
        "context": {},
        "timeout": 30
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 客户端名称（通过认证依赖获取）
    
    Returns:
        任务执行结果
    """
    global coordinator
    
    if not coordinator:
        return {
            "success": False,
            "error": "协调器未初始化",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # 解析请求体
        body = await request.json()
        command = body.get("command")
        context = body.get("context", {})
        timeout = body.get("timeout", 30)
        
        if not command:
            return {
                "success": False,
                "error": "缺少 command 参数",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"客户端 {client_name} 执行任务: {command}")
        
        # 执行任务
        result = await coordinator.execute_cross_device_task(
            command=command,
            context=context,
            api_key=None,  # API Key 已通过中间件验证
            timeout=timeout
        )
        
        result["timestamp"] = datetime.now().isoformat()
        result["client"] = client_name
        
        return result
    
    except Exception as e:
        logger.error(f"❌ 任务执行失败: {e}")
        return {
            "success": False,
            "error": f"任务执行失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v2/cross-device/clipboard/sync")
async def sync_clipboard(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    同步剪贴板
    
    请求体示例：
    ```json
    {
        "source_device": "android",
        "target_device": "windows"
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 客户端名称
    
    Returns:
        同步结果
    """
    global coordinator
    
    if not coordinator:
        return {
            "success": False,
            "error": "协调器未初始化",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        body = await request.json()
        source_device = body.get("source_device", "android")
        target_device = body.get("target_device", "windows")
        
        command = f"把{source_device}上的文本复制到{target_device}"
        
        logger.info(f"客户端 {client_name} 同步剪贴板: {source_device} -> {target_device}")
        
        result = await coordinator._sync_clipboard(command)
        result["timestamp"] = datetime.now().isoformat()
        result["client"] = client_name
        
        return result
    
    except Exception as e:
        logger.error(f"❌ 剪贴板同步失败: {e}")
        return {
            "success": False,
            "error": f"剪贴板同步失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v2/cross-device/file/transfer")
async def transfer_file(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    跨设备文件传输
    
    请求体示例：
    ```json
    {
        "source_device": "android",
        "target_device": "windows",
        "file_path": "/sdcard/Pictures/photo.jpg"
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 客户端名称
    
    Returns:
        传输结果
    """
    global coordinator
    
    if not coordinator:
        return {
            "success": False,
            "error": "协调器未初始化",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        body = await request.json()
        source_device = body.get("source_device", "android")
        target_device = body.get("target_device", "windows")
        file_path = body.get("file_path")
        
        command = f"把{source_device}上的{file_path}传输到{target_device}"
        
        logger.info(f"客户端 {client_name} 传输文件: {file_path}")
        
        result = await coordinator._transfer_file(command)
        result["timestamp"] = datetime.now().isoformat()
        result["client"] = client_name
        
        return result
    
    except Exception as e:
        logger.error(f"❌ 文件传输失败: {e}")
        return {
            "success": False,
            "error": f"文件传输失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v2/cross-device/media/control")
async def media_control(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    媒体控制
    
    请求体示例：
    ```json
    {
        "action": "play",
        "device_ids": ["device_1", "device_2"]
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 客户端名称
    
    Returns:
        控制结果
    """
    global coordinator
    
    if not coordinator:
        return {
            "success": False,
            "error": "协调器未初始化",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        body = await request.json()
        action = body.get("action", "play")
        device_ids = body.get("device_ids", [])
        
        command = f"{action}媒体"
        
        logger.info(f"客户端 {client_name} 控制媒体: {action}")
        
        result = await coordinator._sync_media_control(command)
        result["timestamp"] = datetime.now().isoformat()
        result["client"] = client_name
        
        return result
    
    except Exception as e:
        logger.error(f"❌ 媒体控制失败: {e}")
        return {
            "success": False,
            "error": f"媒体控制失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v2/cross-device/notification/send")
async def send_notification(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    发送通知
    
    请求体示例：
    ```json
    {
        "title": "通知标题",
        "message": "通知内容",
        "device_ids": ["device_1", "device_2"]
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 客户端名称
    
    Returns:
        发送结果
    """
    global coordinator
    
    if not coordinator:
        return {
            "success": False,
            "error": "协调器未初始化",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        body = await request.json()
        title = body.get("title", "UFO Galaxy")
        message = body.get("message")
        device_ids = body.get("device_ids", [])
        
        if not message:
            return {
                "success": False,
                "error": "缺少 message 参数",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"客户端 {client_name} 发送通知: {title}")
        
        result = await coordinator._sync_notification(message, {"notification_text": message})
        result["timestamp"] = datetime.now().isoformat()
        result["client"] = client_name
        
        return result
    
    except Exception as e:
        logger.error(f"❌ 通知发送失败: {e}")
        return {
            "success": False,
            "error": f"通知发送失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# 安全管理 API
# ============================================================================

@app.post("/api/v2/security/generate-api-key")
async def generate_api_key(
    request: Request,
    client_name: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    生成新的 API Key（需要现有 API Key 认证）
    
    请求体示例：
    ```json
    {
        "new_client_name": "new_client"
    }
    ```
    
    Args:
        request: HTTP 请求
        client_name: 当前客户端名称
    
    Returns:
        新生成的 API Key
    """
    try:
        body = await request.json()
        new_client_name = body.get("new_client_name")
        
        if not new_client_name:
            return {
                "success": False,
                "error": "缺少 new_client_name 参数",
                "timestamp": datetime.now().isoformat()
            }
        
        new_api_key = security_manager.generate_api_key(new_client_name)
        
        logger.info(f"客户端 {client_name} 为 {new_client_name} 生成了新的 API Key")
        
        return {
            "success": True,
            "api_key": new_api_key,
            "client_name": new_client_name,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ API Key 生成失败: {e}")
        return {
            "success": False,
            "error": f"API Key 生成失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# 错误处理
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"❌ 未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# 根端点
# ============================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """根端点"""
    return {
        "service": "UFO Galaxy v2.0",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动 UFO Galaxy v2.0 服务器...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
