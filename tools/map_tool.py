"""工具层 - 地图工具

提供地图相关功能，使用高德地图API。
高德地图官网：https://lbs.amap.com/
"""
import requests
from config.settings import settings
from config.logging_config import log_performance

class MapTool:
    """地图工具类 - 高德地图"""
    
    def __init__(self):
        self.api_key = settings.map_api_key
        self.base_url = settings.map_api_url
    
    @log_performance("map.get_route")
    def get_route(self, origin: str, destination: str, city: str = "") -> dict:
        """获取驾车路线信息
        
        Args:
            origin: 起点（支持经纬度或地址）
            destination: 终点（支持经纬度或地址）
            city: 城市名称（可选）
        
        Returns:
            路线信息字典
        """
        # 如果没有配置真实API密钥，返回模拟数据
        if not self.api_key or self.api_key == "your_amap_api_key_here":
            return self._generate_mock_route(origin, destination)
        
        try:
            # 调用高德地图驾车路线API
            url = f"{self.base_url}/direction/driving"
            params = {
                "origin": origin,
                "destination": destination,
                "city": city,
                "key": self.api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                route = data["route"]["paths"][0]
                return {
                    "distance": int(route.get("distance", 0)),
                    "duration": int(route.get("duration", 0)),
                    "travel_time": self._format_duration(int(route.get("duration", 0))),
                    "steps": route.get("steps", []),
                    "origin": origin,
                    "destination": destination
                }
            else:
                return self._generate_mock_route(origin, destination)
        except Exception as e:
            print(f"高德地图API调用失败: {e}")
            return self._generate_mock_route(origin, destination)
    
    @log_performance("map.search_place")
    def search_place(self, keyword: str, city: str = "") -> list:
        """搜索地点（POI搜索）
        
        Args:
            keyword: 搜索关键词
            city: 城市名称（可选）
        
        Returns:
            地点列表
        """
        if not self.api_key or self.api_key == "your_amap_api_key_here":
            return self._generate_mock_places(keyword)
        
        try:
            # 调用高德地图POI搜索API
            url = f"{self.base_url}/place/text"
            params = {
                "keywords": keyword,
                "city": city,
                "key": self.api_key,
                "types": "",
                "offset": 10,
                "page": 1
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                places = []
                for poi in data.get("pois", []):
                    places.append({
                        "name": poi.get("name", ""),
                        "location": poi.get("location", ""),
                        "address": poi.get("address", ""),
                        "type": poi.get("type", ""),
                        "typecode": poi.get("typecode", ""),
                        "distance": poi.get("distance", 0)
                    })
                return places
            else:
                return self._generate_mock_places(keyword)
        except Exception as e:
            print(f"高德地图POI搜索失败: {e}")
            return self._generate_mock_places(keyword)
    
    @log_performance("map.geocode")
    def geocode(self, address: str, city: str = "") -> dict:
        """地址转经纬度（地理编码）
        
        Args:
            address: 地址字符串
            city: 城市名称（可选）
        
        Returns:
            经纬度信息
        """
        if not self.api_key or self.api_key == "your_amap_api_key_here":
            return self._generate_mock_geocode(address)
        
        try:
            url = f"{self.base_url}/geocode/geo"
            params = {
                "address": address,
                "city": city,
                "key": self.api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                geocodes = data.get("geocodes", [])
                if geocodes:
                    return {
                        "formatted_address": geocodes[0].get("formatted_address", ""),
                        "location": geocodes[0].get("location", ""),
                        "province": geocodes[0].get("province", ""),
                        "city": geocodes[0].get("city", ""),
                        "district": geocodes[0].get("district", "")
                    }
            return self._generate_mock_geocode(address)
        except Exception as e:
            print(f"高德地图地理编码失败: {e}")
            return self._generate_mock_geocode(address)
    
    def _generate_mock_places(self, keyword: str) -> list:
        """生成模拟地点数据"""
        mock_places = [
            {"name": f"{keyword}公园", "location": "32.0603,118.7969", "address": "南京市玄武区", "type": "景点", "typecode": "100000", "distance": 1000},
            {"name": f"{keyword}美食城", "location": "32.0574,118.7917", "address": "南京市秦淮区", "type": "餐饮", "typecode": "050000", "distance": 2000},
            {"name": f"{keyword}购物中心", "location": "32.0622,118.7895", "address": "南京市鼓楼区", "type": "购物", "typecode": "060000", "distance": 1500}
        ]
        return mock_places
    
    def _generate_mock_geocode(self, address: str) -> dict:
        """生成模拟地理编码数据"""
        return {
            "formatted_address": address,
            "location": "32.0603,118.7969",
            "province": "江苏省",
            "city": "南京市",
            "district": "玄武区"
        }
    
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