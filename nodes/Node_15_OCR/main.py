_# main.py for Node_15_OCR

import asyncio
import logging
import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from PIL import Image
import pytesseract
from aiohttp import web
import base64
import io

# ==============================================================================
# 1. 配置和状态定义 (Configuration and Status Definitions)
# ==============================================================================

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Node_15_OCR")

class NodeStatus(Enum):
    """
    节点运行状态枚举
    """
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    DEGRADED = "DEGRADED"

@dataclass
class OCRConfig:
    """
    OCR 节点的配置
    """
    node_name: str = "Node_15_OCR"
    host: str = "0.0.0.0"
    port: int = 8080
    tesseract_cmd_path: Optional[str] = None  # Tesseract-OCR 的可执行文件路径
    default_language: str = "eng"  # 默认识别语言
    supported_languages: List[str] = field(default_factory=lambda: ["eng", "chi_sim", "jpn", "kor"])
    config_file_path: str = "config.json"

# ==============================================================================
# 2. 主服务类 (Main Service Class)
# ==============================================================================

class OCRNode:
    """
    OCR 服务节点主类，负责处理所有核心业务逻辑。
    """

    def __init__(self):
        """
        初始化 OCR 节点。
        """
        self.config = OCRConfig()
        self.status = NodeStatus.CREATED
        self.app = web.Application()
        self._setup_routes()
        logger.info(f"节点 {self.config.node_name} 已创建。")

    async def initialize(self):
        """
        异步初始化节点，加载配置并检查依赖。
        """
        self.status = NodeStatus.INITIALIZING
        logger.info("节点正在初始化...")
        await self.load_config()
        await self.check_dependencies()
        if self.status != NodeStatus.ERROR:
            self.status = NodeStatus.RUNNING
            logger.info(f"节点初始化完成，当前状态: {self.status.value}")
        else:
            logger.error("节点初始化失败。")

    async def load_config(self):
        """
        从 JSON 文件加载配置。如果文件不存在，则使用默认配置。
        """
        logger.info(f"尝试从 {self.config.config_file_path} 加载配置...")
        try:
            if os.path.exists(self.config.config_file_path):
                with open(self.config.config_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.config = OCRConfig(**config_data)
                logger.info("配置加载成功。")
            else:
                logger.warning("配置文件未找到，将使用默认配置。")
                # 可以在这里选择创建默认配置文件
                await self.save_default_config()

            # 如果配置中指定了 Tesseract 路径，则设置它
            if self.config.tesseract_cmd_path and os.path.exists(self.config.tesseract_cmd_path):
                pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd_path
                logger.info(f"Tesseract-OCR 路径已设置为: {self.config.tesseract_cmd_path}")

        except Exception as e:
            self.status = NodeStatus.ERROR
            logger.error(f"加载配置时发生错误: {e}", exc_info=True)

    async def save_default_config(self):
        """
        将当前默认配置保存到文件。
        """
        logger.info(f"正在将默认配置保存到 {self.config.config_file_path}...")
        try:
            config_dict = {
                "node_name": self.config.node_name,
                "host": self.config.host,
                "port": self.config.port,
                "tesseract_cmd_path": self.config.tesseract_cmd_path,
                "default_language": self.config.default_language,
                "supported_languages": self.config.supported_languages,
                "config_file_path": self.config.config_file_path
            }
            with open(self.config.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4, ensure_ascii=False)
            logger.info("默认配置文件创建成功。")
        except Exception as e:
            logger.error(f"保存默认配置文件时出错: {e}", exc_info=True)

    async def check_dependencies(self):
        """
        检查 Tesseract-OCR 是否可用。
        """
        logger.info("正在检查 Tesseract-OCR 依赖...")
        try:
            # 尝试获取 Tesseract 版本信息来验证其是否可用
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract-OCR 已找到，版本: {version}")
        except pytesseract.TesseractNotFoundError:
            self.status = NodeStatus.ERROR
            logger.error("Tesseract-OCR 未安装或未在系统 PATH 中。请安装 Tesseract 并/或在配置文件中指定其路径。")
        except Exception as e:
            self.status = NodeStatus.ERROR
            logger.error(f"检查 Tesseract-OCR 时发生未知错误: {e}", exc_info=True)

    def _setup_routes(self):
        """
        设置 aiohttp 的路由。
        """
        self.app.router.add_post('/ocr', self.handle_ocr_request)
        self.app.router.add_get('/health', self.handle_health_check)
        self.app.router.add_get('/status', self.handle_status_query)
        logger.info("API 路由设置完成。")

    # ==============================================================================
    # 3. 核心业务逻辑 (Core Business Logic)
    # ==============================================================================

    async def perform_ocr(self, image_bytes: bytes, language: str) -> str:
        """
        对给定的图像字节流执行 OCR。

        :param image_bytes: 图像的字节数据。
        :param language: 要使用的识别语言。
        :return: 识别出的文本字符串。
        """
        if self.status != NodeStatus.RUNNING:
            raise RuntimeError("OCR 节点未在运行状态，无法处理请求。")

        if language not in self.config.supported_languages:
            raise ValueError(f"不支持的语言: {language}。支持的语言包括: {self.config.supported_languages}")

        logger.info(f"开始对图像进行 OCR，语言: {language}")
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # 在一个独立的执行器中运行同步的 pytesseract 函数，以避免阻塞事件循环
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(
                None,  # 使用默认的 ThreadPoolExecutor
                lambda: pytesseract.image_to_string(image, lang=language)
            )
            logger.info("OCR 成功完成。")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR 处理过程中发生错误: {e}", exc_info=True)
            raise

    # ==============================================================================
    # 4. API 接口处理 (API Endpoint Handlers)
    # ==============================================================================

    async def handle_ocr_request(self, request: web.Request) -> web.Response:
        """
        处理 /ocr 的 POST 请求。
        请求体应为 JSON，包含 base64 编码的图像和可选的语言参数。
        {'image': 'base64_encoded_string', 'language': 'eng'}
        """
        try:
            data = await request.json()
            if 'image' not in data:
                return web.json_response({'error': '请求体中缺少 \'image\' 字段'}, status=400)

            image_b64 = data['image']
            language = data.get('language', self.config.default_language)

            image_bytes = base64.b64decode(image_b64)
            
            recognized_text = await self.perform_ocr(image_bytes, language)
            
            return web.json_response({'text': recognized_text, 'language': language})

        except json.JSONDecodeError:
            return web.json_response({'error': '无效的 JSON 格式'}, status=400)
        except base64.binascii.Error:
            return web.json_response({'error': '无效的 Base64 编码图像'}, status=400)
        except ValueError as ve:
            return web.json_response({'error': str(ve)}, status=400)
        except Exception as e:
            logger.error(f"处理 OCR 请求时发生内部错误: {e}", exc_info=True)
            return web.json_response({'error': '内部服务器错误'}, status=500)

    async def handle_health_check(self, request: web.Request) -> web.Response:
        """
        处理 /health 的 GET 请求，返回节点健康状态。
        """
        if self.status == NodeStatus.RUNNING:
            return web.json_response({'status': 'ok', 'message': 'OCR Node is running properly.'})
        elif self.status == NodeStatus.DEGRADED:
            return web.json_response({'status': 'degraded', 'message': 'OCR Node is running in a degraded state.'}, status=503)
        else:
            return web.json_response({'status': 'error', 'message': f'OCR Node is in an error state: {self.status.value}'}, status=503)

    async def handle_status_query(self, request: web.Request) -> web.Response:
        """
        处理 /status 的 GET 请求，返回节点的详细状态。
        """
        return web.json_response({
            'node_name': self.config.node_name,
            'status': self.status.value,
            'uptime': 'N/A',  # 在实际应用中可以计算运行时间
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'default_language': self.config.default_language,
                'supported_languages': self.config.supported_languages
            }
        })

    # ==============================================================================
    # 5. 启动和停止 (Start and Stop)
    # ==============================================================================

    async def start(self):
        """
        启动 aiohttp web 服务器。
        """
        await self.initialize()
        if self.status != NodeStatus.RUNNING:
            logger.error("由于初始化失败，节点无法启动。")
            return

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.config.host, self.config.port)
        await site.start()
        logger.info(f"服务已启动，监听地址 http://{self.config.host}:{self.config.port}")

        # 保持服务运行，直到被外部中断
        try:
            while True:
                await asyncio.sleep(3600) # 每小时唤醒一次，或根据需要调整
        except asyncio.CancelledError:
            logger.info("服务正在停止...")
        finally:
            await runner.cleanup()
            self.status = NodeStatus.STOPPED
            logger.info("服务已成功停止。")

async def main():
    """
    主入口函数。
    """
    node = OCRNode()
    try:
        await node.start()
    except Exception as e:
        logger.critical(f"节点启动时发生致命错误: {e}", exc_info=True)
        node.status = NodeStatus.ERROR

if __name__ == "__main__":
    # 为了在本地运行和测试，可以取消下面的注释
    # try:
    #     asyncio.run(main())
    # except KeyboardInterrupt:
    #     logger.info("接收到手动中断信号，正在关闭服务...")
    logger.info("Node_15_OCR main.py 文件已生成，包含完整的服务逻辑。")
    logger.info("要运行此服务，请确保已安装 aiohttp, Pillow, pytesseract 并已正确配置 Tesseract-OCR。")
    logger.info("然后取消 __main__ 中的注释并执行此脚本。")
