"""工具层 - 地图工具

提供地图相关功能，使用高德地图API。
高德地图官网：https://lbs.amap.com/
"""
import requests
from config.settings import settings
from config.logging_config import log_performance, logger

class MapTool:
    """地图工具类 - 高德地图"""
    
    def __init__(self):
        self.api_key = settings.map_api_key
        self.base_url = settings.map_api_url
    
    @log_performance("map.get_route")
    def get_route(self, origin: str, destination: str, city: str = "", 
                  travel_mode: str = "driving") -> dict:
        """获取路线信息（支持多种交通方式）
        
        Args:
            origin: 起点（支持经纬度或地址）
            destination: 终点（支持经纬度或地址）
            city: 城市名称（可选）
            travel_mode: 交通方式（driving-驾车, walking-步行, transit-公交）
        
        Returns:
            路线信息字典
        """
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[MapTool] 未配置高德地图API密钥，返回模拟路线数据")
            return self._get_mock_route(origin, destination, travel_mode)
        
        try:
            origin_coords = origin
            destination_coords = destination
            
            if ',' not in origin:
                geo_origin = self.geocode(origin, city)
                origin_coords = geo_origin["location"]
            
            if ',' not in destination:
                geo_dest = self.geocode(destination, city)
                destination_coords = geo_dest["location"]
            
            if travel_mode == "walking":
                return self._get_walking_route(origin_coords, destination_coords)
            elif travel_mode == "transit":
                return self._get_transit_route(origin_coords, destination_coords, city)
            else:
                return self._get_driving_route(origin_coords, destination_coords)
                
        except Exception as e:
            logger.warning(f"获取路线失败: {str(e)}，返回模拟数据")
            return self._get_mock_route(origin, destination, travel_mode)
    
    def _get_driving_route(self, origin: str, destination: str) -> dict:
        """获取驾车路线"""
        url = f"{self.base_url}/direction/driving"
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key,
            "extensions": "all"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1":
            route = data["route"]["paths"][0]
            return {
                "distance": int(route.get("distance", 0)),
                "duration": int(route.get("duration", 0)),
                "travel_time": self._format_duration(int(route.get("duration", 0))),
                "distance_text": f"{int(route.get('distance', 0)) / 1000:.1f}公里",
                "mode": "driving",
                "steps": self._parse_driving_steps(route.get("steps", []))
            }
        else:
            logger.warning(f"驾车路线API返回错误: {data.get('info', '未知错误')}")
            return self._get_mock_route(origin, destination, "driving")
    
    def _get_walking_route(self, origin: str, destination: str) -> dict:
        """获取步行路线"""
        url = f"{self.base_url}/direction/walking"
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
                "distance": int(route.get("distance", 0)),
                "duration": int(route.get("duration", 0)),
                "travel_time": self._format_duration(int(route.get("duration", 0))),
                "distance_text": f"{int(route.get('distance', 0)) / 1000:.1f}公里",
                "mode": "walking",
                "steps": self._parse_walking_steps(route.get("steps", []))
            }
        else:
            logger.warning(f"步行路线API返回错误: {data.get('info', '未知错误')}")
            return self._get_mock_route(origin, destination, "walking")
    
    def _get_transit_route(self, origin: str, destination: str, city: str = "") -> dict:
        """获取公交路线"""
        url = f"{self.base_url}/direction/transit/integrated"
        params = {
            "origin": origin,
            "destination": destination,
            "city": city,
            "key": self.api_key,
            "extensions": "all"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "1":
            route = data["route"]
            return {
                "distance": int(route.get("distance", 0)),
                "duration": int(route.get("duration", 0)),
                "travel_time": self._format_duration(int(route.get("duration", 0))),
                "distance_text": f"{int(route.get('distance', 0)) / 1000:.1f}公里",
                "mode": "transit",
                "walking_distance": int(route.get("walking_distance", 0)),
                "transit_count": int(route.get("transit_count", 0)),
                "lines": self._parse_transit_lines(route.get("lines", []))
            }
        else:
            logger.warning(f"公交路线API返回错误: {data.get('info', '未知错误')}")
            return self._get_mock_route(origin, destination, "transit")
    
    def _parse_driving_steps(self, steps: list) -> list:
        """解析驾车路线步骤"""
        parsed_steps = []
        for step in steps:
            parsed_steps.append({
                "instruction": step.get("instruction", ""),
                "distance": int(step.get("distance", 0)),
                "duration": int(step.get("duration", 0)),
                "action": step.get("action", ""),
                "road": step.get("road", "")
            })
        return parsed_steps
    
    def _parse_walking_steps(self, steps: list) -> list:
        """解析步行路线步骤"""
        parsed_steps = []
        for step in steps:
            parsed_steps.append({
                "instruction": step.get("instruction", ""),
                "distance": int(step.get("distance", 0)),
                "duration": int(step.get("duration", 0)),
                "action": step.get("action", "")
            })
        return parsed_steps
    
    def _parse_transit_lines(self, lines: list) -> list:
        """解析公交路线信息"""
        parsed_lines = []
        for line in lines:
            parsed_lines.append({
                "type": line.get("type", ""),
                "name": line.get("name", ""),
                "line_name": line.get("line_name", ""),
                "departure_stop": line.get("departure_stop", ""),
                "arrival_stop": line.get("arrival_stop", ""),
                "stop_count": int(line.get("stop_count", 0))
            })
        return parsed_lines
    
    @log_performance("map.search_place")
    def search_place(self, keyword: str, city: str = "") -> list:
        """搜索地点（POI搜索）
        
        Args:
            keyword: 搜索关键词
            city: 城市名称（可选）
        
        Returns:
            地点列表
        """
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[MapTool] 未配置高德地图API密钥，返回模拟地点数据")
            return self._get_mock_places(keyword)
        
        try:
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
                logger.warning(f"地图API返回错误: {data.get('info', '未知错误')}，返回模拟数据")
                return self._get_mock_places(keyword)
        except Exception as e:
            logger.warning(f"搜索地点失败: {str(e)}，返回模拟数据")
            return self._get_mock_places(keyword)
    
    @log_performance("map.geocode")
    def geocode(self, address: str, city: str = "") -> dict:
        """地址转经纬度（地理编码）
        
        Args:
            address: 地址字符串
            city: 城市名称（可选）
        
        Returns:
            经纬度信息
        """
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[MapTool] 未配置高德地图API密钥，返回模拟地理编码数据")
            return self._get_mock_geocode(address)
        
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
            logger.warning(f"地理编码失败: {data.get('info', '未找到地址')}，返回模拟数据")
            return self._get_mock_geocode(address)
        except Exception as e:
            logger.warning(f"地理编码失败: {str(e)}，返回模拟数据")
            return self._get_mock_geocode(address)
    
    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}分钟"
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}小时{minutes}分钟"
    
    def _parse_route_steps(self, steps: list) -> list:
        """解析路线步骤"""
        parsed_steps = []
        for step in steps:
            parsed_steps.append({
                "instruction": step.get("instruction", ""),
                "distance": step.get("distance", ""),
                "duration": step.get("duration", ""),
                "action": step.get("action", "")
            })
        return parsed_steps
    
    def _get_mock_route(self, origin: str, destination: str, travel_mode: str = "driving") -> dict:
        """返回模拟路线数据"""
        if travel_mode == "walking":
            return {
                "distance": 2000,
                "duration": 2400,
                "travel_time": "40分钟",
                "distance_text": "2.0公里",
                "mode": "walking",
                "steps": [
                    {"instruction": f"从{origin}出发，直行", "distance": 500, "duration": 600, "action": "go_straight"},
                    {"instruction": "经过红绿灯，继续直行", "distance": 800, "duration": 960, "action": "go_straight"},
                    {"instruction": "左转进入步行街", "distance": 400, "duration": 480, "action": "turn_left"},
                    {"instruction": f"到达{destination}", "distance": 300, "duration": 360, "action": "arrive"}
                ]
            }
        elif travel_mode == "transit":
            return {
                "distance": 5000,
                "duration": 2700,
                "travel_time": "45分钟",
                "distance_text": "5.0公里",
                "mode": "transit",
                "walking_distance": 800,
                "transit_count": 1,
                "lines": [
                    {"type": "地铁", "name": "地铁2号线", "line_name": "2号线", 
                     "departure_stop": "新街口站", "arrival_stop": "夫子庙站", "stop_count": 4}
                ]
            }
        else:
            return {
                "distance": 3500,
                "duration": 1800,
                "travel_time": "30分钟",
                "distance_text": "3.5公里",
                "mode": "driving",
                "steps": [
                    {"instruction": f"从{origin}出发", "distance": 100, "duration": 60, "action": "start", "road": ""},
                    {"instruction": "直行200米", "distance": 200, "duration": 120, "action": "go_straight", "road": "中山路"},
                    {"instruction": "右转进入主路", "distance": 50, "duration": 30, "action": "turn_right", "road": "汉中路"},
                    {"instruction": "直行3000米", "distance": 3000, "duration": 1440, "action": "go_straight", "road": "汉中路"},
                    {"instruction": f"到达{destination}", "distance": 150, "duration": 60, "action": "arrive", "road": ""}
                ]
            }
    
    def _get_mock_places(self, keyword: str) -> list:
        """返回模拟地点数据"""
        mock_places = [
            {"name": f"{keyword}广场", "location": "118.783799,32.060255", "address": "南京市鼓楼区中山路1号", "type": "购物服务", "typecode": "141201", "distance": 500},
            {"name": f"{keyword}购物中心", "location": "118.785678,32.058976", "address": "南京市玄武区新街口步行街", "type": "购物服务", "typecode": "141201", "distance": 800},
            {"name": f"{keyword}商城", "location": "118.778934,32.062345", "address": "南京市秦淮区夫子庙商圈", "type": "购物服务", "typecode": "141201", "distance": 1200}
        ]
        return mock_places
    
    def _get_mock_geocode(self, address: str) -> dict:
        """返回模拟地理编码数据"""
        return {
            "formatted_address": address,
            "location": "118.783799,32.060255",
            "province": "江苏省",
            "city": "南京市",
            "district": "鼓楼区"
        }
