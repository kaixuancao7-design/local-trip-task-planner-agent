"""决策层 - 规划Agent

负责基于用户需求和历史偏好，生成完整的活动方案。
"""
from langchain_core.prompts import PromptTemplate
import json
import uuid
from config.settings import settings
from tools.map_tool import MapTool
from config.logging_config import log_performance, logger

class PlanningAgent:
    """规划Agent"""
    
    def __init__(self):
        self._llm = None
        self.map_tool = MapTool()
        self._plans = {}  # 存储生成的计划
    
    @property
    def llm(self):
        """懒加载LLM模型"""
        if self._llm is None:
            from langchain_ollama import OllamaLLM
            self._llm = OllamaLLM(model=settings.llm_model, temperature=settings.llm_temperature)
        return self._llm
    
    @log_performance("planning.generate_plan")
    def generate_plan(self, parsed_input: dict, user_preferences: dict) -> dict:
        """生成活动计划"""
        logger.info(f"[PlanningAgent] 开始生成计划 - 输入: {parsed_input}, 偏好: {user_preferences}")
        
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
        
        logger.debug("[PlanningAgent] 调用LLM生成计划...")
        chain = prompt | self.llm
        result = chain.invoke({
            "parsed_input": json.dumps(parsed_input, ensure_ascii=False),
            "user_preferences": json.dumps(user_preferences, ensure_ascii=False)
        })
        logger.debug(f"[PlanningAgent] LLM返回结果: {result[:200]}...")
        
        try:
            plan = json.loads(result)
            plan = self._enrich_plan_with_route_info(plan)
            self.save_plan(plan)
            logger.info(f"[PlanningAgent] 计划生成成功 - plan_id: {plan.get('plan_id')}, 标题: {plan.get('title')}")
            return plan
        except json.JSONDecodeError as e:
            logger.warning(f"[PlanningAgent] LLM返回结果解析失败，使用默认计划 - 错误: {e}")
            plan = self._generate_default_plan(parsed_input)
            self.save_plan(plan)
            logger.info(f"[PlanningAgent] 默认计划生成成功 - plan_id: {plan.get('plan_id')}")
            return plan
    
    def _enrich_plan_with_route_info(self, plan: dict) -> dict:
        """为计划添加路线信息"""
        logger.debug("[PlanningAgent] 开始为计划添加路线信息")
        if plan.get("activities"):
            for i, activity in enumerate(plan["activities"]):
                if activity.get("location"):
                    logger.debug(f"[PlanningAgent] 查询路线 - 活动{i+1}: {activity['name']} -> {activity['location']}")
                    route_info = self.map_tool.get_route("当前位置", activity["location"])
                    activity["travel_time"] = route_info.get("travel_time", "")
                    logger.debug(f"[PlanningAgent] 路线信息 - 交通时间: {activity['travel_time']}")
        logger.debug("[PlanningAgent] 路线信息添加完成")
        return plan
    
    def _generate_default_plan(self, parsed_input: dict) -> dict:
        """生成默认计划（当LLM解析失败时）"""
        logger.info("[PlanningAgent] 生成默认计划")
        location = parsed_input.get("地点", "未知地点")
        activity = parsed_input.get("活动", "活动")
        logger.debug(f"[PlanningAgent] 默认计划参数 - 地点: {location}, 活动: {activity}")
        
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
    
    def save_plan(self, plan: dict) -> bool:
        """保存计划"""
        if plan.get("plan_id"):
            self._plans[plan["plan_id"]] = plan
            logger.info(f"[PlanningAgent] 计划已保存 - plan_id: {plan['plan_id']}, 当前缓存计划数: {len(self._plans)}")
            return True
        logger.warning("[PlanningAgent] 保存计划失败 - plan_id为空")
        return False
    
    def get_plan(self, plan_id: str) -> dict:
        """根据计划ID获取计划"""
        plan = self._plans.get(plan_id)
        if plan:
            logger.info(f"[PlanningAgent] 获取计划成功 - plan_id: {plan_id}")
        else:
            logger.warning(f"[PlanningAgent] 获取计划失败 - plan_id: {plan_id} 不存在")
        return plan or {}