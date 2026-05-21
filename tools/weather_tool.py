"""工具层 - 天气工具

提供天气查询功能，使用心知天气API。
心知天气官网：https://www.seniverse.com/
"""
import requests
from config.settings import settings
from config.logging_config import log_performance, logger

class WeatherTool:
    """天气工具类 - 心知天气"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_api_url
    
    @log_performance("weather.get_weather")
    def get_weather(self, city: str) -> dict:
        """获取城市当前天气"""
        # 检查API密钥，若无则返回模拟数据
        if not self.api_key or self.api_key == "your_seniverse_api_key":
            logger.info("[WeatherTool] 未配置心知天气API密钥，返回模拟天气数据")
            return self._get_mock_weather(city)
        
        try:
            url = f"{self.base_url}/weather/now.json"
            params = {
                "key": self.api_key,
                "location": city,
                "language": "zh-Hans",
                "unit": "c"
            }
            logger.info(f"调用天气API - URL: {url}, 参数: {params}")
            response = requests.get(url, params=params)
            logger.info(f"天气API响应状态码: {response.status_code}")
            data = response.json()
            logger.info(f"天气API响应数据: {data}")
            
            # 检查是否有results字段
            if "results" in data and len(data["results"]) > 0:
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
                logger.warning(f"天气API返回错误: {data.get('status', '未知错误')}，返回模拟数据")
                return self._get_mock_weather(city)
        except Exception as e:
            logger.warning(f"获取天气失败: {str(e)}，返回模拟数据")
            return self._get_mock_weather(city)
    
    @log_performance("weather.get_forecast")
    def get_forecast(self, city: str, days: int = 3) -> dict:
        """获取城市天气预报"""
        # 检查API密钥，若无则返回模拟数据
        if not self.api_key or self.api_key == "your_seniverse_api_key":
            logger.info("[WeatherTool] 未配置心知天气API密钥，返回模拟天气预报数据")
            return self._get_mock_forecast(city, days)
        
        try:
            url = f"{self.base_url}/weather/daily.json"
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
            
            # 检查是否有results字段
            if "results" in data and len(data["results"]) > 0:
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
                logger.warning(f"天气API返回错误: {data.get('status', '未知错误')}，返回模拟数据")
                return self._get_mock_forecast(city, days)
        except Exception as e:
            logger.warning(f"获取天气预报失败: {str(e)}，返回模拟数据")
            return self._get_mock_forecast(city, days)
    
    def _get_mock_weather(self, city: str) -> dict:
        """返回模拟天气数据"""
        return {
            "city": city,
            "temperature": 26,
            "description": "晴",
            "humidity": 65,
            "wind_speed": 12,
            "wind_direction": "东南风",
            "icon": "01",
            "update_time": "2026-05-21T10:30:00+08:00"
        }
    
    def _get_mock_forecast(self, city: str, days: int = 3) -> dict:
        """返回模拟天气预报数据"""
        import datetime
        forecast = []
        today = datetime.date.today()
        for i in range(days):
            date = today + datetime.timedelta(days=i)
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "high": 28 + i % 3,
                "low": 18 + i % 2,
                "description": ["晴", "多云", "阴", "小雨"][i % 4],
                "icon": str(i + 1).zfill(2)
            })
        return {
            "city": city,
            "forecast": forecast,
            "update_time": "2026-05-21T10:00:00+08:00"
        }
    
