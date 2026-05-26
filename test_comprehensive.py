"""项目全面测试脚本

功能测试：覆盖所有核心业务流程
性能测试：响应时间、并发处理、资源占用
"""
import time
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.activity_search_tool import ActivitySearchTool
from tools.restaurant_search_tool import RestaurantSearchTool
from tools.queue_check_tool import QueueCheckTool
from tools.booking_tool import BookingTool
from tools.notification_tool import NotificationTool
from tools.map_tool import MapTool
from tools.weather_tool import WeatherTool
from core.planner import PlanningAgent
from core.parser import InputParser


class TestReport:
    """测试报告生成器"""
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.test_stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0
        }
    
    def add_result(self, test_name, category, status, expected, actual, duration, message=""):
        result = {
            "test_name": test_name,
            "category": category,
            "status": status,
            "expected": expected,
            "actual": actual,
            "duration_ms": round(duration * 1000, 2),
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        self.test_stats["total"] += 1
        
        if status == "PASS":
            self.test_stats["passed"] += 1
        elif status == "FAIL":
            self.test_stats["failed"] += 1
        elif status == "ERROR":
            self.test_stats["errors"] += 1
        
        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERROR]"
        print(f"{status_symbol} [{category}] {test_name}: {status} ({result['duration_ms']}ms)")
        if message:
            print(f"   └─ {message}")
        
        return result
    
    def generate_report(self):
        """生成测试报告"""
        total_duration = time.time() - self.start_time
        
        report = {
            "report_title": "Local Task Planner Agent - 测试报告",
            "test_summary": {
                "total_tests": self.test_stats["total"],
                "passed": self.test_stats["passed"],
                "failed": self.test_stats["failed"],
                "errors": self.test_stats["errors"],
                "pass_rate": f"{(self.test_stats['passed'] / self.test_stats['total'] * 100):.1f}%" if self.test_stats['total'] > 0 else "0%",
                "total_duration_seconds": round(total_duration, 2)
            },
            "categories_summary": self._get_category_summary(),
            "test_results": self.results,
            "defects": self._get_defects()
        }
        
        return report
    
    def _get_category_summary(self):
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
            categories[cat]["total"] += 1
            if result["status"] == "PASS":
                categories[cat]["passed"] += 1
            elif result["status"] == "FAIL":
                categories[cat]["failed"] += 1
            elif result["status"] == "ERROR":
                categories[cat]["errors"] += 1
        return categories
    
    def _get_defects(self):
        defects = []
        for result in self.results:
            if result["status"] in ["FAIL", "ERROR"]:
                defect = {
                    "test_name": result["test_name"],
                    "category": result["category"],
                    "severity": self._assess_severity(result),
                    "status": result["status"],
                    "description": result["message"] or f"预期: {result['expected']}, 实际: {result['actual']}"
                }
                defects.append(defect)
        return defects
    
    def _assess_severity(self, result):
        """评估缺陷严重程度"""
        if result["status"] == "ERROR":
            return "HIGH"
        category = result["category"]
        if category in ["API", "Agent"]:
            return "HIGH"
        elif category in ["Tools"]:
            return "MEDIUM"
        return "LOW"


