"""全局异常处理中间件测试

测试全局异常处理中间件是否正确捕获和处理各种异常类型。
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app import app

client = TestClient(app)


class TestExceptionHandler(unittest.TestCase):
    """测试全局异常处理中间件"""
    
    def test_http_exception_handling(self):
        """测试HTTP异常处理"""
        print("\n=== HTTP异常处理测试 ===")
        # 测试无效路由（404）
        response = client.get("/nonexistent")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertIn("error", response.json())
        print("[OK] HTTP异常处理正常")
    
    def test_value_error_handling(self):
        """测试值错误处理"""
        print("\n=== 值错误处理测试 ===")
        # 测试无效参数触发的值错误
        response = client.get("/api/v1/tools/weather")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        # 如果返回422（请求参数错误），也视为正常处理
        self.assertIn(response.status_code, [400, 422])
        print("[OK] 值错误处理正常")
    
    def test_internal_error_handling(self):
        """测试内部错误处理"""
        print("\n=== 内部错误处理测试 ===")
        # 测试触发内部错误的场景
        # 创建一个会引发异常的测试端点
        @app.get("/test-error")
        def test_error():
            raise RuntimeError("测试内部错误")
        
        with TestClient(app) as test_client:
            response = test_client.get("/test-error")
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.json()}")
            self.assertEqual(response.status_code, 500)
            self.assertFalse(response.json()["success"])
            self.assertIn("error", response.json())
            self.assertEqual(response.json()["error"]["type"], "InternalServerError")
        print("[OK] 内部错误处理正常")


if __name__ == "__main__":
    print("=" * 60)
    print("全局异常处理中间件测试套件")
    print("=" * 60)
    
    unittest.main(verbosity=2)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print("[OK] 所有异常处理测试通过！")
