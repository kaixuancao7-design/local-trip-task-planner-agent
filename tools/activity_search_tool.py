
"""工具层 - 本地活动搜索工具

提供本地休闲活动搜索功能,使用高德地图POI API。
支持亲子、好友聚会等场景化活动搜索。
支持用户位置和通勤时间/距离排序。
"""
import requests
import random
from config.settings import settings
from config.logging_config import log_performance, logger
from tools.map_tool import MapTool

class ActivitySearchTool:
    """本地活动搜索工具类 - 基于高德地图API"""
    
    def __init__(self):
        self.api_key = settings.map_api_key
        self.base_url = settings.map_api_url
        self.map_tool = MapTool()
        
        # 活动类型映射（高德POI分类）- 确保所有类型都有对应的POI编码
        self.activity_types = {
            "亲子": ["儿童乐园", "动物园", "植物园", "科技馆", "博物馆", "游乐场", "水族馆", "公园"],
            "好友聚会": ["展览馆", "美术馆", "咖啡馆", "公园", "特色街区", "酒吧", "茶馆", "KTV", "电影院", "游戏厅"],
            "情侣约会": ["公园", "咖啡馆", "电影院", "美术馆", "餐厅", "音乐厅", "剧院", "观景点", "城市广场"],
            "个人休闲": ["图书馆", "书店", "咖啡馆", "公园", "体育馆", "健身房", "游泳馆", "茶馆", "文化宫"]
        }
        
        # POI类型编码（高德地图）- 根据官方文档 V1.06_20230208 更新
        # 编码规则: 80xxx=体育休闲服务, 14xxxx=科教文化服务, 11xxxx=风景名胜, 50xxx=餐饮服务
        self.poi_typecodes = {
            # 体育休闲服务 (80xxx)
            "游乐场": "80501",
            "儿童乐园": "80501",  # 高德POI中儿童乐园和游乐场同属一个大分类
            "游戏厅": "80305",
            "棋牌室": "80306",
            "电影院": "80601",
            "音乐厅": "80602",
            "剧院": "80603",
            "KTV": "80302",
            "酒吧": "80304",
            "迪厅": "80303",
            "夜总会": "80301",
            "体育馆": "80100",
            "综合体育馆": "80101",
            "游泳馆": "80110",
            "健身中心": "80111",
            "健身房": "80111",  # 高德POI中健身中心和健身房同属一个分类
            "台球厅": "80113",
            "保龄球馆": "80102",
            "网球场": "80103",
            "篮球场": "80104",
            "足球场": "80105",
            "羽毛球馆": "80118",
            "乒乓球馆": "80112",
            "户外健身": "80108",
            "瑜伽馆": "80108",  # 高德POI中瑜伽馆归类到户外健身大类
            
            # 科教文化服务 (14xxxx)
            "博物馆": "140100",
            "展览馆": "140200",
            "会展中心": "140300",
            "美术馆": "140400",
            "图书馆": "140500",
            "科技馆": "140600",
            "天文馆": "140700",
            "文化宫": "140800",
            "档案馆": "140900",
            "学校": "141200",
            "高等院校": "141201",
            "书店": "140604",  # 书店使用独立编码
            
            # 风景名胜 (11xxxx)
            "公园": "110101",
            "动物园": "110102",
            "植物园": "110103",
            "水族馆": "110104",
            "城市广场": "110105",
            "世界遗产": "110201",
            "国家级景点": "110202",
            "纪念馆": "110204",
            "寺庙道观": "110205",
            "教堂": "110206",
            "回教寺": "110207",
            "海滩": "110208",
            "观景点": "110209",
            
            # 休闲娱乐 (805xx)
            "咖啡馆": "80500",
            "茶馆": "80502",  # 茶馆使用独立编码
            
            # 餐饮服务 (50xxx)
            "餐厅": "50100",
            
            # 通用分类
            "步行街": "110106",  # 步行街使用独立编码
            "特色街区": "110106",  # 特色街区归类到步行街
            "文创园": "110101"  # 文创园归类到公园
        }
    
    @log_performance("activity.search")
    def search_activities(self, scene_type: str = "亲子", city: str = "南京", radius: float = 3.0, 
                         keywords: str = "", limit: int = 10, user_location: str = "", 
                         sort_by: str = "distance") -> list:
        """搜索本地活动
        
        Args:
            scene_type: 场景类型（亲子/好友聚会/情侣约会/个人休闲）
            city: 城市名称
            radius: 搜索半径（公里）
            keywords: 搜索关键词
            limit: 返回数量限制
            user_location: 用户位置（经纬度格式："lng,lat"），用于计算通勤时间/距离
            sort_by: 排序方式（distance-距离, time-通勤时间, rating-评分）
        
        Returns:
            活动地点列表（含通勤信息）
        """
        logger.info(f"[ActivitySearchTool] 搜索活动 - 场景: {scene_type}, 城市: {city}, 半径: {radius}km, "
                    f"用户位置: {user_location}, 排序: {sort_by}")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[ActivitySearchTool] 未配置API密钥，返回模拟数据")
            return self._get_mock_activities(scene_type, city, limit, user_location, sort_by)
        
        try:
            activity_keywords = self.activity_types.get(scene_type, ["公园", "景点"])
            
            all_results = []
            for keyword in activity_keywords[:3]:
                typecode = self.poi_typecodes.get(keyword, "")
                results = self._search_by_type(keyword, typecode, city, radius, limit, user_location)
                all_results.extend(results)
            
            unique_results = self._deduplicate_results(all_results)
            
            # 为所有活动添加通勤信息（即使没有用户位置，也估算通勤时间）
            if user_location and ',' in user_location:
                unique_results = self._add_commute_info(unique_results, user_location)
            else:
                # 如果没有用户位置，使用直线距离估算通勤时间
                for activity in unique_results:
                    distance = activity.get("distance", 0)
                    activity["commute_distance"] = distance
                    activity["commute_duration"] = int(distance / 50) * 60  # 估算时间
                    activity["commute_time"] = f"{distance // 500 + 5}分钟" if distance > 0 else "未知"
                    activity["commute_distance_text"] = f"{distance / 1000:.1f}公里"
            
            # 根据排序方式排序
            sorted_results = self._sort_results(unique_results, sort_by)
            
            # 如果搜索结果为空，使用模拟数据
            if len(sorted_results) == 0:
                logger.info("[ActivitySearchTool] 未找到活动，使用模拟数据")
                return self._get_mock_activities(scene_type, city, limit, user_location, sort_by)
            
            logger.info(f"[ActivitySearchTool] 搜索完成 - 找到 {len(sorted_results)} 个活动")
            return sorted_results[:limit]
            
        except Exception as e:
            logger.warning(f"搜索活动失败: {str(e)}，返回模拟数据")
            return self._get_mock_activities(scene_type, city, limit, user_location, sort_by)
    
    @log_performance("activity.search_by_category")
    def search_by_category(self, category: str, city: str = "南京", radius: float = 3.0, 
                          limit: int = 10) -> list:
        """按类别搜索活动
        
        Args:
            category: 活动类别（如：儿童乐园、展览馆、公园等）
            city: 城市名称
            radius: 搜索半径（公里）
            limit: 返回数量限制
        
        Returns:
            活动地点列表
        """
        logger.info(f"[ActivitySearchTool] 按类别搜索 - 类别: {category}, 城市: {city}")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[ActivitySearchTool] 未配置API密钥，返回模拟数据")
            return self._get_mock_activities_by_category(category, city, limit)
        
        try:
            typecode = self.poi_typecodes.get(category, "")
            results = self._search_by_type(category, typecode, city, radius, limit)
            
            logger.info(f"[ActivitySearchTool] 按类别搜索完成 - 找到 {len(results)} 个活动")
            return results
        except Exception as e:
            logger.warning(f"按类别搜索失败: {str(e)}，返回模拟数据")
            return self._get_mock_activities_by_category(category, city, limit)
    
    @log_performance("activity.get_activity_detail")
    def get_activity_detail(self, place_id: str) -> dict:
        """获取活动详情
        
        Args:
            place_id: POI ID
        
        Returns:
            活动详情信息
        """
        logger.info(f"[ActivitySearchTool] 获取活动详情 - place_id: {place_id}")
        
        if not self.api_key or self.api_key == "your_amap_api_key":
            logger.info("[ActivitySearchTool] 未配置API密钥，返回模拟详情")
            return self._get_mock_activity_detail(place_id)
        
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
                    "typecode": poi.get("typecode", ""),
                    "tel": poi.get("tel", ""),
                    "business_time": poi.get("business_time", ""),
                    "rating": poi.get("rating", ""),
                    "cost": poi.get("cost", ""),
                    "photos": poi.get("photos", []),
                    "description": poi.get("description", "")
                }
            else:
                logger.warning(f"获取详情失败: {data.get('info', '未知错误')}")
                return self._get_mock_activity_detail(place_id)
        except Exception as e:
            logger.warning(f"获取活动详情失败: {str(e)}，返回模拟数据")
            return self._get_mock_activity_detail(place_id)
    
    def _search_by_type(self, keyword: str, typecode: str, city: str, radius: float, limit: int, 
                        user_location: str = "") -> list:
        """内部方法：按类型搜索"""
        url = f"{self.base_url}/place/text"
        params = {
            "keywords": keyword,
            "city": city,
            "key": self.api_key,
            "types": typecode,
            "offset": 0,
            "limit": min(limit, 50),  # 扩大默认限制，最多50条
            "extensions": "all",
            "citylimit": "true"  # 限制在指定城市内搜索
        }
        
        # 如果有用户位置，使用周边搜索API
        if user_location and ',' in user_location:
            url = f"{self.base_url}/place/around"
            params["location"] = user_location
            params["radius"] = int(radius * 1000)
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") != "1":
            return []
        
        results = []
        for poi in data.get("pois", []):
            # 处理distance字段
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
                "typecode": poi.get("typecode", ""),
                "distance": distance,
                "rating": poi.get("rating", ""),
                "cost": poi.get("cost", ""),
                "business_time": poi.get("business_time", ""),
                "tel": poi.get("tel", ""),
                "photos": poi.get("photos", []),
                "id": poi.get("id", "")
            })
        
        return results
    
    def _add_commute_info(self, activities: list, user_location: str) -> list:
        """为活动列表添加通勤信息"""
        for activity in activities:
            location = activity.get("location", "")
            if location and ',' in location:
                try:
                    route = self.map_tool.get_route(user_location, location, travel_mode="driving")
                    activity["commute_distance"] = route.get("distance", 0)
                    activity["commute_duration"] = route.get("duration", 0)
                    activity["commute_time"] = route.get("travel_time", "")
                    activity["commute_distance_text"] = route.get("distance_text", "")
                except Exception as e:
                    logger.warning(f"计算通勤信息失败: {str(e)}")
                    activity["commute_distance"] = activity.get("distance", 0)
                    activity["commute_duration"] = int(activity.get("distance", 0) / 50) * 60  # 估算时间
                    activity["commute_time"] = f"{(activity.get('distance', 0) // 500)}分钟"
                    activity["commute_distance_text"] = f"{activity.get('distance', 0) / 1000:.1f}公里"
        return activities
    
    def _sort_results(self, activities: list, sort_by: str) -> list:
        """根据指定方式排序"""
        if sort_by == "time":
            return sorted(activities, key=lambda x: x.get("commute_duration", float('inf')))
        elif sort_by == "rating":
            return sorted(activities, key=lambda x: float(x.get("rating", 0)) if x.get("rating") else 0, reverse=True)
        else:  # distance
            return sorted(activities, key=lambda x: x.get("commute_distance", x.get("distance", float('inf'))))
    
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
    
    def _get_mock_activities(self, scene_type: str, city: str, limit: int, 
                            user_location: str = "", sort_by: str = "distance") -> list:
        """返回模拟活动数据"""
        mock_data = {
            "亲子": [
                {"name": f"{city}儿童乐园", "location": "118.783799,32.060255", "address": f"{city}市鼓楼区亲子路1号", 
                 "type": "儿童乐园", "typecode": "80501", "distance": 500, "rating": "4.8", "cost": "60-100元", 
                 "business_time": "09:00-18:00", "tel": "025-12345678", "id": "mock-qz-001"},
                {"name": f"{city}动物园", "location": "118.778934,32.058976", "address": f"{city}市玄武区动物园路88号", 
                 "type": "动物园", "typecode": "110102", "distance": 1200, "rating": "4.6", "cost": "40-60元", 
                 "business_time": "08:30-17:30", "tel": "025-87654321", "id": "mock-qz-002"},
                {"name": f"{city}科技馆", "location": "118.791234,32.065432", "address": f"{city}市建邺区科技大道100号", 
                 "type": "科技馆", "typecode": "140600", "distance": 1800, "rating": "4.7", "cost": "免费", 
                 "business_time": "09:00-16:30", "tel": "025-11223344", "id": "mock-qz-003"},
                {"name": f"{city}植物园", "location": "118.765432,32.071234", "address": f"{city}市雨花台区植物园路66号", 
                 "type": "植物园", "typecode": "110103", "distance": 2500, "rating": "4.5", "cost": "30元", 
                 "business_time": "08:00-18:00", "tel": "025-55667788", "id": "mock-qz-004"}
            ],
            "好友聚会": [
                {"name": f"{city}艺术展览馆", "location": "118.785678,32.056789", "address": f"{city}市秦淮区艺术街1号", 
                 "type": "展览馆", "typecode": "140200", "distance": 600, "rating": "4.9", "cost": "50元", 
                 "business_time": "10:00-18:00", "tel": "025-22334455", "id": "mock-hy-001"},
                {"name": f"{city}老门东历史街区", "location": "118.798765,32.045678", "address": f"{city}市秦淮区老门东", 
                 "type": "特色街区", "typecode": "110105", "distance": 900, "rating": "4.8", "cost": "免费", 
                 "business_time": "全天", "tel": "", "id": "mock-hy-002"},
                {"name": f"{city}美术馆", "location": "118.772345,32.053456", "address": f"{city}市鼓楼区美术大道8号", 
                 "type": "美术馆", "typecode": "140400", "distance": 1100, "rating": "4.7", "cost": "免费", 
                 "business_time": "09:00-17:00", "tel": "025-66778899", "id": "mock-hy-003"},
                {"name": f"{city}中央公园", "location": "118.789012,32.067890", "address": f"{city}市玄武区公园路1号", 
                 "type": "公园", "typecode": "110101", "distance": 400, "rating": "4.6", "cost": "免费", 
                 "business_time": "全天", "tel": "", "id": "mock-hy-004"}
            ],
            "情侣约会": [
                {"name": f"{city}浪漫咖啡馆", "location": "118.782345,32.059876", "address": f"{city}市鼓楼区情侣巷1314号", 
                 "type": "咖啡馆", "typecode": "80500", "distance": 300, "rating": "4.8", "cost": "50-100元", 
                 "business_time": "09:00-22:00", "tel": "025-77889900", "id": "mock-ql-001"},
                {"name": f"{city}滨江公园", "location": "118.756789,32.062345", "address": f"{city}市建邺区滨江大道", 
                 "type": "公园", "typecode": "110101", "distance": 2000, "rating": "4.7", "cost": "免费", 
                 "business_time": "全天", "tel": "", "id": "mock-ql-002"},
                {"name": f"{city}艺术电影院", "location": "118.776543,32.055678", "address": f"{city}市玄武区电影街88号", 
                 "type": "电影院", "typecode": "80601", "distance": 700, "rating": "4.6", "cost": "30-80元", 
                 "business_time": "10:00-23:00", "tel": "025-33445566", "id": "mock-ql-003"}
            ],
            "个人休闲": [
                {"name": f"{city}市图书馆", "location": "118.787654,32.061234", "address": f"{city}市鼓楼区图书路1号", 
                 "type": "图书馆", "typecode": "140500", "distance": 500, "rating": "4.5", "cost": "免费", 
                 "business_time": "09:00-21:00", "tel": "025-44556677", "id": "mock-gr-001"},
                {"name": f"{city}阅读书店", "location": "118.792345,32.058765", "address": f"{city}市秦淮区书店街23号", 
                 "type": "书店", "typecode": "140500", "distance": 800, "rating": "4.7", "cost": "免费", 
                 "business_time": "10:00-22:00", "tel": "025-55667788", "id": "mock-gr-002"},
                {"name": f"{city}全民健身中心", "location": "118.767890,32.066789", "address": f"{city}市雨花台区健身路66号", 
                 "type": "体育馆", "typecode": "80100", "distance": 1500, "rating": "4.4", "cost": "20-50元", 
                 "business_time": "08:00-22:00", "tel": "025-88990011", "id": "mock-gr-003"}
            ]
        }
        
        activities = mock_data.get(scene_type, mock_data["亲子"])
        
        # 添加通勤信息（模拟）
        for activity in activities:
            activity["distance"] = random.randint(300, 3000)
            activity["commute_distance"] = activity["distance"]
            activity["commute_duration"] = int(activity["distance"] / 50) * 60
            activity["commute_time"] = f"{activity['distance'] // 500 + 5}分钟"
            activity["commute_distance_text"] = f"{activity['distance'] / 1000:.1f}公里"
        
        # 根据排序方式排序
        if sort_by == "time":
            sorted_activities = sorted(activities, key=lambda x: x["commute_duration"])
        elif sort_by == "rating":
            sorted_activities = sorted(activities, key=lambda x: float(x["rating"]), reverse=True)
        else:
            sorted_activities = sorted(activities, key=lambda x: x["distance"])
        
        return sorted_activities[:limit]
    
    def _get_mock_activities_by_category(self, category: str, city: str, limit: int) -> list:
        """按类别返回模拟数据"""
        mock_category_data = {
            "儿童乐园": [{"name": f"{city}欢乐儿童乐园", "location": "118.783799,32.060255", "address": f"{city}市儿童路1号", 
                        "type": "儿童乐园", "typecode": "80501", "distance": 500, "rating": "4.8", "cost": "80元", 
                        "business_time": "09:00-18:00", "id": "mock-cat-001"}],
            "展览馆": [{"name": f"{city}当代艺术展览馆", "location": "118.785678,32.058976", "address": f"{city}市艺术大道8号", 
                      "type": "展览馆", "typecode": "140200", "distance": 800, "rating": "4.9", "cost": "60元", 
                      "business_time": "10:00-18:00", "id": "mock-cat-002"}],
            "公园": [{"name": f"{city}市民公园", "location": "118.778934,32.062345", "address": f"{city}市公园路1号", 
                    "type": "公园", "typecode": "110101", "distance": 300, "rating": "4.6", "cost": "免费", 
                    "business_time": "全天", "id": "mock-cat-003"}],
            "咖啡馆": [{"name": f"{city}时光咖啡馆", "location": "118.791234,32.056789", "address": f"{city}市咖啡巷88号", 
                      "type": "咖啡馆", "typecode": "80500", "distance": 600, "rating": "4.7", "cost": "40-60元", 
                      "business_time": "08:00-23:00", "id": "mock-cat-004"}]
        }
        
        return mock_category_data.get(category, mock_category_data["公园"])[:limit]
    
    def _get_mock_activity_detail(self, place_id: str) -> dict:
        """返回模拟活动详情"""
        return {
            "name": "示例活动",
            "address": "南京市鼓楼区示例路1号",
            "location": "118.783799,32.060255",
            "type": "儿童乐园",
            "typecode": "80501",
            "tel": "025-12345678",
            "business_time": "09:00-18:00",
            "rating": "4.8",
            "cost": "60-100元",
            "photos": [{"url": "https://example.com/photo1.jpg"}],
            "description": "这是一个非常适合亲子游玩的场所，设施齐全，环境优美。"
        }