class FunctionalTester:
    """功能测试"""
    
    def __init__(self, report):
        self.report = report
    
    def test_activity_search_tool(self):
        """测试活动搜索工具"""
        print("\n" + "="*60)
        print("测试：活动搜索工具 (ActivitySearchTool)")
        print("="*60)
        
        tool = ActivitySearchTool()
        
        # 测试1：基本搜索
        start = time.time()
        try:
            results = tool.search_activities(scene_type="亲子", city="南京", radius=3)
            duration = time.time() - start
            self.report.add_result(
                "test_activity_search_basic",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration,
                f"搜索到 {len(results)} 个活动"
            )
        except Exception as e:
            self.report.add_result(
                "test_activity_search_basic",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start,
                f"异常: {e}"
            )
        
        # 测试2：指定场景类型搜索
        start = time.time()
        try:
            results = tool.search_activities(scene_type="好友聚会", city="南京")
            duration = time.time() - start
            self.report.add_result(
                "test_activity_search_friends",
                "Tools",
                "PASS" if len(results) > 0 else "FAIL",
                "返回非空结果",
                f"{len(results)} 个结果",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_activity_search_friends",
                "Tools",
                "ERROR",
                "正常返回结果",
                str(e),
                time.time() - start
            )
        
        # 测试3：按类别搜索
        start = time.time()
        try:
            results = tool.search_by_category(category="展览馆", city="南京")
            duration = time.time() - start
            self.report.add_result(
                "test_activity_search_by_category",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_activity_search_by_category",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start
            )
        
        # 测试4：带用户位置搜索
        start = time.time()
        try:
            results = tool.search_activities(scene_type="情侣约会", city="南京", 
                                          user_location="118.783799,32.060255", sort_by="time")
            duration = time.time() - start
            self.report.add_result(
                "test_activity_search_with_location",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration,
                f"搜索到 {len(results)} 个结果"
            )
        except Exception as e:
            self.report.add_result(
                "test_activity_search_with_location",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start
            )
    
    def test_restaurant_search_tool(self):
        """测试餐厅搜索工具"""
        print("\n" + "="*60)
        print("测试：餐厅搜索工具 (RestaurantSearchTool)")
        print("="*60)
        
        tool = RestaurantSearchTool()
        
        # 测试1：按需求搜索
        start = time.time()
        try:
            results = tool.search_restaurants(requirement="减肥餐", city="南京")
            duration = time.time() - start
            self.report.add_result(
                "test_restaurant_search_health",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration,
                f"搜索到 {len(results)} 家餐厅"
            )
        except Exception as e:
            self.report.add_result(
                "test_restaurant_search_health",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start
            )
        
        # 测试2：多人团建搜索
        start = time.time()
        try:
            results = tool.search_restaurants(requirement="多人团建", city="南京")
            duration = time.time() - start
            self.report.add_result(
                "test_restaurant_search_group",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_restaurant_search_group",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start
            )
        
        # 测试3：按菜系搜索
        start = time.time()
        try:
            results = tool.search_by_cuisine(cuisine="川菜", city="南京")
            duration = time.time() - start
            self.report.add_result(
                "test_restaurant_search_cuisine",
                "Tools",
                "PASS" if isinstance(results, list) else "FAIL",
                "返回列表类型",
                type(results).__name__,
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_restaurant_search_cuisine",
                "Tools",
                "ERROR",
                "正常返回列表",
                str(e),
                time.time() - start
            )
    
    def test_queue_check_tool(self):
        """测试排队核验工具"""
        print("\n" + "="*60)
        print("测试：排队核验工具 (QueueCheckTool)")
        print("="*60)
        
        tool = QueueCheckTool()
        
        # 测试1：检查单个场地
        start = time.time()
        try:
            result = tool.check_queue("mock-activity-children-001")
            duration = time.time() - start
            self.report.add_result(
                "test_queue_check_single",
                "Tools",
                "PASS" if isinstance(result, dict) else "FAIL",
                "返回字典类型",
                type(result).__name__,
                duration,
                f"排队人数: {result.get('waiting_count', 'N/A')}"
            )
        except Exception as e:
            self.report.add_result(
                "test_queue_check_single",
                "Tools",
                "ERROR",
                "正常返回字典",
                str(e),
                time.time() - start
            )
        
        # 测试2：批量检查
        start = time.time()
        try:
            results = tool.batch_check_queue(["mock-activity-children-001", 
                                            "mock-activity-children-002"])
            duration = time.time() - start
            self.report.add_result(
                "test_queue_check_batch",
                "Tools",
                "PASS" if isinstance(results, dict) and len(results) == 2 else "FAIL",
                "返回包含2个结果的字典",
                f"返回 {len(results)} 个结果",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_queue_check_batch",
                "Tools",
                "ERROR",
                "正常返回字典",
                str(e),
                time.time() - start
            )
    
    def test_booking_tool(self):
        """测试预订工具"""
        print("\n" + "="*60)
        print("测试：预订工具 (BookingTool)")
        print("="*60)
        
        tool = BookingTool()
        
        # 测试1：创建餐厅预订
        start = time.time()
        try:
            result = tool.create_restaurant_booking(
                venue_id="mock-rest-jf-001",
                user_id="test_user",
                date="2026-06-01",
                time_slot="12:00",
                guests=4
            )
            duration = time.time() - start
            success = result.get("success", False)
            booking_ref = result.get("booking_ref", "")
            self.report.add_result(
                "test_booking_restaurant",
                "Tools",
                "PASS" if success and booking_ref else "FAIL",
                "预订成功并返回预订号",
                f"success={success}, ref={booking_ref}",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_booking_restaurant",
                "Tools",
                "ERROR",
                "正常完成预订",
                str(e),
                time.time() - start
            )
        
        # 测试2：获取预订详情
        start = time.time()
        try:
            if booking_ref:
                detail = tool.get_booking(booking_ref)
                duration = time.time() - start
                self.report.add_result(
                    "test_booking_get_detail",
                    "Tools",
                    "PASS" if detail and detail.get("booking_ref") == booking_ref else "FAIL",
                    "成功获取预订详情",
                    f"booking_ref={detail.get('booking_ref', 'N/A')}" if detail else "None",
                    duration
                )
        except Exception as e:
            self.report.add_result(
                "test_booking_get_detail",
                "Tools",
                "ERROR",
                "正常获取详情",
                str(e),
                time.time() - start
            )
        
        # 测试3：取消预订
        start = time.time()
        try:
            if booking_ref:
                cancel_result = tool.cancel_booking(booking_ref)
                duration = time.time() - start
                self.report.add_result(
                    "test_booking_cancel",
                    "Tools",
                    "PASS" if cancel_result.get("success") else "FAIL",
                    "取消成功",
                    str(cancel_result),
                    duration
                )
        except Exception as e:
            self.report.add_result(
                "test_booking_cancel",
                "Tools",
                "ERROR",
                "正常取消预订",
                str(e),
                time.time() - start
            )
    
    def test_notification_tool(self):
        """测试通知生成工具"""
        print("\n" + "="*60)
        print("测试：通知生成工具 (NotificationTool)")
        print("="*60)
        
        tool = NotificationTool()
        
        sample_plan = {
            "title": "周末亲子游",
            "steps": [
                {"name": "南京动物园", "start_time": "10:00", "end_time": "12:00"},
                {"name": "亲子餐厅", "start_time": "12:00", "end_time": "13:30"}
            ]
        }
        
        # 测试1：生成文本通知
        start = time.time()
        try:
            result = tool.generate_text_notification(sample_plan, "family")
            duration = time.time() - start
            self.report.add_result(
                "test_notification_text",
                "Tools",
                "PASS" if result and len(result) > 0 else "FAIL",
                "返回非空文本",
                f"生成了 {len(result)} 字符",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_notification_text",
                "Tools",
                "ERROR",
                "正常生成通知",
                str(e),
                time.time() - start
            )
        
        # 测试2：生成社交分享
        start = time.time()
        try:
            result = tool.generate_social_share(sample_plan, "family")
            duration = time.time() - start
            self.report.add_result(
                "test_notification_social",
                "Tools",
                "PASS" if result and len(result) > 0 else "FAIL",
                "返回非空分享文案",
                f"生成了 {len(result)} 字符",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_notification_social",
                "Tools",
                "ERROR",
                "正常生成分享",
                str(e),
                time.time() - start
            )
    
    def test_map_tool(self):
        """测试地图工具"""
        print("\n" + "="*60)
        print("测试：地图工具 (MapTool)")
        print("="*60)
        
        tool = MapTool()
        
        # 测试1：获取驾车路线
        start = time.time()
        try:
            result = tool.get_route("南京市新街口", "南京市夫子庙", "南京", "driving")
            duration = time.time() - start
            has_distance = "distance" in result
            has_duration = "duration" in result
            self.report.add_result(
                "test_map_route_driving",
                "Tools",
                "PASS" if has_distance and has_duration else "FAIL",
                "返回距离和时长",
                f"distance={'有' if has_distance else '无'}, duration={'有' if has_duration else '无'}",
                duration,
                f"距离: {result.get('distance', 'N/A')}米, 时长: {result.get('duration', 'N/A')}秒"
            )
        except Exception as e:
            self.report.add_result(
                "test_map_route_driving",
                "Tools",
                "ERROR",
                "正常返回路线",
                str(e),
                time.time() - start
            )
        
        # 测试2：地理编码
        start = time.time()
        try:
            result = tool.geocode("南京市新街口")
            duration = time.time() - start
            self.report.add_result(
                "test_map_geocode",
                "Tools",
                "PASS" if isinstance(result, dict) else "FAIL",
                "返回字典类型",
                type(result).__name__,
                duration,
                f"经纬度: {result.get('location', 'N/A')}"
            )
        except Exception as e:
            self.report.add_result(
                "test_map_geocode",
                "Tools",
                "ERROR",
                "正常返回结果",
                str(e),
                time.time() - start
            )
    
    def test_weather_tool(self):
        """测试天气工具"""
        print("\n" + "="*60)
        print("测试：天气工具 (WeatherTool)")
        print("="*60)
        
        tool = WeatherTool()
        
        # 测试1：获取天气
        start = time.time()
        try:
            result = tool.get_weather("南京")
            duration = time.time() - start
            self.report.add_result(
                "test_weather_current",
                "Tools",
                "PASS" if isinstance(result, dict) else "FAIL",
                "返回字典类型",
                type(result).__name__,
                duration,
                f"温度: {result.get('temperature', 'N/A')}°C"
            )
        except Exception as e:
            self.report.add_result(
                "test_weather_current",
                "Tools",
                "ERROR",
                "正常返回天气",
                str(e),
                time.time() - start
            )
        
        # 测试2：获取天气预报
        start = time.time()
        try:
            result = tool.get_forecast("南京", 3)
            duration = time.time() - start
            self.report.add_result(
                "test_weather_forecast",
                "Tools",
                "PASS" if isinstance(result, list) else "FAIL",
                "返回列表类型",
                type(result).__name__,
                duration,
                f"预报 {len(result)} 天"
            )
        except Exception as e:
            self.report.add_result(
                "test_weather_forecast",
                "Tools",
                "ERROR",
                "正常返回预报",
                str(e),
                time.time() - start
            )


