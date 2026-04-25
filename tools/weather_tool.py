"""工具层 - 天气工具

提供天气查询功能，使用心知天气API。
心知天气官网：https://www.seniverse.com/
"""
import requests
from config.settings import settings

class WeatherTool:
    """天气工具类 - 心知天气"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_api_url
    
    def get_weather(self, city: str) -> dict:
        """获取城市当前天气"""
        # 如果没有配置API密钥，返回模拟数据
        if not self.api_key or self.api_key == "your_seniverse_api_key_here":
            return self._generate_mock_weather(city)
        
        try:
            url = f"{self.base_url}/now.json"
            params = {
                "key": self.api_key,
                "location": city,
                "language": "zh-Hans",
                "unit": "c"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("code") == "200":
                weather_data = data["results"][0]
                return {
                    "city": weather_data["location"]["name"],
                    "temperature": int(weather_data["now"]["temperature"]),
                    "description": weather_data["now"]["text"],
                    "humidity": weather_data["now"].get("humidity", 0),
                    "wind_speed": weather_data["now"].get("wind_speed", 0),
                    "wind_direction": weather_data["now"].get("wind_direction", ""),
                    "icon": weather_data["now"].get("code", ""),
                    "update_time": weather_data["last_update"]
                }
            else:
                return self._generate_mock_weather(city)
        except Exception as e:
            print(f"天气API调用失败: {e}")
            return self._generate_mock_weather(city)
    
    def get_forecast(self, city: str, days: int = 3) -> dict:
        """获取城市天气预报"""
        if not self.api_key or self.api_key == "your_seniverse_api_key_here":
            return self._generate_mock_forecast(city, days)
        
        try:
            url = f"{self.base_url}/daily.json"
            params = {
                "key": self.api_key,
                "location": city,
                "language": "zh-Hans",
                "unit": "c",
                "start": 0,
                "days": days
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("code") == "200":
                results = data["results"][0]
                forecast = []
                for day in results["daily"]:
                    forecast.append({
                        "date": day["date"],
                        "high": int(day["high"]),
                        "low": int(day["low"]),
                        "description": day["text_day"],
                        "icon": day["code_day"]
                    })
                return {
                    "city": results["location"]["name"],
                    "forecast": forecast,
                    "update_time": results["last_update"]
                }
            else:
                return self._generate_mock_forecast(city, days)
        except Exception as e:
            print(f"天气预报API调用失败: {e}")
            return self._generate_mock_forecast(city, days)
    
    def _generate_mock_weather(self, city: str) -> dict:
        """生成模拟天气数据"""
        import random
        descriptions = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "晴转多云"]
        return {
            "city": city,
            "temperature": random.randint(15, 35),
            "description": random.choice(descriptions),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(1, 10),
            "wind_direction": random.choice(["北风", "南风", "东风", "西风"]),
            "icon": "01",
            "update_time": "2024-01-01T12:00:00+08:00"
        }
    
    def _generate_mock_forecast(self, city: str, days: int) -> dict:
        """生成模拟天气预报数据"""
        import random
        from datetime import datetime, timedelta
        
        descriptions = ["晴", "多云", "阴", "小雨"]
        forecast = []
        today = datetime.now()
        
        for i in range(days):
            date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                "date": date,
                "high": random.randint(18, 35),
                "low": random.randint(5, 20),
                "description": random.choice(descriptions),
                "icon": str(random.randint(1, 4))
            })
        
        return {
            "city": city,
            "forecast": forecast,
            "update_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }