"""用户操作行为追踪中间件

记录用户的每个请求，包括请求路径、方法、参数、响应时间等信息。
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging_config import logger, SensitiveDataFilter


class UserActivityTracker(BaseHTTPMiddleware):
    """用户操作行为追踪中间件"""
    
    # 不记录的路径（健康检查、静态文件等）
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    ]
    
    # 敏感参数名（不记录值）
    SENSITIVE_PARAMS = [
        "password",
        "token",
        "api_key",
        "secret",
        "authorization"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要记录
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取请求信息
        request_info = await self._extract_request_info(request)
        
        # 记录请求开始
        logger.info(
            f"请求开始 - {request_info['method']} {request_info['path']}",
            extra={"context": {"request": request_info}}
        )
        
        try:
            # 执行请求
            response = await call_next(request)
            
            # 计算响应时间
            duration = time.time() - start_time
            
            # 记录请求完成
            response_info = {
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "success": 200 <= response.status_code < 400
            }
            
            logger.info(
                f"请求完成 - {request_info['method']} {request_info['path']} - "
                f"状态码: {response.status_code} - 耗时: {response_info['duration_ms']}ms",
                extra={"context": {"request": request_info, "response": response_info}}
            )
            
            # 添加响应头记录请求ID（用于追踪）
            response.headers["X-Request-Duration"] = f"{response_info['duration_ms']}ms"
            
            return response
            
        except Exception as e:
            # 计算响应时间
            duration = time.time() - start_time
            
            # 记录请求失败
            logger.error(
                f"请求失败 - {request_info['method']} {request_info['path']} - "
                f"错误: {str(e)} - 耗时: {round(duration * 1000, 2)}ms",
                extra={"context": {"request": request_info, "error": str(e)}}
            )
            raise
    
    async def _extract_request_info(self, request: Request) -> dict:
        """提取请求信息"""
        info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "Unknown"),
        }
        
        # 脱敏查询参数
        info["query_params"] = self._mask_sensitive_params(info["query_params"])
        
        # 记录请求体（仅对POST/PUT/PATCH）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # 尝试解析JSON
                    try:
                        body_json = json.loads(body.decode("utf-8"))
                        info["body"] = self._mask_sensitive_params(body_json)
                    except:
                        # 非JSON格式，记录大小
                        info["body_size"] = len(body)
            except:
                pass
        
        return info
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从X-Forwarded-For获取（反向代理场景）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 从client获取
        if request.client:
            return request.client.host
        
        return "Unknown"
    
    def _mask_sensitive_params(self, params: dict) -> dict:
        """脱敏敏感参数"""
        if not isinstance(params, dict):
            return params
        
        masked = {}
        for key, value in params.items():
            if key.lower() in self.SENSITIVE_PARAMS:
                masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_params(value)
            else:
                # 使用敏感数据过滤器
                masked[key] = SensitiveDataFilter.mask_sensitive_data(str(value))
        
        return masked
