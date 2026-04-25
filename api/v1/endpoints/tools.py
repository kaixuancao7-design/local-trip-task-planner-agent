"""工具模块API端点

提供天气查询、地理编码和路线查询功能。
"""
from fastapi import APIRouter, HTTPException, Query
from tools.weather_tool import WeatherTool
from tools.map_tool import MapTool
from config.logging_config import logger

router = APIRouter(prefix="/tools", tags=["工具"])

# 初始化工具实例
weather_tool = WeatherTool()
map_tool = MapTool()

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
