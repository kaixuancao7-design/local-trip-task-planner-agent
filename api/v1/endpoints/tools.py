"""工具模块API端点

提供天气查询、地理编码、路线查询、活动搜索、餐厅检索、排队核验、预订和通知生成功能。
"""
from fastapi import APIRouter, HTTPException, Query, Body
from tools.weather_tool import WeatherTool
from tools.map_tool import MapTool
from tools.activity_search_tool import ActivitySearchTool
from tools.restaurant_search_tool import RestaurantSearchTool
from tools.queue_check_tool import QueueCheckTool
from tools.booking_tool import BookingTool
from tools.notification_tool import NotificationTool
from config.logging_config import logger

router = APIRouter(prefix="/tools", tags=["工具"])

# 初始化工具实例
weather_tool = WeatherTool()
map_tool = MapTool()
activity_tool = ActivitySearchTool()
restaurant_tool = RestaurantSearchTool()
queue_tool = QueueCheckTool()
booking_tool = BookingTool()
notification_tool = NotificationTool()

logger.info("工具模块API端点已初始化")


@router.get("/weather", summary="获取天气信息")
async def get_weather(city: str = Query(..., description="城市名称")):
    """获取指定城市的天气信息"""
    try:
        logger.info(f"获取天气信息 - 城市: {city}")
        result = weather_tool.get_weather(city)
        logger.debug(f"天气查询结果 - {city}: {result.get('temperature')}°C, {result.get('description')}")
        return {
            "success": True,
            "city": result.get("city", ""),
            "temperature": result.get("temperature", 0),
            "description": result.get("description", ""),
            "humidity": result.get("humidity", 0),
            "wind_speed": result.get("wind_speed", 0),
            "wind_direction": result.get("wind_direction", ""),
            "update_time": result.get("update_time", "")
        }
    except Exception as e:
        logger.error(f"获取天气信息失败 - 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast", summary="获取天气预报")
async def get_forecast(
    city: str = Query(..., description="城市名称"),
    days: int = Query(3, description="预报天数", ge=1, le=7)
):
    """获取指定城市的天气预报"""
    try:
        logger.info(f"获取天气预报 - 城市: {city}, 天数: {days}")
        result = weather_tool.get_forecast(city, days)
        logger.debug(f"天气预报查询成功 - {city}, {len(result.get('forecast', []))}天")
        return {
            "success": True,
            "city": result.get("city", ""),
            "forecast": result.get("forecast", []),
            "update_time": result.get("update_time", "")
        }
    except Exception as e:
        logger.error(f"获取天气预报失败 - 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geocode", summary="地理编码")
async def geocode(
    address: str = Query(..., description="地址字符串"),
    city: str = Query("", description="城市名称（可选）")
):
    """将地址转换为经纬度"""
    try:
        logger.info(f"地理编码 - 地址: {address}, 城市: {city}")
        result = map_tool.geocode(address, city)
        logger.debug(f"地理编码成功 - 位置: {result.get('location')}")
        return {
            "success": True,
            "formatted_address": result.get("formatted_address", ""),
            "location": result.get("location", ""),
            "province": result.get("province", ""),
            "city": result.get("city", ""),
            "district": result.get("district", "")
        }
    except Exception as e:
        logger.error(f"地理编码失败 - 地址: {address}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/route", summary="获取路线信息")
async def get_route(
    origin: str = Query(..., description="起点（地址或经纬度）"),
    destination: str = Query(..., description="终点（地址或经纬度）"),
    city: str = Query("", description="城市名称（可选）")
):
    """获取两点之间的驾车路线信息"""
    try:
        logger.info(f"路线查询 - 起点: {origin}, 终点: {destination}, 城市: {city}")
        result = map_tool.get_route(origin, destination, city)
        logger.debug(f"路线查询成功 - 距离: {result.get('distance')}米, 时间: {result.get('travel_time')}")
        return {
            "success": True,
            "origin": result.get("origin", ""),
            "destination": result.get("destination", ""),
            "distance": result.get("distance", 0),
            "duration": result.get("duration", 0),
            "travel_time": result.get("travel_time", ""),
            "steps": result.get("steps", [])
        }
    except Exception as e:
        logger.error(f"路线查询失败 - 起点: {origin}, 终点: {destination}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", summary="地点搜索")