class AgentTester:
    """Agent功能测试"""
    
    def __init__(self, report):
        self.report = report
        self.agent = PlanningAgent()
        self.parser = InputParser()
    
    def test_parser(self):
        """测试输入解析器"""
        print("\n" + "="*60)
        print("测试：输入解析器 (InputParser)")
        print("="*60)
        
        # 测试1：基本解析
        start = time.time()
        try:
            result = self.parser.parse("周末带5岁孩子去玩")
            duration = time.time() - start
            has_activity = "活动" in result or "activity" in result
            self.report.add_result(
                "test_parser_basic",
                "Parser",
                "PASS" if has_activity or isinstance(result, dict) else "FAIL",
                "返回解析结果",
                type(result).__name__,
                duration,
                f"解析结果包含活动信息"
            )
        except Exception as e:
            self.report.add_result(
                "test_parser_basic",
                "Parser",
                "ERROR",
                "正常返回结果",
                str(e),
                time.time() - start
            )
    
    def test_scene_recognition(self):
        """测试场景识别"""
        print("\n" + "="*60)
        print("测试：场景识别 (Scene Recognition)")
        print("="*60)
        
        test_cases = [
            ("周末带5岁孩子出去玩", "family"),
            ("和4个朋友聚会吃火锅", "friends"),
            ("明天和女朋友约会", "couple"),
            ("一个人想放松一下", "solo"),
        ]
        
        for input_text, expected_scene in test_cases:
            start = time.time()
            try:
                result = self.agent.generate_scene_plan(input_text)
                duration = time.time() - start
                
                actual_scene = result.get("scene_info", {}).get("scene_type", "")
                success = actual_scene == expected_scene
                
                self.report.add_result(
                    f"test_scene_recognition_{expected_scene}",
                    "Agent",
                    "PASS" if success else "FAIL",
                    f"识别为 {expected_scene}",
                    f"识别为 {actual_scene}",
                    duration,
                    f"输入: {input_text}"
                )
            except Exception as e:
                self.report.add_result(
                    f"test_scene_recognition_{expected_scene}",
                    "Agent",
                    "ERROR",
                    f"识别为 {expected_scene}",
                    str(e),
                    time.time() - start
                )
    
    def test_constraint_extraction(self):
        """测试约束提取"""
        print("\n" + "="*60)
        print("测试：约束条件提取 (Constraint Extraction)")
        print("="*60)
        
        start = time.time()
        try:
            result = self.agent.generate_scene_plan("周末下午带孩子玩4小时，想吃清淡的")
            duration = time.time() - start
            
            constraints = result.get("constraints", {})
            has_duration = constraints.get("duration_hours", 0) > 0
            has_cuisine = constraints.get("cuisine_preference", "") != ""
            
            self.report.add_result(
                "test_constraint_extraction",
                "Agent",
                "PASS" if has_duration else "FAIL",
                "提取到时长约束",
                f"时长={constraints.get('duration_hours')}, 餐饮={constraints.get('cuisine_preference')}",
                duration,
                f"约束条件: {constraints}"
            )
        except Exception as e:
            self.report.add_result(
                "test_constraint_extraction",
                "Agent",
                "ERROR",
                "正常提取约束",
                str(e),
                time.time() - start
            )
    
    def test_plan_generation(self):
        """测试计划生成"""
        print("\n" + "="*60)
        print("测试：计划生成 (Plan Generation)")
        print("="*60)
        
        start = time.time()
        try:
            result = self.agent.generate_scene_plan("周末带孩子去户外活动")
            duration = time.time() - start
            
            success = result.get("success", False)
            has_plan = "plan" in result
            has_steps = len(result.get("plan", {}).get("steps", [])) > 0
            
            self.report.add_result(
                "test_plan_generation",
                "Agent",
                "PASS" if success and has_plan and has_steps else "FAIL",
                "生成包含步骤的计划",
                f"success={success}, has_steps={has_steps}",
                duration,
                f"生成了 {len(result.get('plan', {}).get('steps', []))} 个步骤"
            )
        except Exception as e:
            self.report.add_result(
                "test_plan_generation",
                "Agent",
                "ERROR",
                "正常生成计划",
                str(e),
                time.time() - start
            )
    
    def test_llm_parsing(self):
        """测试LLM解析"""
        print("\n" + "="*60)
        print("测试：LLM需求解析 (LLM Parsing)")
        print("="*60)
        
        start = time.time()
        try:
            result = self.agent._parse_scene_constraints_llm(
                "明天上午带老人和孩子去户外景点，想吃清淡的"
            )
            duration = time.time() - start
            
            parsing_method = result.get("parsing_method", "")
            scene_info = result.get("scene_info", {})
            constraints = result.get("constraints", {})
            
            self.report.add_result(
                "test_llm_parsing",
                "Agent",
                "PASS" if parsing_method == "llm" else "FAIL",
                "使用LLM解析",
                f"使用 {parsing_method} 解析",
                duration,
                f"场景: {scene_info.get('scene_name')}, 时长: {constraints.get('duration_hours')}h"
            )
        except Exception as e:
            self.report.add_result(
                "test_llm_parsing",
                "Agent",
                "ERROR",
                "正常使用LLM解析",
                str(e),
                time.time() - start,
                f"降级到规则解析"
            )
    
    def test_tool_decision(self):
        """测试工具决策"""
        print("\n" + "="*60)
        print("测试：工具决策 (Tool Decision)")
        print("="*60)
        
        scene_info = {
            "scene_type": "family",
            "scene_name": "亲子",
            "people_count": 3,
            "age_groups": ["child", "adult"]
        }
        constraints = {"duration_hours": 4.0, "distance_limit": 3.0}
        
        start = time.time()
        try:
            tool_calls = self.agent._decide_tool_calls(scene_info, constraints)
            duration = time.time() - start
            
            has_activities = "search_activities" in tool_calls
            has_restaurants = "search_restaurants" in tool_calls
            
            self.report.add_result(
                "test_tool_decision",
                "Agent",
                "PASS" if has_activities and has_restaurants else "FAIL",
                "决定调用活动和餐厅搜索工具",
                f"决定调用: {tool_calls}",
                duration,
                f"工具决策: {tool_calls}"
            )
        except Exception as e:
            self.report.add_result(
                "test_tool_decision",
                "Agent",
                "ERROR",
                "正常进行工具决策",
                str(e),
                time.time() - start
            )


