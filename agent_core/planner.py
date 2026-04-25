from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import json
import config

class PlanningAgent:
    def __init__(self, memory_manager, map_tool, weather_tool):
        self.memory_manager = memory_manager
        self.map_tool = map_tool
        self.weather_tool = weather_tool
        self.llm = OllamaLLM(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)
        
    def parse_input(self, user_input):
        """解析用户输入，提取关键实体"""
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""请从以下用户输入中提取关键实体，以JSON格式输出：
            用户输入：{user_input}
            输出格式：{{"地点": "", "活动": "", "餐饮": "", "关系": "", "时间": ""}}"""
        )
        
        # 使用新的方式构建链
        chain = prompt | self.llm
        result = chain.invoke({"user_input": user_input})
        
        try:
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError:
            # 如果解析失败，返回默认值
            return {
                "地点": "",
                "活动": "",
                "餐饮": "",
                "关系": "",
                "时间": ""
            }
    
    def generate_plan(self, parsed_input, user_preferences):
        """生成活动计划"""
        # 构建提示词
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
            - schedule: 时间安排列表
            - activities: 活动列表
            - restaurants: 餐饮推荐
            - transportation: 交通建议
            - estimated_cost: 预估费用"""
        )
        
        # 使用新的方式构建链
        chain = prompt | self.llm
        result = chain.invoke({
            "parsed_input": json.dumps(parsed_input, ensure_ascii=False),
            "user_preferences": json.dumps(user_preferences, ensure_ascii=False)
        })
        
        try:
            plan = json.loads(result)
            # 调用地图工具计算路线
            if plan.get("activities"):
                for activity in plan["activities"]:
                    if activity.get("location"):
                        route_info = self.map_tool.get_route(
                            "当前位置", 
                            activity["location"]
                        )
                        activity["travel_time"] = route_info.get("travel_time", "")
            return plan
        except json.JSONDecodeError:
            raise Exception("计划生成失败，请重试")
    
    def execute_plan(self, plan_id):
        """执行计划，生成行程单"""
        # 模拟执行过程
        itinerary = {
            "itinerary_id": f"ITN-{plan_id}",
            "status": "completed",
            "message": "预订成功",
            "details": {
                "activities": [
                    {
                        "name": "紫金山爬山",
                        "time": "09:30-12:00",
                        "location": "紫金山",
                        "status": "confirmed"
                    }
                ],
                "restaurant": {
                    "name": "推荐餐厅",
                    "time": "12:30",
                    "location": "紫金山附近",
                    "status": "booked"
                }
            }
        }
        return itinerary