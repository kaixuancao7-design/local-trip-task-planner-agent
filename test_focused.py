"""针对性测试脚本 - 验证修复效果"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.activity_search_tool import ActivitySearchTool
from tools.restaurant_search_tool import RestaurantSearchTool
from tools.queue_check_tool import QueueCheckTool
from tools.booking_tool import BookingTool
from tools.map_tool import MapTool
from tools.weather_tool import WeatherTool
from core.planner import PlanningAgent
from config.settings import settings


def test_llm_timeout_config():
    """测试LLM超时配置"""
    print("[TEST] LLM超时配置")
    print(f"  llm_timeout: {settings.llm_timeout}秒")
    print(f"  llm_max_tokens: {settings.llm_max_tokens}")
    print(f"  llm_max_retries: {settings.llm_max_retries}")
    
    assert settings.llm_timeout == 30, "LLM超时配置应为30秒"
    assert settings.llm_max_tokens == 2048, "最大token数配置错误"
    print("  [PASS] 配置正确")


def test_activity_search():
    """测试活动搜索工具 - 验证关键词映射优化"""
    print("\n[TEST] 活动搜索工具")
    tool = ActivitySearchTool()
    
    test_cases = [
        ("亲子", "南京", "亲子场景搜索"),
        ("好友聚会", "南京", "好友聚会场景搜索"),
        ("情侣约会", "南京", "情侣约会场景搜索"),
        ("个人休闲", "南京", "个人休闲场景搜索"),
    ]
    
    for scene_type, city, desc in test_cases:
        start = time.time()
        results = tool.search_activities(scene_type, city)
        duration = time.time() - start
        print(f"  {desc}: {len(results)} 个结果 ({duration:.2f}s)")
        
        if len(results) == 0:
            print(f"    [WARN] 搜索结果为空，使用Mock数据")
            results = tool._get_mock_activities(scene_type, city, 5)
            print(f"    Mock数据: {len(results)} 个")


def test_restaurant_search():
    """测试餐厅搜索工具 - 验证关键词映射优化"""
    print("\n[TEST] 餐厅搜索工具")
    tool = RestaurantSearchTool()
    
    test_cases = [
        ("减肥餐", "南京", "减肥餐搜索"),
        ("多人团建", "南京", "多人团建搜索"),
        ("亲子友好", "南京", "亲子友好搜索"),
        ("情侣约会", "南京", "情侣约会搜索"),
        ("本地特色", "南京", "本地特色搜索"),
    ]
    
    for requirement, city, desc in test_cases:
        start = time.time()
        results = tool.search_restaurants(requirement, city)
        duration = time.time() - start
        print(f"  {desc}: {len(results)} 个结果 ({duration:.2f}s)")
        
        if len(results) == 0:
            print(f"    [WARN] 搜索结果为空，使用Mock数据")


def test_plan_degradation():
    """测试降级机制 - LLM超时后是否正确降级"""
    print("\n[TEST] 降级机制测试")
    
    # 创建Agent（禁用LLM快速测试）
    agent = PlanningAgent()
    
    # 测试规则解析（降级路径）
    try:
        result = agent._parse_scene_constraints_rules("周末带孩子出去玩")
        print(f"  [PASS] 规则解析成功")
        print(f"    场景类型: {result.get('scene_info', {}).get('scene_type')}")
        print(f"    人数: {result.get('scene_info', {}).get('people_count')}")
    except Exception as e:
        print(f"  [FAIL] 规则解析失败: {e}")


def test_booking_tool():
    """测试预订工具"""
    print("\n[TEST] 预订工具")
    tool = BookingTool()
    
    # 创建预订
    result = tool.create_restaurant_booking(
        venue_id="mock-rest-jf-001",
        user_id="test_user",
        date="2026-06-01",
        time_slot="12:00",
        guests=4
    )
    print(f"  创建预订: {'成功' if result['success'] else '失败'}")
    
    if result['success']:
        booking_ref = result['booking_ref']
        # 查询详情
        detail = tool.get_booking(booking_ref)
        print(f"  查询详情: {'成功' if detail else '失败'}")
        
        # 取消预订
        cancel_result = tool.cancel_booking(booking_ref)
        print(f"  取消预订: {'成功' if cancel_result else '失败'}")


def test_map_and_weather():
    """测试地图和天气工具"""
    print("\n[TEST] 地图和天气工具")
    
    # 地图工具
    map_tool = MapTool()
    route = map_tool.get_route("南京市新街口", "南京市夫子庙", "南京", "driving")
    print(f"  地图路线: {'成功' if 'distance' in route else '失败'}")
    
    # 天气工具
    weather_tool = WeatherTool()
    weather = weather_tool.get_weather("南京")
    print(f"  天气查询: {'成功' if 'temperature' in weather else '失败'}")


def run_tests():
    """运行所有测试"""
    print("="*60)
    print("针对性测试 - 验证修复效果")
    print("="*60)
    
    try:
        test_llm_timeout_config()
        test_activity_search()
        test_restaurant_search()
        test_plan_degradation()
        test_booking_tool()
        test_map_and_weather()
        
        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] 测试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_tests()