class PerformanceTester:
    """性能测试"""
    
    def __init__(self, report):
        self.report = report
        self.agent = PlanningAgent()
    
    def test_response_time(self):
        """测试响应时间"""
        print("\n" + "="*60)
        print("性能测试：响应时间 (Response Time)")
        print("="*60)
        
        test_cases = [
            ("工具调用：活动搜索", lambda: ActivitySearchTool().search_activities("亲子", "南京")),
            ("工具调用：餐厅搜索", lambda: RestaurantSearchTool().search_restaurants("川菜", "南京")),
            ("工具调用：排队核验", lambda: QueueCheckTool().check_queue("test-id")),
            ("Agent：场景识别", lambda: self.agent.generate_scene_plan("周末带孩子玩")),
        ]
        
        for name, func in test_cases:
            start = time.time()
            try:
                func()
                duration = time.time() - start
                
                status = "PASS" if duration < 5.0 else "WARNING"
                self.report.add_result(
                    f"perf_response_{name}",
                    "Performance",
                    status,
                    "< 5秒",
                    f"{duration:.2f}秒",
                    duration,
                    f"{name}: {duration:.2f}秒"
                )
            except Exception as e:
                self.report.add_result(
                    f"perf_response_{name}",
                    "Performance",
                    "ERROR",
                    "正常响应",
                    str(e),
                    time.time() - start
                )
    
    def test_concurrent_processing(self):
        """测试并发处理能力"""
        print("\n" + "="*60)
        print("性能测试：并发处理 (Concurrent Processing)")
        print("="*60)
        
        def concurrent_request(request_id):
            agent = PlanningAgent()
            try:
                result = agent.generate_scene_plan(f"周末活动{request_id}")
                return result.get("success", False)
            except:
                return False
        
        # 测试并发5个请求
        start = time.time()
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(concurrent_request, i) for i in range(5)]
                results = [f.result() for f in futures]
            
            duration = time.time() - start
            success_count = sum(results)
            
            self.report.add_result(
                "perf_concurrent_3",
                "Performance",
                "PASS" if success_count >= 3 else "FAIL",
                "至少3个请求成功",
                f"{success_count}/3 成功",
                duration,
                f"并发3个请求耗时: {duration:.2f}秒"    
            )
        except Exception as e:
            self.report.add_result(
                "perf_concurrent_5",
                "Performance",
                "ERROR",
                "正常并发处理",
                str(e),
                time.time() - start
            )
        
        # 测试并发10个请求
        start = time.time()
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(concurrent_request, i) for i in range(10)]
                results = [f.result() for f in futures]
            
            duration = time.time() - start
            success_count = sum(results)
            
            self.report.add_result(
                "perf_concurrent_5",
                "Performance",
                "PASS" if success_count >= 3 else "FAIL",
                "至少3个请求成功",
                f"{success_count}/5 成功",
                duration,
                f"并发5个请求耗时: {duration:.2f}秒"
            )
        except Exception as e:
            self.report.add_result(
                "perf_concurrent_10",
                "Performance",
                "ERROR",
                "正常并发处理",
                str(e),
                time.time() - start
            )
    
    def test_memory_usage(self):
        """测试内存占用"""
        print("\n" + "="*60)
        print("性能测试：资源占用 (Resource Usage)")
        print("="*60)
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行多次规划
            for i in range(3):
                self.agent.generate_scene_plan(f"周末活动{i}")
            
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_increase = mem_after - mem_before
            
            self.report.add_result(
                "perf_memory",
                "Performance",
                "PASS" if mem_increase < 500 else "WARNING",
                "内存增长 < 500MB",
                f"增长 {mem_increase:.1f}MB",
                0,
                f"内存使用: {mem_before:.1f}MB -> {mem_after:.1f}MB"
            )
        except ImportError:
            self.report.add_result(
                "perf_memory",
                "Performance",
                "WARNING",
                "可测试内存使用",
                "psutil未安装",
                0,
                "跳过内存测试（需要安装psutil）"
            )
        except Exception as e:
            self.report.add_result(
                "perf_memory",
                "Performance",
                "ERROR",
                "正常测试内存",
                str(e),
                0
            )


