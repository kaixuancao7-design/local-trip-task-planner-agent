"""日志配置模块

配置应用的日志记录系统，支持控制台输出和文件输出。
"""
import logging
import sys
from pathlib import Path
from config.settings import settings

def setup_logging():
    """配置日志系统"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 创建日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # 清除默认处理器
    
    # 创建控制台处理器（支持中文）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 创建文件处理器（支持中文，使用utf-8编码）
    # 使用绝对路径确保日志文件写入正确位置
    log_file_path = log_dir / "app.log"
    
    file_handler = logging.FileHandler(
        log_file_path,
        encoding="utf-8-sig",
        mode="a"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return root_logger

# 创建全局日志记录器
logger = setup_logging()
