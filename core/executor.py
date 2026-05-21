"""执行层 - 执行Agent

负责执行预订动作，生成最终行程单。
"""
import uuid
from typing import Dict
from config.logging_config import logger

class ExecutionAgent:
    """执行Agent"""
    
    def __init__(self):
        self.simulated_database = {}
    
    def execute_plan(self, plan_id: str, plan_details: Dict) -> Dict:
        """执行计划，生成行程单"""
        logger.info(f"[ExecutionAgent] 开始执行计划 - plan_id: {plan_id}")
        logger.debug(f"[ExecutionAgent] 计划详情 - 活动数: {len(plan_details.get('activities', []))}, 餐厅数: {len(plan_details.get('restaurants', []))}")
        
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
            logger.info(f"[ExecutionAgent] 开始预订活动 - 数量: {len(plan_details['activities'])}")
            for i, activity in enumerate(plan_details["activities"]):
                booking_ref = f"BK-{uuid.uuid4().hex[:6]}"
                itinerary["details"]["activities"].append({
                    "name": activity.get("name", ""),
                    "time": activity.get("time", ""),
                    "location": activity.get("location", ""),
                    "status": "confirmed",
                    "booking_ref": booking_ref
                })
                logger.debug(f"[ExecutionAgent] 活动预订成功 - {i+1}. {activity.get('name')} - 预订号: {booking_ref}")
        
        # 模拟预订餐厅
        if plan_details.get("restaurants"):
            logger.info(f"[ExecutionAgent] 开始预订餐厅 - 数量: {len(plan_details['restaurants'])}")
            for i, restaurant in enumerate(plan_details["restaurants"]):
                booking_ref = f"RES-{uuid.uuid4().hex[:6]}"
                itinerary["details"]["restaurants"].append({
                    "name": restaurant.get("name", ""),
                    "time": restaurant.get("time", ""),
                    "location": restaurant.get("location", ""),
                    "status": "booked",
                    "booking_ref": booking_ref
                })
                logger.debug(f"[ExecutionAgent] 餐厅预订成功 - {i+1}. {restaurant.get('name')} - 预订号: {booking_ref}")
        
        # 保存到模拟数据库
        self.simulated_database[itinerary_id] = itinerary
        logger.info(f"[ExecutionAgent] 行程单生成完成 - itinerary_id: {itinerary_id}, 状态: {itinerary['status']}")
        
        return itinerary
    
    def get_itinerary(self, itinerary_id: str) -> Dict:
        """查询行程单"""
        itinerary = self.simulated_database.get(itinerary_id)
        if itinerary:
            logger.info(f"[ExecutionAgent] 查询行程单成功 - itinerary_id: {itinerary_id}")
        else:
            logger.warning(f"[ExecutionAgent] 查询行程单失败 - itinerary_id: {itinerary_id} 不存在")
        return itinerary or {}
    
    def cancel_itinerary(self, itinerary_id: str) -> bool:
        """取消行程单"""
        if itinerary_id in self.simulated_database:
            self.simulated_database[itinerary_id]["status"] = "cancelled"
            logger.info(f"[ExecutionAgent] 行程单已取消 - itinerary_id: {itinerary_id}")
            return True
        logger.warning(f"[ExecutionAgent] 取消行程单失败 - itinerary_id: {itinerary_id} 不存在")
        return False
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")