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
    # llm_model: str = "qwen3.5:9b"
    llm_provider: str = "deepseek"  # ollama / deepseek
    llm_model: str = "deepseek-v4-pro"  # deepseek-chat / deepseek-r1 / deepseek-chat-lite
    llm_temperature: float = 0.7
    llm_timeout: int = 30  # LLM调用超时时间（秒）
    llm_max_tokens: int = 2048  # 最大token数
    llm_max_retries: int = 2  # 最大重试次数
    
    # DeepSeek API配置
    deepseek_api_key: str = "your_deepseek_api_key"
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    
    # ChromaDB配置
    chroma_db_path: str = "./data/chroma_db"
    chroma_collection_name: str = "user_preferences"
    
    # 地图API配置
    map_api_key: str = "your_amap_api_key"
    map_api_url: str = "https://restapi.amap.com/v3"
    
    # 天气API配置
    weather_api_key: str = "your_weather_api_key"
    weather_api_url: str = "https://api.seniverse.com/v3"
    
    # 前端配置
    frontend_url: str = "http://localhost:3000"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 业务配置
    default_budget_range: list = [200, 500]
    default_planning_duration: int = 3600
    max_plan_activities: int = 10
    
    # 场景化配置
    default_distance_limit: float = 3.0  # 默认3km范围
    max_waiting_time: int = 20  # 最大排队时间（分钟）
    preferred_rating: float = 4.5  # 最低评分要求
    
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