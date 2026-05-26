"""工具层 - 智能餐厅检索工具

提供智能餐厅搜索功能，支持多种餐饮需求匹配:
- 减肥餐（低脂、低糖、健康餐）
- 多人团建（大桌、包间、套餐）
- 亲子友好（儿童餐、高椅）
- 情侣约会（氛围、私密）
"""

import requests
import random
from config.settings import settings
from config.logging_config import log_performance, logger

class RestaurantSearchTool:
    """智能餐厅检索工具类 - 基于高德地图API"""
    
    def __init__(self):
        self.api_key = settings.map_api_key
        self.base_url = settings.map_api_url
        
        # 餐饮类型映射 - 根据官方POI编码分类优化
        self.cuisine_types = {
            "无特别偏好": ["中餐", "西餐", "本地特色", "火锅", "烧烤", "自助餐"],
            "减肥餐": ["轻食", "沙拉", "健康餐", "低脂", "素食", "减脂餐", "营养餐", "有机", "健身餐"],
            "多人团建": ["川菜", "火锅", "烧烤", "自助餐", "粤菜", "湘菜", "东北菜", "海鲜", "融合菜"],
            "亲子友好": ["西餐", "日料", "披萨", "汉堡", "甜品", "蛋糕", "冰淇淋", "儿童餐", "亲子餐厅"],
            "情侣约会": ["西餐", "日料", "法餐", "意餐", "咖啡厅", "牛排", "地中海菜", "浪漫餐厅"],
            "本地特色": ["地方菜", "老字号", "特色小吃", "南京菜", "金陵菜", "江浙菜", "上海菜"],
            "商务宴请": ["粤菜", "江浙菜", "高端餐厅", "私房菜", "海鲜", "潮州菜", "台湾菜"],
            "夜宵": ["烧烤", "串串", "小龙虾", "大排档", "深夜食堂"],
            "休闲下午茶": ["咖啡", "咖啡厅", "甜品", "蛋糕", "茶餐厅"],
            "异国风味": ["日料", "韩国料理", "泰国菜", "越南菜", "印度菜", "美式"]
        }
        
        # 菜系编码（高德地图POI类型）- 根据官方文档 V1.06_20230208 更新
        # 编码规则: 501xx=中餐厅, 502xx=外国餐厅, 503xx=快餐厅, 504xx=休闲餐饮, 505xx=咖啡厅, 509xx=甜品店
        self.cuisine_codes = {
            # 默认分类
            "中餐": "50100",
            "西餐": "50201",
            
            # 中餐厅 (501xx)
            "川菜": "50102",
            "粤菜": "50103",
            "湘菜": "50108",
            "东北菜": "50113",
            "北京菜": "50111",
            "江苏菜": "50105",
            "浙江菜": "50106",
            "上海菜": "50107",
            "火锅": "50117",
            "海鲜": "50119",
            "素食": "50120",
            "清真": "50121",
            "台湾菜": "50122",
            "潮州菜": "50123",
            "地方菜": "50118",
            "特色小吃": "50118",
            "私房菜": "50100",
            "高端餐厅": "50101",
            
            # 外国餐厅 (502xx)
            "西餐": "50201",
            "日料": "50202",
            "韩国料理": "50203",
            "法餐": "50204",
            "意餐": "50205",
            "泰国菜": "50206",
            "越南菜": "50206",
            "美式": "50208",
            "印度菜": "50209",
            "地中海菜": "50207",
            "披萨": "50201",
            "汉堡": "50208",
            "牛排": "50211",
            
            # 快餐厅 (503xx)
            "快餐": "50300",
            "茶餐厅": "50305",
            "自助餐": "50300",
            
            # 休闲餐饮 (504xx)
            "轻食": "50400",
            "沙拉": "50400",
            "健康餐": "50400",
            "低脂": "50400",
            
            # 咖啡厅 (505xx)
            "咖啡": "50500",
            "咖啡厅": "50500",
            
            # 甜品店 (509xx)
            "甜品": "50900",
            "蛋糕": "50900",
            "冰淇淋": "50700",
            
            # 烧烤（使用中餐厅分类）
            "烧烤": "50100",
            "串串": "50100",
            "小龙虾": "50100"
        }
    
    @log_performance("restaurant.search")
    def search_restaurants(self, requirement: str = "减肥餐", city: str = "南京", 
                         radius: float = 3.0, limit: int = 10) -> list:
        """搜索餐厅
        
        Args:
            requirement: 餐饮需求类型（减肥餐/多人团建/亲子友好/情侣约会/本地特色）
            city: 城市名称
            radius: 搜索半径（公里）
            limit: 返回数量限制
        
        Returns:
            餐厅列表
        """
        logger.info(f"[RestaurantSearchTool] 搜索餐厅 - 需求: {requirement}, 城市: {city}, 半径: {radius}km")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[RestaurantSearchTool] 未配置API密钥，返回模拟数据")
            return self._get_mock_restaurants(requirement, city, limit)
        
        try:
            # 处理空需求，默认使用"无特别偏好"
            if not requirement or requirement in ["无", "", " ", "无特别偏好"]:
                requirement = "无特别偏好"
            keywords = self.cuisine_types.get(requirement, ["餐厅"])
            all_results = []
            
            for keyword in keywords[:3]:
                typecode = self.cuisine_codes.get(keyword, "")
                results = self._search_by_cuisine(keyword, typecode, city, radius, limit)
                all_results.extend(results)
            
            unique_results = self._deduplicate_results(all_results)
            sorted_results = sorted(unique_results, key=lambda x: x.get("distance", float('inf')))
            
            # 如果搜索结果为空，使用模拟数据
            if len(sorted_results) == 0:
                logger.info("[RestaurantSearchTool] 未找到餐厅，使用模拟数据")
                return self._get_mock_restaurants(requirement, city, limit)
            
            logger.info(f"[RestaurantSearchTool] 搜索完成 - 找到 {len(sorted_results)} 家餐厅")
            return sorted_results[:limit]
            
        except Exception as e:
            logger.warning(f"搜索餐厅失败: {str(e)}，返回模拟数据")
            return self._get_mock_restaurants(requirement, city, limit)
    
    @log_performance("restaurant.search_by_cuisine")
    def search_by_cuisine(self, cuisine: str, city: str = "南京", radius: float = 3.0, 
                         limit: int = 10) -> list:
        """按菜系搜索餐厅
        
        Args:
            cuisine: 菜系名称（川菜/火锅/西餐/日料等）
            city: 城市名称
            radius: 搜索半径（公里）
            limit: 返回数量限制
        
        Returns:
            餐厅列表
        """
        logger.info(f"[RestaurantSearchTool] 按菜系搜索 - 菜系: {cuisine}, 城市: {city}")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[RestaurantSearchTool] 未配置API密钥，返回模拟数据")
            return self._get_mock_restaurants_by_cuisine(cuisine, city, limit)
        
        try:
            typecode = self.cuisine_codes.get(cuisine, "")
            results = self._search_by_cuisine(cuisine, typecode, city, radius, limit)
            
            logger.info(f"[RestaurantSearchTool] 按菜系搜索完成 - 找到 {len(results)} 家餐厅")
            return results
        except Exception as e:
            logger.warning(f"按菜系搜索失败: {str(e)}，返回模拟数据")
            return self._get_mock_restaurants_by_cuisine(cuisine, city, limit)
    
    @log_performance("restaurant.get_detail")
    def get_restaurant_detail(self, place_id: str) -> dict:
        """获取餐厅详情
        
        Args:
            place_id: POI ID
        
        Returns:
            餐厅详情信息
        """
        logger.info(f"[RestaurantSearchTool] 获取餐厅详情 - place_id: {place_id}")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[RestaurantSearchTool] 未配置API密钥，返回模拟详情")
            return self._get_mock_restaurant_detail(place_id)
        
        try:
            url = f"{self.base_url}/place/detail"
            params = {
                "id": place_id,
                "key": self.api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                poi = data.get("poi", {})
                return {
                    "name": poi.get("name", ""),
                    "address": poi.get("address", ""),
                    "location": poi.get("location", ""),
                    "type": poi.get("type", ""),
                    "rating": poi.get("rating", ""),
                    "cost": poi.get("cost", ""),
                    "tel": poi.get("tel", ""),
                    "business_time": poi.get("business_time", ""),
                    "photos": poi.get("photos", []),
                    "description": poi.get("description", ""),
                    "parking": poi.get("parking_type", ""),
                    "wifi": poi.get("wifi", "")
                }
            else:
                logger.warning(f"获取餐厅详情失败: {data.get('info', '未知错误')}")
                return self._get_mock_restaurant_detail(place_id)
        except Exception as e:
            logger.warning(f"获取餐厅详情失败: {str(e)}，返回模拟数据")
            return self._get_mock_restaurant_detail(place_id)
    
    def _search_by_cuisine(self, keyword: str, typecode: str, city: str, radius: float, limit: int) -> list:
        """内部方法：按菜系搜索"""
        url = f"{self.base_url}/place/text"
        params = {
            "keywords": keyword,
            "city": city,
            "key": self.api_key,
            "types": typecode if typecode else "50100",  # 默认餐饮类型（新编码格式）
            "offset": 0,
            "limit": min(limit, 50),  # 扩大默认限制，最多50条
            "extensions": "all",
            "citylimit": "true"  # 限制在指定城市内搜索
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") != "1":
            return []
        
        results = []
        for poi in data.get("pois", []):
            # 处理distance字段，可能是列表或字符串
            distance = poi.get("distance", 0)
            if isinstance(distance, list):
                distance = distance[0] if distance else 0
            try:
                distance = int(distance)
            except (ValueError, TypeError):
                distance = random.randint(300, int(radius * 1000))
            
            results.append({
                "name": poi.get("name", ""),
                "location": poi.get("location", ""),
                "address": poi.get("address", ""),
                "type": poi.get("type", ""),
                "rating": poi.get("rating", ""),
                "cost": poi.get("cost", ""),
                "distance": distance,
                "business_time": poi.get("business_time", ""),
                "tel": poi.get("tel", ""),
                "id": poi.get("id", "")
            })
        
        return results
    
    def _deduplicate_results(self, results: list) -> list:
        """去重结果"""
        seen = set()
        unique = []
        for r in results:
            name = r.get("name", "")
            if name not in seen:
                seen.add(name)
                unique.append(r)
        return unique
    
    def _get_mock_restaurants(self, requirement: str, city: str, limit: int) -> list:
        """返回模拟餐厅数据"""
        mock_data = {
            "减肥餐": [
                {"name": f"{city}轻食沙拉屋", "location": "118.783799,32.060255", "address": f"{city}市鼓楼区健康路1号", 
                 "type": "轻食餐厅", "rating": "4.8", "cost": "30-50元", "distance": 500, 
                 "business_time": "08:00-21:00", "tel": "025-12345678", "id": "mock-rest-jf-001"},
                {"name": f"{city}绿氧健康餐厅", "location": "118.778934,32.058976", "address": f"{city}市玄武区健身街88号", 
                 "type": "健康餐", "rating": "4.6", "cost": "40-60元", "distance": 800, 
                 "business_time": "07:00-22:00", "tel": "025-87654321", "id": "mock-rest-jf-002"},
                {"name": f"{city}素食花园", "location": "118.791234,32.065432", "address": f"{city}市建邺区素食巷66号", 
                 "type": "素食餐厅", "rating": "4.7", "cost": "50-80元", "distance": 1200, 
                 "business_time": "11:00-20:00", "tel": "025-11223344", "id": "mock-rest-jf-003"}
            ],
            "多人团建": [
                {"name": f"{city}川渝火锅城", "location": "118.785678,32.056789", "address": f"{city}市秦淮区火锅街1号", 
                 "type": "火锅店", "rating": "4.9", "cost": "80-120元", "distance": 600, 
                 "business_time": "11:00-23:00", "tel": "025-22334455", "id": "mock-rest-tj-001"},
                {"name": f"{city}烧烤部落", "location": "118.772345,32.053456", "address": f"{city}市鼓楼区烧烤大道8号", 
                 "type": "烧烤店", "rating": "4.8", "cost": "60-100元", "distance": 900, 
                 "business_time": "17:00-02:00", "tel": "025-66778899", "id": "mock-rest-tj-002"},
                {"name": f"{city}海鲜自助餐厅", "location": "118.798765,32.045678", "address": f"{city}市玄武区自助路66号", 
                 "type": "自助餐", "rating": "4.7", "cost": "120-180元", "distance": 1500, 
                 "business_time": "11:00-21:00", "tel": "025-77889900", "id": "mock-rest-tj-003"}
            ],
            "亲子友好": [
                {"name": f"{city}欢乐亲子餐厅", "location": "118.782345,32.059876", "address": f"{city}市鼓楼区亲子巷1号", 
                 "type": "亲子餐厅", "rating": "4.8", "cost": "50-80元", "distance": 400, 
                 "business_time": "09:00-20:00", "tel": "025-33445566", "id": "mock-rest-qz-001"},
                {"name": f"{city}披萨乐园", "location": "118.767890,32.066789", "address": f"{city}市雨花台区披萨路88号", 
                 "type": "西餐厅", "rating": "4.6", "cost": "40-70元", "distance": 1000, 
                 "business_time": "10:00-21:00", "tel": "025-88990011", "id": "mock-rest-qz-002"}
            ],
            "情侣约会": [
                {"name": f"{city}浪漫西餐厅", "location": "118.787654,32.061234", "address": f"{city}市鼓楼区浪漫路1314号", 
                 "type": "西餐厅", "rating": "4.9", "cost": "100-200元", "distance": 500, 
                 "business_time": "11:00-23:00", "tel": "025-44556677", "id": "mock-rest-ql-001"},
                {"name": f"{city}和风日料", "location": "118.792345,32.058765", "address": f"{city}市秦淮区日料街23号", 
                 "type": "日料店", "rating": "4.8", "cost": "80-150元", "distance": 700, 
                 "business_time": "11:00-22:00", "tel": "025-55667788", "id": "mock-rest-ql-002"}
            ],
            "本地特色": [
                {"name": f"{city}老字号小吃", "location": "118.756789,32.062345", "address": f"{city}市建邺区老字号街1号", 
                 "type": "特色小吃", "rating": "4.7", "cost": "20-40元", "distance": 1200, 
                 "business_time": "06:00-18:00", "tel": "025-66778899", "id": "mock-rest-bd-001"},
                {"name": f"{city}金陵菜馆", "location": "118.765432,32.071234", "address": f"{city}市鼓楼区金陵路88号", 
                 "type": "地方菜", "rating": "4.8", "cost": "60-100元", "distance": 1500, 
                 "business_time": "11:00-14:00,17:00-21:00", "tel": "025-77889900", "id": "mock-rest-bd-002"}
            ]
        }
        
        restaurants = mock_data.get(requirement, mock_data["本地特色"])
        for restaurant in restaurants:
            restaurant["distance"] = random.randint(300, int(radius * 1000))
        
        return sorted(restaurants[:limit], key=lambda x: x["distance"])
    
    def _get_mock_restaurants_by_cuisine(self, cuisine: str, city: str, limit: int) -> list:
        """按菜系返回模拟数据"""
        mock_data = {
            "川菜": [{"name": f"{city}川味居", "location": "118.783799,32.060255", "address": f"{city}市川菜街1号", 
                     "type": "川菜馆", "rating": "4.8", "cost": "60-100元", "distance": 500, 
                     "business_time": "11:00-22:00", "id": "mock-cuisine-sc-001"}],
            "火锅": [{"name": f"{city}红火锅", "location": "118.785678,32.058976", "address": f"{city}市火锅大道8号", 
                     "type": "火锅店", "rating": "4.9", "cost": "80-120元", "distance": 800, 
                     "business_time": "11:00-23:00", "id": "mock-cuisine-hg-001"}],
            "西餐": [{"name": f"{city}欧风西餐厅", "location": "118.778934,32.062345", "address": f"{city}市西餐路66号", 
                     "type": "西餐厅", "rating": "4.7", "cost": "100-150元", "distance": 600, 
                     "business_time": "11:00-22:00", "id": "mock-cuisine-xc-001"}],
            "日料": [{"name": f"{city}樱之町", "location": "118.791234,32.056789", "address": f"{city}市日料巷23号", 
                     "type": "日料店", "rating": "4.8", "cost": "80-150元", "distance": 700, 
                     "business_time": "11:00-22:00", "id": "mock-cuisine-rl-001"}]
        }
        
        return mock_data.get(cuisine, mock_data["西餐"])[:limit]
    
    def _get_mock_restaurant_detail(self, place_id: str) -> dict:
        """返回模拟餐厅详情"""
        return {
            "name": "示例餐厅",
            "address": "南京市鼓楼区美食街1号",
            "location": "118.783799,32.060255",
            "type": "西餐厅",
            "rating": "4.8",
            "cost": "100-150元",
            "tel": "025-12345678",
            "business_time": "11:00-22:00",
            "photos": [{"url": "https://example.com/restaurant.jpg"}],
            "description": "环境优雅，菜品精致，适合约会聚餐",
            "parking": "有停车场",
            "wifi": "免费WiFi"
        }

