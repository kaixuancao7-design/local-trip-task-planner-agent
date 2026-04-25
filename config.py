# 项目配置文件

# 应用配置
APP_NAME = "Local Task Planner Agent"
APP_VERSION = "1.0.0"
DEBUG = True

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000

# 大模型配置
LLM_MODEL = "qwen2.5:7b"
LLM_TEMPERATURE = 0.7

# ChromaDB配置
CHROMA_DB_PATH = "./chroma_db"
CHROMA_COLLECTION_NAME = "user_preferences"

# 地图API配置
MAP_API_KEY = "your_amap_api_key"
MAP_API_URL = "https://restapi.amap.com/v3"

# 天气API配置
WEATHER_API_KEY = "your_weather_api_key"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# 前端配置
FRONTEND_URL = "http://localhost:3000"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"

# 其他配置
DEFAULT_BUDGET_RANGE = [200, 500]
DEFAULT_PLANNING_DURATION = 3600  # 1小时
MAX_PLAN_ACTIVITIES = 10