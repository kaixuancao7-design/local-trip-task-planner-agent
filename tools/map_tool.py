"""工具层 - 地图工具

提供地图相关功能，如路线查询、距离计算等。
"""
import requests
from config.settings import settings

class MapTool:
    """地图工具类"""
    
    def __init__(self):
        self.api_key = settings.map_api_key
        self.base_url = settings.map_api_url
    
    def get_route(self, origin: str, destination: str) -> dict:
        """获取路线信息"""
        # 模拟地图API调用
        if not self.api_key or self.api_key == "your_amap_api_key":
            # 如果没有配置真实API密钥，返回模拟数据
            return self._generate_mock_route(origin, destination)
        
        try:
            # 实际调用地图API
            url = f"{self.base_url}/direction/driving"
            params = {
                "origin": origin,
                "destination": destination,
                "key": self.api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                route = data["route"]["paths"][0]
                return {
                    "distance": route.get("distance", 0),
                    "duration": route.get("duration", 0),
                    "travel_time": self._format_duration(route.get("duration", 0)),
                    "steps": route.get("steps", [])
                }
            else:
                return self._generate_mock_route(origin, destination)
        except Exception:
            return self._generate_mock_route(origin, destination)
    
    def search_place(self, keyword: str, city: str = "") -> list:
        """搜索地点"""
        # 模拟地点搜索
        mock_places = [
            {"name": f"{keyword}景点A", "location": "32.0603,118.7969", "type": "景点"},
            {"name": f"{keyword}餐厅B", "location": "32.0574,118.7917", "type": "餐饮"},
            {"name": f"{keyword}购物中心C", "location": "32.0622,118.7895", "type": "购物"}
        ]
        return mock_places
    
    def _generate_mock_route(self, origin: str, destination: str) -> dict:
        """生成模拟路线数据"""
        import random
        travel_time_minutes = random.randint(20, 60)
        return {
            "distance": random.randint(5, 20),
            "duration": travel_time_minutes * 60,
            "travel_time": f"{travel_time_minutes}分钟",
            "steps": []
        }
    
    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}分钟"
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}小时{minutes}分钟"