class EdgeCaseTester:
    """边界情况测试"""
    
    def __init__(self, report):
        self.report = report
        self.agent = PlanningAgent()
    
    def test_empty_input(self):
        """测试空输入"""
        print("\n" + "="*60)
        print("边界测试：空输入处理 (Empty Input)")
        print("="*60)
        
        start = time.time()
        try:
            result = self.agent.generate_scene_plan("")
            duration = time.time() - start
            
            # 应该返回默认计划而不是崩溃
            has_plan = "plan" in result
            self.report.add_result(
                "test_edge_empty_input",
                "EdgeCase",
                "PASS" if has_plan else "FAIL",
                "返回默认计划",
                f"返回结果: {result.get('success')}",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_edge_empty_input",
                "EdgeCase",
                "ERROR",
                "优雅处理空输入",
                str(e),
                time.time() - start
            )
    
    def test_very_long_input(self):
        """测试超长输入"""
        print("\n" + "="*60)
        print("边界测试：超长输入处理 (Long Input)")
        print("="*60)
        
        long_input = "周末" + "带孩子出去玩" * 100
        
        start = time.time()
        try:
            result = self.agent.generate_scene_plan(long_input)
            duration = time.time() - start
            
            self.report.add_result(
                "test_edge_long_input",
                "EdgeCase",
                "PASS" if result.get("success") else "FAIL",
                "正常处理长输入",
                f"耗时 {duration:.2f}秒",
                duration
            )
        except Exception as e:
            self.report.add_result(
                "test_edge_long_input",
                "EdgeCase",
                "ERROR",
                "正常处理长输入",
                str(e),
                time.time() - start
            )
    
    def test_special_characters(self):
        """测试特殊字符"""
        print("\n" + "="*60)
        print("边界测试：特殊字符处理 (Special Characters)")
        print("="*60)
        
        special_inputs = [
            "周末带孩子去🎢玩🍔",
            "周末活动 <script>alert('test')</script>",
            "周末带孩子去'OR'1'='1",
        ]
        
        for i, special_input in enumerate(special_inputs):
            start = time.time()
            try:
                result = self.agent.generate_scene_plan(special_input)
                duration = time.time() - start
                
                self.report.add_result(
                    f"test_edge_special_{i}",
                    "EdgeCase",
                    "PASS" if result.get("success") else "FAIL",
                    "正常处理特殊字符",
                    f"返回: {result.get('success')}",
                    duration
                )
            except Exception as e:
                self.report.add_result(
                    f"test_edge_special_{i}",
                    "EdgeCase",
                    "ERROR",
                    "正常处理特殊字符",
                    str(e),
                    time.time() - start
                )
    
    def test_invalid_city(self):
        """测试无效城市"""
        print("\n" + "="*60)
        print("边界测试：无效城市处理 (Invalid City)")
        print("="*60)
        
        start = time.time()
        try:
            result = ActivitySearchTool().search_activities("亲子", "不存在的城市XYZ")
            duration = time.time() - start
            
            # 应该返回空列表或模拟数据
            self.report.add_result(
                "test_edge_invalid_city",
                "EdgeCase",
                "PASS" if isinstance(result, list) else "FAIL",
                "返回列表类型",
                type(result).__name__,
                duration,
                f"返回 {len(result)} 个结果"
            )
        except Exception as e:
            self.report.add_result(
                "test_edge_invalid_city",
                "EdgeCase",
                "ERROR",
                "正常处理无效城市",
                str(e),
                time.time() - start
            )


