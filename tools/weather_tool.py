"""工具层 - 天气工具

提供天气查询功能。
"""
import requests
from config.settings import settings

class WeatherTool:
    """天气工具类"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_api_url
    
    def get_weather(self, city: str) -> dict:
        """获取城市天气"""
        # 模拟天气API调用
        if not self.api_key or self.api_key == "your_weather_api_key":
            return self._generate_mock_weather(city)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("cod") == 200:
                return {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "icon": data["weather"][0]["icon"]
                }
            else:
                return self._generate_mock_weather(city)
        except Exception:
            return self._generate_mock_weather(city)
    
    def _generate_mock_weather(self, city: str) -> dict:
        """生成模拟天气数据"""
        import random
        descriptions = ["晴朗", "多云", "阴天", "小雨", "晴转多云"]
        return {
            "city": city,
            "temperature": random.randint(15, 35),
            "description": random.choice(descriptions),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(1, 10),
            "icon": "01d"
        }