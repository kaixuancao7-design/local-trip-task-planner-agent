"""核心模块 - 全局异常处理中间件

提供统一的异常处理机制，捕获并处理应用中未处理的异常，返回标准化的错误响应。
"""
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from config.logging_config import logger


class GlobalExceptionHandler(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # 处理404错误（路由未找到）
            if response.status_code == 404:
                logger.warning(f"404错误 - 请求路径: {request.url.path}")
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": {
                            "code": 404,
                            "message": "请求的资源未找到",
                            "type": "NotFound"
                        }
                    }
                )
            
            return response
            
        except HTTPException as e:
            # 处理HTTP异常（已定义的业务异常）
            logger.warning(f"HTTP异常 - 状态码: {e.status_code}, 详情: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": e.status_code,
                        "message": str(e.detail),
                        "type": "HTTPException"
                    }
                }
            )
        except ValueError as e:
            # 处理值错误
            logger.error(f"值错误 - 请求路径: {request.url.path}, 错误: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {
                        "code": 400,
                        "message": str(e),
                        "type": "ValueError"
                    }
                }
            )
        except Exception as e:
            # 处理未知异常
            logger.error(f"未知异常 - 请求路径: {request.url.path}, 错误: {e}")
            logger.error(f"异常堆栈:\n{traceback.format_exc()}")
            
            # 生产环境不返回详细错误信息
            from config.settings import settings
            error_message = "服务器内部错误，请稍后重试" if not settings.debug else str(e)
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": 500,
                        "message": error_message,
                        "type": "InternalServerError"
                    }
                }
            )


def register_middlewares(app):
    """注册所有中间件"""
    # 注册用户操作行为追踪中间件
    from core.activity_tracker import UserActivityTracker
    app.add_middleware(UserActivityTracker)
    
    # 注册全局异常处理中间件
    app.add_middleware(GlobalExceptionHandler)
    
    # 注册Starlette异常处理器（处理422验证错误等）
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"Starlette HTTP异常 - 状态码: {exc.status_code}, 详情: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": str(exc.detail),
                    "type": "HTTPException"
                }
            }
        )
    
    # 注册422验证错误处理器
    from fastapi.exceptions import RequestValidationError
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"请求验证失败 - 请求路径: {request.url.path}, 错误: {exc.errors()}")
        error_messages = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "请求参数验证失败",
                    "type": "ValidationError",
                    "details": error_messages
                }
            }
        )
    
    logger.info("全局异常处理中间件已注册")
    logger.info("用户操作行为追踪中间件已注册")
