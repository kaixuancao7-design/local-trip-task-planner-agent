"""执行层 - 执行Agent

负责执行预订动作，生成最终行程单。
"""
import uuid
from typing import Dict

class ExecutionAgent:
    """执行Agent"""
    
    def __init__(self):
        self.simulated_database = {}
    
    def execute_plan(self, plan_id: str, plan_details: Dict) -> Dict:
        """执行计划，生成行程单"""
        itinerary_id = f"ITN-{uuid.uuid4().hex[:8]}"
        
        itinerary = {
            "itinerary_id": itinerary_id,
            "plan_id": plan_id,
            "status": "confirmed",
            "message": "预订成功",
            "details": {
                "activities": [],
                "restaurants": []
            },
            "created_at": self._get_current_time()
        }
        
        # 模拟预订活动
        if plan_details.get("activities"):
            for activity in plan_details["activities"]:
                itinerary["details"]["activities"].append({
                    "name": activity.get("name", ""),
                    "time": activity.get("time", ""),
                    "location": activity.get("location", ""),
                    "status": "confirmed",
                    "booking_ref": f"BK-{uuid.uuid4().hex[:6]}"
                })
        
        # 模拟预订餐厅
        if plan_details.get("restaurants"):
            for restaurant in plan_details["restaurants"]:
                itinerary["details"]["restaurants"].append({
                    "name": restaurant.get("name", ""),
                    "time": restaurant.get("time", ""),
                    "location": restaurant.get("location", ""),
                    "status": "booked",
                    "booking_ref": f"RES-{uuid.uuid4().hex[:6]}"
                })
        
        # 保存到模拟数据库
        self.simulated_database[itinerary_id] = itinerary
        
        return itinerary
    
    def get_itinerary(self, itinerary_id: str) -> Dict:
        """查询行程单"""
        return self.simulated_database.get(itinerary_id, {})
    
    def cancel_itinerary(self, itinerary_id: str) -> bool:
        """取消行程单"""
        if itinerary_id in self.simulated_database:
            self.simulated_database[itinerary_id]["status"] = "cancelled"
            return True
        return False
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")