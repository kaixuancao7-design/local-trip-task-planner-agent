"""决策层 - 规划Agent

负责基于用户需求和历史偏好，生成完整的活动方案。
"""
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import json
import uuid
from config.settings import settings
from tools.map_tool import MapTool

class PlanningAgent:
    """规划Agent"""
    
    def __init__(self):
        self.llm = OllamaLLM(model=settings.llm_model, temperature=settings.llm_temperature)
        self.map_tool = MapTool()
    
    def generate_plan(self, parsed_input: dict, user_preferences: dict) -> dict:
        """生成活动计划"""
        prompt = PromptTemplate(
            input_variables=["parsed_input", "user_preferences"],
            template="""请根据用户需求和历史偏好，生成详细的活动计划：
            用户需求：{parsed_input}
            历史偏好：{user_preferences}
            
            计划应包括：
            1. 时间安排（具体到小时）
            2. 活动内容
            3. 地点选择
            4. 餐饮推荐
            5. 交通建议
            
            请以JSON格式输出，包含以下字段：
            - plan_id: 唯一标识符
            - title: 计划标题
            - schedule: 时间安排列表，每个元素包含time和description
            - activities: 活动列表，每个元素包含name、time、location、description
            - restaurants: 餐饮推荐列表，每个元素包含name、time、location、cuisine、price_range
            - transportation: 交通建议
            - estimated_cost: 预估费用（字符串格式）"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "parsed_input": json.dumps(parsed_input, ensure_ascii=False),
            "user_preferences": json.dumps(user_preferences, ensure_ascii=False)
        })
        
        try:
            plan = json.loads(result)
            plan = self._enrich_plan_with_route_info(plan)
            return plan
        except json.JSONDecodeError:
            return self._generate_default_plan(parsed_input)
    
    def _enrich_plan_with_route_info(self, plan: dict) -> dict:
        """为计划添加路线信息"""
        if plan.get("activities"):
            for activity in plan["activities"]:
                if activity.get("location"):
                    route_info = self.map_tool.get_route("当前位置", activity["location"])
                    activity["travel_time"] = route_info.get("travel_time", "")
        return plan
    
    def _generate_default_plan(self, parsed_input: dict) -> dict:
        """生成默认计划（当LLM解析失败时）"""
        location = parsed_input.get("地点", "未知地点")
        activity = parsed_input.get("活动", "活动")
        
        return {
            "plan_id": f"plan-{uuid.uuid4().hex[:8]}",
            "title": f"{activity}计划",
            "schedule": [
                {"time": "09:00", "description": "出发"},
                {"time": "10:00", "description": f"到达{location}"},
                {"time": "12:00", "description": "午餐"},
                {"time": "14:00", "description": f"{activity}"},
                {"time": "17:00", "description": "返回"}
            ],
            "activities": [
                {"name": activity, "time": "10:00-16:00", "location": location, "description": f"在{location}进行{activity}"}
            ],
            "restaurants": [
                {"name": "推荐餐厅", "time": "12:00", "location": f"{location}附近", "cuisine": "中餐", "price_range": "适中"}
            ],
            "transportation": "建议自驾或乘坐公共交通",
            "estimated_cost": "300-500元"
        }
    
    def validate_plan(self, plan: dict) -> tuple[bool, str]:
        """验证计划合理性"""
        if not plan.get("plan_id"):
            return False, "计划ID缺失"
        if not plan.get("activities"):
            return False, "活动列表为空"
        return True, "验证通过"