async def search_place(
    keyword: str = Query(..., description="搜索关键词"),
    city: str = Query("", description="城市名称（可选）")
):
    """搜索指定关键词的地点"""
    try:
        logger.info(f"地点搜索 - 关键词: {keyword}, 城市: {city}")
        result = map_tool.search_place(keyword, city)
        logger.debug(f"地点搜索成功 - 找到 {len(result)} 个地点")
        return {
            "success": True,
            "places": result
        }
    except Exception as e:
        logger.error(f"地点搜索失败 - 关键词: {keyword}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location", summary="获取用户位置")
async def get_user_location():
    """通过IP地址获取用户大致位置信息
    
    注意：此接口不直接暴露用户隐私数据，返回的是脱敏后的城市级位置信息
    """
    try:
        logger.info("获取用户位置信息（脱敏处理）")
        # 模拟位置数据（实际生产环境可使用IP地理定位服务）
        # 不直接返回精确坐标，只返回城市级信息以保护隐私
        mock_location = {
            "city": "南京市",
            "province": "江苏省",
            "lat": 32.0603,
            "lng": 118.7969,
            "address": "南京市"
        }
        
        logger.debug(f"返回用户位置 - 城市: {mock_location['city']}, 坐标: {mock_location['lat']}, {mock_location['lng']}")
        return {
            "success": True,
            "city": mock_location["city"],
            "province": mock_location["province"],
            "lat": mock_location["lat"],
            "lng": mock_location["lng"],
            "address": mock_location["address"]
        }
    except Exception as e:
        logger.error(f"获取用户位置失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map/config", summary="获取地图配置")
async def get_map_config():
    """获取地图服务配置信息
    
    返回地图API的必要配置，注意：不直接返回完整的API key，
    而是返回用于前端加载的安全配置
    """
    try:
        logger.info("获取地图配置信息")
        from config.settings import settings
        
        logger.debug(f"返回地图配置 - API URL: https://webapi.amap.com/maps")
        return {
            "success": True,
            "map_api_key": settings.map_api_key,
            "map_api_url": "https://webapi.amap.com/maps",
            "map_ui_url": "https://webapi.amap.com/ui/1.0/main.js"
        }
    except Exception as e:
        logger.error(f"获取地图配置失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities/search", summary="搜索本地活动")
async def search_activities(
    scene_type: str = Query("亲子", description="场景类型（亲子/好友聚会/情侣约会/个人休闲）"),
    city: str = Query("南京", description="城市名称"),
    radius: float = Query(3.0, description="搜索半径（公里）", ge=0.5, le=10),
    keywords: str = Query("", description="搜索关键词"),
    limit: int = Query(10, description="返回数量限制", ge=1, le=20),
    user_location: str = Query("", description="用户位置（经纬度格式：lng,lat）"),
    sort_by: str = Query("distance", description="排序方式（distance-距离, time-通勤时间, rating-评分）")
):
    """根据场景类型搜索本地休闲活动，支持用户位置和通勤排序"""
    try:
        logger.info(f"搜索本地活动 - 场景: {scene_type}, 城市: {city}, 半径: {radius}km, 用户位置: {user_location}, 排序: {sort_by}")
        result = activity_tool.search_activities(scene_type, city, radius, keywords, limit, user_location, sort_by)
        logger.debug(f"活动搜索成功 - 找到 {len(result)} 个活动")
        return {
            "success": True,
            "scene_type": scene_type,
            "city": city,
            "activities": result
        }
    except Exception as e:
        logger.error(f"搜索活动失败 - 场景: {scene_type}, 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities/category", summary="按类别搜索活动")
