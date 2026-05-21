"""日志配置模块

配置应用的日志记录系统，支持控制台输出和文件输出。
支持日志轮转（按日期和大小）、性能监控、敏感信息脱敏。
"""
import logging
import logging.handlers
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import time
from config.settings import settings


class SensitiveDataFilter:
    """敏感数据过滤器"""
    
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'password'),
        (r'api_key["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'api_key'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'token'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'secret'),
        (r'authorization["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'authorization'),
    ]
    
    @classmethod
    def mask_sensitive_data(cls, message: str) -> str:
        """脱敏敏感数据"""
        if not isinstance(message, str):
            message = str(message)
        
        masked_message = message
        for pattern, field_name in cls.SENSITIVE_PATTERNS:
            masked_message = re.sub(
                pattern,
                f'{field_name}=***MASKED***',
                masked_message,
                flags=re.IGNORECASE
            )
        
        return masked_message


class ContextFormatter(logging.Formatter):
    """支持上下文数据的日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 添加额外字段
        record.timestamp = datetime.fromtimestamp(record.created).isoformat()
        record.module_name = record.module
        record.function_name = record.funcName
        record.line_number = record.lineno
        
        # 脱敏处理
        if hasattr(record, 'msg') and record.msg:
            record.msg = SensitiveDataFilter.mask_sensitive_data(str(record.msg))
        
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """JSON格式日志输出（便于日志分析）"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": SensitiveDataFilter.mask_sensitive_data(str(record.msg)),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外上下文
        if hasattr(record, 'context') and record.context:
            log_data['context'] = record.context
        
        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.slow_threshold = 1.0  # 慢操作阈值（秒）
    
    def record(self, operation: str, duration: float, metadata: Optional[Dict] = None):
        """记录性能指标"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "metadata": metadata or {}
        }
        self.metrics[operation].append(metric)
        
        # 记录慢操作
        if duration > self.slow_threshold:
            logger.warning(
                f"慢操作检测: {operation} 耗时 {duration:.2f}秒",
                extra={"context": {"operation": operation, "duration": duration, "metadata": metadata}}
            )
    
    def get_stats(self, operation: str) -> Dict[str, Any]:
        """获取操作统计信息"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        durations = [m['duration'] for m in self.metrics[operation]]
        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations)
        }


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def log_performance(operation_name: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record(operation, duration, {"status": "success"})
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record(operation, duration, {"status": "error", "error": str(e)})
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record(operation, duration, {"status": "success"})
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record(operation, duration, {"status": "error", "error": str(e)})
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


class PerformanceContext:
    """性能监控上下文管理器"""
    
    def __init__(self, operation: str, metadata: Optional[Dict] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "error" if exc_type else "success"
        self.metadata["status"] = status
        if exc_type:
            self.metadata["error"] = str(exc_val)
        performance_monitor.record(self.operation, duration, self.metadata)
        return False


def setup_logging():
    """配置日志系统"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 创建详细日志格式（包含模块、函数、行号）
    detailed_formatter = ContextFormatter(
        "%(asctime)s [%(levelname)-8s] %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建简单日志格式（控制台用）
    simple_formatter = ContextFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # JSON格式（用于日志分析）
    json_formatter = JsonFormatter()
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # 清除默认处理器
    
    # 1. 控制台处理器（支持中文）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 主日志文件处理器（按大小轮转）
    log_file_path = log_dir / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8-sig"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # 3. 错误日志文件（按日期轮转）
    error_log_path = log_dir / "error.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        error_log_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8-sig"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. JSON格式日志（用于分析）
    json_log_path = log_dir / "app.json"
    json_handler = logging.handlers.RotatingFileHandler(
        json_log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8-sig"
    )
    json_handler.setLevel(log_level)
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return root_logger


# 创建全局日志记录器
logger = setup_logging()
