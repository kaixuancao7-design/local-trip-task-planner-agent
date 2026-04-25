"""配置管理模块

使用Pydantic管理应用配置，支持从环境变量加载。
"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "Local Task Planner Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 大模型配置
    llm_model: str = "qwen2.5:7b"
    llm_temperature: float = 0.7
    
    # ChromaDB配置
    chroma_db_path: str = "./data/chroma_db"
    chroma_collection_name: str = "user_preferences"
    
    # 地图API配置
    map_api_key: str = "your_amap_api_key"
    map_api_url: str = "https://restapi.amap.com/v3"
    
    # 天气API配置
    weather_api_key: str = "your_weather_api_key"
    weather_api_url: str = "https://api.openweathermap.org/data/2.5"
    
    # 前端配置
    frontend_url: str = "http://localhost:3000"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 业务配置
    default_budget_range: list = [200, 500]
    default_planning_duration: int = 3600
    max_plan_activities: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建必要的目录
def init_directories():
    directories = [
        "./data",
        "./data/chroma_db",
        "./logs",
        "./api/v1/endpoints",
        "./core",
        "./tools",
        "./models",
        "./config"
    ]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

init_directories()

settings = Settings()