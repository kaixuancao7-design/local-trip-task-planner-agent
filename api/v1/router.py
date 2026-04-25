"""API路由配置

统一管理所有API端点的注册。
"""
from fastapi import APIRouter
from api.v1.endpoints import plan, preferences, tools

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(plan.router)
api_router.include_router(preferences.router)
api_router.include_router(tools.router)