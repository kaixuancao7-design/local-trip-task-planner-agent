"""FastAPI 应用入口

作为整个应用的启动点，负责初始化各层组件并配置路由。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.v1.router import api_router
from config.settings import Settings

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="智能活动规划代理系统 - 感知-决策-执行-记忆四层闭环架构",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """健康检查接口"""
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)