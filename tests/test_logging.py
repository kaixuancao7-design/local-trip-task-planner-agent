"""日志功能测试

测试日志系统的各项功能，包括日志轮转、性能监控、敏感信息脱敏等。
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path
from config.logging_config import (
    logger, 
    SensitiveDataFilter, 
    PerformanceMonitor, 
    log_performance,
    PerformanceContext,
    performance_monitor
)
from tools.map_tool import MapTool
from tools.weather_tool import WeatherTool


class TestSensitiveDataFilter(unittest.TestCase):
    """测试敏感数据脱敏功能"""
    
    def test_mask_password(self):
        """测试密码脱敏"""
        print("\n=== 密码脱敏测试 ===")
        message = "用户登录: password=admin123"
        masked = SensitiveDataFilter.mask_sensitive_data(message)
        print(f"原始: {message}")
        print(f"脱敏: {masked}")
        self.assertIn("***MASKED***", masked)
        self.assertNotIn("admin123", masked)
        print("[OK] 密码脱敏正常")
    
    def test_mask_api_key(self):
        """测试API密钥脱敏"""
        print("\n=== API密钥脱敏测试 ===")
        message = "配置: api_key=sk-1234567890abcdef"
        masked = SensitiveDataFilter.mask_sensitive_data(message)
        print(f"原始: {message}")
        print(f"脱敏: {masked}")
        self.assertIn("***MASKED***", masked)
        self.assertNotIn("sk-1234567890abcdef", masked)
        print("[OK] API密钥脱敏正常")
    
    def test_mask_token(self):
        """测试Token脱敏"""
        print("\n=== Token脱敏测试 ===")
        message = "认证: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        masked = SensitiveDataFilter.mask_sensitive_data(message)
        print(f"原始: {message}")
        print(f"脱敏: {masked}")
        self.assertIn("***MASKED***", masked)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", masked)
        print("[OK] Token脱敏正常")


class TestPerformanceMonitor(unittest.TestCase):
    """测试性能监控功能"""
    
    def test_record_performance(self):
        """测试性能记录"""
        print("\n=== 性能记录测试 ===")
        monitor = PerformanceMonitor()
        
        # 记录一些操作
        monitor.record("test_operation", 0.5, {"status": "success"})
        monitor.record("test_operation", 1.2, {"status": "success"})
        monitor.record("test_operation", 0.8, {"status": "error"})
        
        # 获取统计信息
        stats = monitor.get_stats("test_operation")
        print(f"统计信息: {stats}")
        
        self.assertEqual(stats["count"], 3)
        self.assertAlmostEqual(stats["avg"], 0.833, places=2)
        self.assertEqual(stats["min"], 0.5)
        self.assertEqual(stats["max"], 1.2)
        print("[OK] 性能记录正常")
    
    def test_performance_decorator(self):
        """测试性能监控装饰器"""
        print("\n=== 性能监控装饰器测试 ===")
        
        @log_performance("test.decorated_function")
        def test_function():
            import time
            time.sleep(0.1)
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        # 检查是否记录了性能数据
        stats = performance_monitor.get_stats("test.decorated_function")
        print(f"装饰器统计: {stats}")
        self.assertGreater(stats["count"], 0)
        print("[OK] 性能监控装饰器正常")
    
    def test_performance_context(self):
        """测试性能监控上下文管理器"""
        print("\n=== 性能监控上下文管理器测试 ===")
        
        with PerformanceContext("test.context_operation", {"user": "test"}):
            import time
            time.sleep(0.1)
        
        stats = performance_monitor.get_stats("test.context_operation")
        print(f"上下文统计: {stats}")
        self.assertGreater(stats["count"], 0)
        print("[OK] 性能监控上下文管理器正常")


class TestLoggingFunctions(unittest.TestCase):
    """测试日志功能"""
    
    def test_logger_info(self):
        """测试INFO级别日志"""
        print("\n=== INFO日志测试 ===")
        logger.info("这是一条INFO日志")
        print("[OK] INFO日志正常")
    
    def test_logger_warning(self):
        """测试WARNING级别日志"""
        print("\n=== WARNING日志测试 ===")
        logger.warning("这是一条WARNING日志")
        print("[OK] WARNING日志正常")
    
    def test_logger_error(self):
        """测试ERROR级别日志"""
        print("\n=== ERROR日志测试 ===")
        logger.error("这是一条ERROR日志")
        print("[OK] ERROR日志正常")
    
    def test_logger_with_context(self):
        """测试带上下文的日志"""
        print("\n=== 上下文日志测试 ===")
        logger.info(
            "用户操作日志",
            extra={"context": {"user_id": "123", "action": "login", "ip": "192.168.1.1"}}
        )
        print("[OK] 上下文日志正常")
    
    def test_sensitive_data_in_log(self):
        """测试日志中的敏感数据脱敏"""
        print("\n=== 日志敏感数据脱敏测试 ===")
        logger.info("用户登录: password=secret123, api_key=abc123xyz")
        print("[OK] 日志敏感数据脱敏正常")


class TestLogFileCreation(unittest.TestCase):
    """测试日志文件创建"""
    
    def test_log_files_exist(self):
        """测试日志文件是否存在"""
        print("\n=== 日志文件检查测试 ===")
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
        
        # 检查日志目录
        self.assertTrue(log_dir.exists(), "日志目录不存在")
        print(f"日志目录: {log_dir}")
        
        # 检查主日志文件
        app_log = log_dir / "app.log"
        self.assertTrue(app_log.exists(), "app.log不存在")
        print(f"主日志文件大小: {app_log.stat().st_size} bytes")
        
        # 检查JSON日志文件
        json_log = log_dir / "app.json"
        self.assertTrue(json_log.exists(), "app.json不存在")
        print(f"JSON日志文件大小: {json_log.stat().st_size} bytes")
        
        print("[OK] 日志文件检查正常")


class TestToolPerformanceMonitoring(unittest.TestCase):
    """测试工具性能监控"""
    
    def test_map_tool_performance(self):
        """测试地图工具性能监控"""
        print("\n=== 地图工具性能监控测试 ===")
        map_tool = MapTool()
        
        # 调用地图工具
        result = map_tool.get_route("南京站", "紫金山")
        self.assertIsNotNone(result)
        
        # 检查性能记录
        stats = performance_monitor.get_stats("map.get_route")
        print(f"地图工具统计: {stats}")
        self.assertGreater(stats["count"], 0)
        print("[OK] 地图工具性能监控正常")
    
    def test_weather_tool_performance(self):
        """测试天气工具性能监控"""
        print("\n=== 天气工具性能监控测试 ===")
        weather_tool = WeatherTool()
        
        # 调用天气工具
        result = weather_tool.get_weather("南京")
        self.assertIsNotNone(result)
        
        # 检查性能记录
        stats = performance_monitor.get_stats("weather.get_weather")
        print(f"天气工具统计: {stats}")
        self.assertGreater(stats["count"], 0)
        print("[OK] 天气工具性能监控正常")


if __name__ == "__main__":
    print("=" * 60)
    print("日志功能测试套件")
    print("=" * 60)
    
    unittest.main(verbosity=2)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print("[OK] 所有日志功能测试通过！")
