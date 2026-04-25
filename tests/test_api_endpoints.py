"""API端点测试文件

测试FastAPI端点是否正常工作。
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestAPIEndpoints(unittest.TestCase):
    """测试API端点"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        print("\n=== 健康检查接口测试 ===")
        response = client.get("/")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "ok")
        print("[OK] 健康检查接口正常")
    
    def test_weather_endpoint(self):
        """测试天气查询接口"""
        print("\n=== 天气查询接口测试 ===")
        response = client.get("/api/v1/tools/weather", params={"city": "南京"})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("city", response.json())
        self.assertIn("temperature", response.json())
        self.assertIn("description", response.json())
        print("[OK] 天气查询接口正常")
    
    def test_forecast_endpoint(self):
        """测试天气预报接口"""
        print("\n=== 天气预报接口测试 ===")
        response = client.get("/api/v1/tools/forecast", params={"city": "南京", "days": 3})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("city", response.json())
        self.assertIn("forecast", response.json())
        self.assertIsInstance(response.json()["forecast"], list)
        print("[OK] 天气预报接口正常")
    
    def test_geocode_endpoint(self):
        """测试地理编码接口"""
        print("\n=== 地理编码接口测试 ===")
        response = client.get("/api/v1/tools/geocode", params={"address": "南京市玄武区紫金山", "city": "南京"})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("location", response.json())
        self.assertIn("city", response.json())
        print("[OK] 地理编码接口正常")
    
    def test_route_endpoint(self):
        """测试路线查询接口"""
        print("\n=== 路线查询接口测试 ===")
        response = client.get("/api/v1/tools/route", params={"origin": "南京站", "destination": "紫金山", "city": "南京"})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("distance", response.json())
        self.assertIn("travel_time", response.json())
        print("[OK] 路线查询接口正常")
    
    def test_search_endpoint(self):
        """测试地点搜索接口"""
        print("\n=== 地点搜索接口测试 ===")
        response = client.get("/api/v1/tools/search", params={"keyword": "餐厅", "city": "南京"})
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("places", response.json())
        self.assertIsInstance(response.json()["places"], list)
        print("[OK] 地点搜索接口正常")
    
    def test_location_endpoint(self):
        """测试用户位置接口"""
        print("\n=== 用户位置接口测试 ===")
        response = client.get("/api/v1/tools/location")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("city", response.json())
        self.assertIn("lat", response.json())
        self.assertIn("lng", response.json())
        print("[OK] 用户位置接口正常")
    
    def test_map_config_endpoint(self):
        """测试地图配置接口"""
        print("\n=== 地图配置接口测试 ===")
        response = client.get("/api/v1/tools/map/config")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("map_api_key", response.json())
        self.assertIn("map_api_url", response.json())
        print("[OK] 地图配置接口正常")
    
    def test_weather_invalid_city(self):
        """测试无效城市参数"""
        print("\n=== 无效城市参数测试 ===")
        response = client.get("/api/v1/tools/weather", params={"city": ""})
        print(f"状态码: {response.status_code}")
        # 空城市应该返回错误或默认值
        self.assertIn(response.status_code, [200, 422])
        print("[OK] 无效城市参数处理正常")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("API端点测试套件")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(TestAPIEndpoints('test_health_check'))
    suite.addTest(TestAPIEndpoints('test_weather_endpoint'))
    suite.addTest(TestAPIEndpoints('test_forecast_endpoint'))
    suite.addTest(TestAPIEndpoints('test_geocode_endpoint'))
    suite.addTest(TestAPIEndpoints('test_route_endpoint'))
    suite.addTest(TestAPIEndpoints('test_search_endpoint'))
    suite.addTest(TestAPIEndpoints('test_location_endpoint'))
    suite.addTest(TestAPIEndpoints('test_map_config_endpoint'))
    suite.addTest(TestAPIEndpoints('test_weather_invalid_city'))
    
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
        print("[OK] 所有API端点测试通过！")
    else:
        print("[FAIL] 部分测试失败，请检查代码")


if __name__ == '__main__':
    run_tests()