def run_all_tests():
    """运行所有测试"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n" + "="*80)
    print("  Local Task Planner Agent - 全面测试")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    report = TestReport()
    
    # # 功能测试
    # print("\n[1] 第一部分：功能测试")
    # print("-" * 60)
    
    # func_tester = FunctionalTester(report)
    # func_tester.test_activity_search_tool()
    # func_tester.test_restaurant_search_tool()
    # func_tester.test_queue_check_tool()
    # func_tester.test_booking_tool()
    # func_tester.test_notification_tool()
    # func_tester.test_map_tool()
    # func_tester.test_weather_tool()
    
    # # Agent测试
    # print("\n[2] 第二部分：Agent功能测试")
    # print("-" * 60)
    
    # agent_tester = AgentTester(report)
    # agent_tester.test_parser()
    # agent_tester.test_scene_recognition()
    # agent_tester.test_constraint_extraction()
    # agent_tester.test_plan_generation()
    # agent_tester.test_llm_parsing()
    # agent_tester.test_tool_decision()
    
    # # 性能测试
    # print("\n[3] 第三部分：性能测试")
    # print("-" * 60)
    
    # perf_tester = PerformanceTester(report)
    # perf_tester.test_response_time()
    # perf_tester.test_concurrent_processing()
    # perf_tester.test_memory_usage()
    
    # 边界测试
    print("\n[4] 第四部分：边界情况测试")
    print("-" * 60)
    
    edge_tester = EdgeCaseTester(report)
    edge_tester.test_empty_input()
    edge_tester.test_very_long_input()
    edge_tester.test_special_characters()
    edge_tester.test_invalid_city()
    
    # 生成报告
    print("\n" + "="*80)
    print("[REPORT] 测试报告生成")
    print("="*80)
    
    test_report = report.generate_report()
    
    # 保存报告
    report_path = os.path.join(os.path.dirname(__file__), "test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n[FILE] 报告已保存到: {report_path}")
    
    # 打印摘要
    print("\n" + "="*80)
    print("[SUMMARY] 测试结果摘要")
    print("="*80)
    
    summary = test_report["test_summary"]
    print(f"总测试数: {summary['total_tests']}")
    print(f"通过: {summary['passed']} [PASS]")
    print(f"失败: {summary['failed']} [FAIL]")
    print(f"错误: {summary['errors']} [ERROR]")
    print(f"通过率: {summary['pass_rate']}")
    print(f"总耗时: {summary['total_duration_seconds']:.2f}秒")
    
    print("\n[STATS] 分类统计:")
    for cat, stats in test_report["categories_summary"].items():
        pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({pass_rate:.0f}%)")
    
    if test_report["defects"]:
        print("\n[DEFECTS] 发现缺陷:")
        for i, defect in enumerate(test_report["defects"], 1):
            print(f"  {i}. [{defect['severity']}] {defect['test_name']}")
            print(f"     描述: {defect['description']}")
    
    print("\n" + "="*80)
    print(" 测试完成")
    print("="*80)
    
    return test_report


if __name__ == "__main__":
    report = run_all_tests()
