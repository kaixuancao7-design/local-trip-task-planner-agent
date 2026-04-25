"""API配置测试文件

测试地图和天气API是否正确配置。
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tools.map_tool import MapTool
from tools.weather_tool import WeatherTool
from config.settings import settings


class TestMapAPIConfig(unittest.TestCase):
    """测试地图API配置"""
    
    def setUp(self):
        self.map_tool = MapTool()
    
    def test_map_api_key_configured(self):
        """测试地图API密钥是否配置"""
        print("\n=== 地图API配置测试 ===")
        print("当前API Key: %s" % self.map_tool.api_key)
        print("API URL: %s" % self.map_tool.base_url)
        
        if self.map_tool.api_key and self.map_tool.api_key != "your_amap_api_key_here":
            print("[OK] 地图API密钥已配置")
        else:
            print("[WARN] 地图API密钥未配置，将使用模拟数据")
    
    def test_map_get_route(self):
        """测试路线查询功能"""
        print("\n=== 路线查询测试 ===")
        result = self.map_tool.get_route("南京站", "紫金山", "南京")
        print("起点: 南京站")
        print("终点: 紫金山")
        print("距离: %d米" % result.get('distance', 0))
        print("预计时间: %s" % result.get('travel_time', '未知'))
        self.assertIn("distance", result)
        self.assertIn("travel_time", result)
        print("[OK] 路线查询功能正常")
    
    def test_map_search_place(self):
        """测试地点搜索功能"""
        print("\n=== 地点搜索测试 ===")
        places = self.map_tool.search_place("餐厅", "南京")
        print("搜索关键词: 餐厅")
        print("城市: 南京")
        print("找到地点数: %d" % len(places))
        for place in places[:3]:
            print("  - %s: %s" % (place.get('name', ''), place.get('address', '')))
        self.assertIsInstance(places, list)
        print("[OK] 地点搜索功能正常")
    
    def test_map_geocode(self):
        """测试地理编码功能"""
        print("\n=== 地理编码测试 ===")
        result = self.map_tool.geocode("南京市玄武区紫金山")
        print("地址: 南京市玄武区紫金山")
        print("经纬度: %s" % result.get('location', ''))
        print("城市: %s" % result.get('city', ''))
        self.assertIn("location", result)
        print("[OK] 地理编码功能正常")


class TestWeatherAPIConfig(unittest.TestCase):
    """测试天气API配置"""
    
    def setUp(self):
        self.weather_tool = WeatherTool()
    
    def test_weather_api_key_configured(self):
        """测试天气API密钥是否配置"""
        print("\n=== 天气API配置测试 ===")
        print("当前API Key: %s" % self.weather_tool.api_key)
        print("API URL: %s" % self.weather_tool.base_url)
        
        if self.weather_tool.api_key and self.weather_tool.api_key != "your_seniverse_api_key_here":
            print("[OK] 天气API密钥已配置")
        else:
            print("[WARN] 天气API密钥未配置，将使用模拟数据")
    
    def test_weather_get_weather(self):
        """测试获取实时天气功能"""
        print("\n=== 实时天气测试 ===")
        result = self.weather_tool.get_weather("南京")
        print("城市: %s" % result.get('city', ''))
        print("温度: %d°C" % result.get('temperature', 0))
        print("天气: %s" % result.get('description', ''))
        print("湿度: %d%%" % result.get('humidity', 0))
        print("风速: %d m/s" % result.get('wind_speed', 0))
        self.assertIn("city", result)
        self.assertIn("temperature", result)
        print("[OK] 实时天气查询功能正常")
    
    def test_weather_get_forecast(self):
        """测试获取天气预报功能"""
        print("\n=== 天气预报测试 ===")
        result = self.weather_tool.get_forecast("南京", days=3)
        print("城市: %s" % result.get('city', ''))
        print("未来3天预报:")
        for day in result.get("forecast", []):
            print("  - %s: %s %d°C~%d°C" % (day.get('date', ''), day.get('description', ''), day.get('low', 0), day.get('high', 0)))
        self.assertIn("city", result)
        self.assertIn("forecast", result)
        print("[OK] 天气预报功能正常")


class TestSettingsConfig(unittest.TestCase):
    """测试配置文件加载"""
    
    def test_settings_loaded(self):
        """测试配置文件是否正确加载"""
        print("\n=== 配置文件测试 ===")
        print("应用名称: %s" % settings.app_name)
        print("应用版本: %s" % settings.app_version)
        print("调试模式: %s" % settings.debug)
        print("服务器端口: %d" % settings.port)
        print("大模型: %s" % settings.llm_model)
        print("Chroma路径: %s" % settings.chroma_db_path)
        print("[OK] 配置文件加载正常")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("API配置测试套件")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(TestMapAPIConfig('test_map_api_key_configured'))
    suite.addTest(TestMapAPIConfig('test_map_get_route'))
    suite.addTest(TestMapAPIConfig('test_map_search_place'))
    suite.addTest(TestMapAPIConfig('test_map_geocode'))
    
    suite.addTest(TestWeatherAPIConfig('test_weather_api_key_configured'))
    suite.addTest(TestWeatherAPIConfig('test_weather_get_weather'))
    suite.addTest(TestWeatherAPIConfig('test_weather_get_forecast'))
    
    suite.addTest(TestSettingsConfig('test_settings_loaded'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print("运行测试数: %d" % result.testsRun)
    print("失败数: %d" % len(result.failures))
    print("错误数: %d" % len(result.errors))
    
    if result.wasSuccessful():
        print("[OK] 所有测试通过！")
    else:
        print("[FAIL] 部分测试失败，请检查配置")


if __name__ == '__main__':
    run_tests()