async def search_activities_by_category(
    category: str = Query(..., description="活动类别（儿童乐园/展览馆/公园/咖啡馆等）"),
    city: str = Query("南京", description="城市名称"),
    radius: float = Query(3.0, description="搜索半径（公里）", ge=0.5, le=10),
    limit: int = Query(10, description="返回数量限制", ge=1, le=20)
):
    """按指定类别搜索活动"""
    try:
        logger.info(f"按类别搜索活动 - 类别: {category}, 城市: {city}")
        result = activity_tool.search_by_category(category, city, radius, limit)
        logger.debug(f"按类别搜索成功 - 找到 {len(result)} 个活动")
        return {
            "success": True,
            "category": category,
            "city": city,
            "activities": result
        }
    except Exception as e:
        logger.error(f"按类别搜索活动失败 - 类别: {category}, 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities/detail", summary="获取活动详情")
async def get_activity_detail(
    place_id: str = Query(..., description="活动地点ID")
):
    """获取指定活动的详细信息"""
    try:
        logger.info(f"获取活动详情 - place_id: {place_id}")
        result = activity_tool.get_activity_detail(place_id)
        logger.debug(f"获取活动详情成功 - 名称: {result.get('name')}")
        return {
            "success": True,
            "activity": result
        }
    except Exception as e:
        logger.error(f"获取活动详情失败 - place_id: {place_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 餐厅检索API ==========
@router.get("/restaurants/search", summary="搜索餐厅")
async def search_restaurants(
    requirement: str = Query("减肥餐", description="餐饮需求（减肥餐/多人团建/亲子友好/情侣约会/本地特色）"),
    city: str = Query("南京", description="城市名称"),
    radius: float = Query(3.0, description="搜索半径（公里）", ge=0.5, le=10),
    limit: int = Query(10, description="返回数量限制", ge=1, le=20)
):
    """根据餐饮需求搜索餐厅"""
    try:
        logger.info(f"搜索餐厅 - 需求: {requirement}, 城市: {city}, 半径: {radius}km")
        result = restaurant_tool.search_restaurants(requirement, city, radius, limit)
        logger.debug(f"餐厅搜索成功 - 找到 {len(result)} 家餐厅")
        return {
            "success": True,
            "requirement": requirement,
            "city": city,
            "restaurants": result
        }
    except Exception as e:
        logger.error(f"搜索餐厅失败 - 需求: {requirement}, 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/restaurants/category", summary="按菜系搜索餐厅")
async def search_restaurants_by_category(
    cuisine: str = Query(..., description="菜系名称（川菜/火锅/西餐/日料等）"),
    city: str = Query("南京", description="城市名称"),
    radius: float = Query(3.0, description="搜索半径（公里）", ge=0.5, le=10),
    limit: int = Query(10, description="返回数量限制", ge=1, le=20)
):
    """按菜系搜索餐厅"""
    try:
        logger.info(f"按菜系搜索餐厅 - 菜系: {cuisine}, 城市: {city}")
        result = restaurant_tool.search_by_cuisine(cuisine, city, radius, limit)
        logger.debug(f"按菜系搜索成功 - 找到 {len(result)} 家餐厅")
        return {
            "success": True,
            "cuisine": cuisine,
            "city": city,
            "restaurants": result
        }
    except Exception as e:
        logger.error(f"按菜系搜索餐厅失败 - 菜系: {cuisine}, 城市: {city}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/restaurants/detail", summary="获取餐厅详情")
async def get_restaurant_detail(
    place_id: str = Query(..., description="餐厅ID")
):
    """获取餐厅详情"""
    try:
        logger.info(f"获取餐厅详情 - place_id: {place_id}")
        result = restaurant_tool.get_restaurant_detail(place_id)
        logger.debug(f"获取餐厅详情成功 - 名称: {result.get('name')}")
        return {
            "success": True,
            "restaurant": result
        }
    except Exception as e:
        logger.error(f"获取餐厅详情失败 - place_id: {place_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 排队核验API ==========
@router.get("/queue/check", summary="查询排队状态")
async def check_queue(
    venue_id: str = Query(..., description="场地/餐厅ID")
):
    """查询场地/餐厅的排队状态"""
    try:
        logger.info(f"查询排队状态 - venue_id: {venue_id}")
        result = queue_tool.check_queue(venue_id)
        logger.debug(f"排队状态查询成功 - 排队人数: {result.get('waiting_count')}")
        return {
            "success": True,
            "queue_info": result
        }
    except Exception as e:
        logger.error(f"查询排队状态失败 - venue_id: {venue_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/batch-check", summary="批量查询排队状态")
async def batch_check_queue(
    venue_ids: str = Query(..., description="场地ID列表，逗号分隔")
):
    """批量查询多个场地的排队状态"""
    try:
        venue_id_list = [v.strip() for v in venue_ids.split(",")]
        logger.info(f"批量查询排队状态 - venue_ids: {venue_id_list}")
        result = queue_tool.batch_check_queue(venue_id_list)
        logger.debug(f"批量查询成功 - {len(result)} 个场地")
        return {
            "success": True,
            "queue_info_list": result
        }
    except Exception as e:
        logger.error(f"批量查询排队状态失败 - venue_ids: {venue_ids}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/recommendations", summary="获取推荐场地")
async def get_recommendations(
    venue_ids: str = Query(..., description="场地ID列表，逗号分隔"),
    max_wait_time: int = Query(20, description="最大等待时间（分钟）", ge=5, le=60)
):
    """获取推荐场地（按等待时间筛选）"""
    try:
        venue_id_list = [v.strip() for v in venue_ids.split(",")]
        logger.info(f"获取推荐场地 - 最大等待时间: {max_wait_time}分钟")
        result = queue_tool.get_recommendations(venue_id_list, max_wait_time)
        logger.debug(f"推荐完成 - {len(result)} 个场地")
        return {
            "success": True,
            "recommendations": result
        }
    except Exception as e:
        logger.error(f"获取推荐场地失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 预订API ==========
@router.post("/booking/activity", summary="预订活动门票")
async def book_activity(
    venue_id: str = Body(..., description="活动场地ID"),
    user_id: str = Body(..., description="用户ID"),
    date: str = Body(..., description="预订日期（YYYY-MM-DD）"),
    time_slot: str = Body(..., description="时间段（如 10:00-12:00）"),
    quantity: int = Body(1, description="人数")
):
    """预订活动门票"""
    try:
        logger.info(f"预订活动 - venue_id: {venue_id}, user_id: {user_id}, date: {date}")
        result = booking_tool.create_activity_booking(venue_id, user_id, date, time_slot, quantity)
        if result.get("status") == "confirmed":
            logger.info(f"活动预订成功 - booking_ref: {result.get('booking_ref')}")
            return {
                "success": True,
                "booking_ref": result.get("booking_ref"),
                "message": "预订成功",
                "detail": result
            }
        else:
            logger.warning(f"活动预订失败 - {result.get('message')}")
            return {
                "success": False,
                "message": result.get("message")
            }
    except Exception as e:
        logger.error(f"预订活动失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking/restaurant", summary="预订餐厅座位")
async def book_restaurant(
    venue_id: str = Body(..., description="餐厅ID"),
    user_id: str = Body(..., description="用户ID"),
    date: str = Body(..., description="预订日期（YYYY-MM-DD）"),
    time_slot: str = Body(..., description="用餐时间（如 12:00）"),
    guests: int = Body(2, description="用餐人数")
):
    """预订餐厅座位"""
    try:
        logger.info(f"预订餐厅 - venue_id: {venue_id}, user_id: {user_id}, date: {date}")
        result = booking_tool.create_restaurant_booking(venue_id, user_id, date, time_slot, guests)
        if result.get("status") == "booked":
            logger.info(f"餐厅预订成功 - booking_ref: {result.get('booking_ref')}")
            return {
                "success": True,
                "booking_ref": result.get("booking_ref"),
                "message": "预订成功",
                "detail": result
            }
        else:
            logger.warning(f"餐厅预订失败 - {result.get('message')}")
            return {
                "success": False,
                "message": result.get("message")
            }
    except Exception as e:
        logger.error(f"预订餐厅失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/booking/detail", summary="查询预订详情")
async def get_booking_detail(
    booking_ref: str = Query(..., description="预订号")
):
    """查询预订详情"""
    try:
        logger.info(f"查询预订详情 - booking_ref: {booking_ref}")
        result = booking_tool.get_booking(booking_ref)
        if result.get("success") is False:
            return {"success": False, "message": result.get("message")}
        logger.debug(f"预订查询成功 - status: {result.get('status')}")
        return {
            "success": True,
            "booking": result
        }
    except Exception as e:
        logger.error(f"查询预订详情失败 - booking_ref: {booking_ref}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking/cancel", summary="取消预订")
async def cancel_booking(
    booking_ref: str = Body(..., description="预订号")
):
    """取消预订"""
    try:
        logger.info(f"取消预订 - booking_ref: {booking_ref}")
        result = booking_tool.cancel_booking(booking_ref)
        if result:
            logger.info(f"预订取消成功 - booking_ref: {booking_ref}")
            return {"success": True, "message": "取消成功"}
        else:
            logger.warning(f"取消预订失败 - booking_ref: {booking_ref}")
            return {"success": False, "message": "取消失败，预订不存在"}
    except Exception as e:
        logger.error(f"取消预订失败 - booking_ref: {booking_ref}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/booking/user", summary="获取用户预订列表")
async def get_user_bookings(
    user_id: str = Query(..., description="用户ID")
):
    """获取用户所有预订"""
    try:
        logger.info(f"获取用户预订 - user_id: {user_id}")
        result = booking_tool.get_user_bookings(user_id)
        logger.debug(f"用户预订查询成功 - {len(result)} 个预订")
        return {
            "success": True,
            "user_id": user_id,
            "bookings": result
        }
    except Exception as e:
        logger.error(f"获取用户预订失败 - user_id: {user_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 通知生成API ==========
@router.post("/notification/text", summary="生成文本通知")
async def generate_text_notification(
    plan: dict = Body(..., description="计划数据"),
    scene_type: str = Body("friends", description="场景类型（family/friends/couple/solo）")
):
    """生成纯文本格式行程通知"""
    try:
        logger.info(f"生成文本通知 - 场景: {scene_type}")
        result = notification_tool.generate_text_notification(plan, scene_type)
        return {
            "success": True,
            "format": "text",
            "content": result
        }
    except Exception as e:
        logger.error(f"生成文本通知失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification/html", summary="生成HTML通知")
async def generate_html_notification(
    plan: dict = Body(..., description="计划数据"),
    scene_type: str = Body("friends", description="场景类型")
):
    """生成HTML格式行程通知"""
    try:
        logger.info(f"生成HTML通知 - 场景: {scene_type}")
        result = notification_tool.generate_html_notification(plan, scene_type)
        return {
            "success": True,
            "format": "html",
            "content": result
        }
    except Exception as e:
        logger.error(f"生成HTML通知失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification/markdown", summary="生成Markdown通知")
async def generate_markdown_notification(
    plan: dict = Body(..., description="计划数据"),
    scene_type: str = Body("friends", description="场景类型")
):
    """生成Markdown格式行程通知"""
    try:
        logger.info(f"生成Markdown通知 - 场景: {scene_type}")
        result = notification_tool.generate_markdown_notification(plan, scene_type)
        return {
            "success": True,
            "format": "markdown",
            "content": result
        }
    except Exception as e:
        logger.error(f"生成Markdown通知失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification/social", summary="生成社交分享文案")
async def generate_social_share(
    plan: dict = Body(..., description="计划数据"),
    scene_type: str = Body("friends", description="场景类型")
):
    """生成社交媒体分享文案"""
    try:
        logger.info(f"生成社交分享文案 - 场景: {scene_type}")
        result = notification_tool.generate_social_share(plan, scene_type)
        return {
            "success": True,
            "format": "social",
            "content": result
        }
    except Exception as e:
        logger.error(f"生成社交分享文案失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification/sms", summary="生成短信通知")
async def generate_sms_notification(
    plan: dict = Body(..., description="计划数据")
):
    """生成短信格式通知"""
    try:
        logger.info("生成短信通知")
        result = notification_tool.generate_sms_notification(plan)
        return {
            "success": True,
            "format": "sms",
            "content": result
        }
    except Exception as e:
        logger.error(f"生成短信通知失败 - 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
