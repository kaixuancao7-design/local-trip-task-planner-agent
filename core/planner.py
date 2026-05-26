"""决策层 - 规划Agent

基于LLM的智能规划Agent，支持：
- LLM驱动的需求解析和场景识别
- ReAct工具调用闭环
- 多方案择优和反思机制
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Optional
from config.settings import settings
from tools.map_tool import MapTool
from tools.activity_search_tool import ActivitySearchTool
from tools.restaurant_search_tool import RestaurantSearchTool
from tools.queue_check_tool import QueueCheckTool
from config.logging_config import log_performance, logger

class PlanningAgent:
    """LLM驱动的规划Agent"""
    
    def __init__(self):
        self._llm = None
        self.map_tool = MapTool()
        self.activity_tool = ActivitySearchTool()
        self.restaurant_tool = RestaurantSearchTool()
        self.queue_tool = QueueCheckTool()
        self._plans = {}
        self._conversation_history = {}
        
        # 场景类型映射
        self.scene_mapping = {
            "family": "亲子",
            "friends": "好友聚会", 
            "couple": "情侣约会",
            "solo": "个人休闲",
            "sports": "运动健身",
            "study": "研学教育",
            "explore": "探店打卡",
            "team": "团建活动"
        }
        
        # 评分权重
        self.score_weights = {
            "distance": 0.4,
            "experience": 0.35,
            "rhythm": 0.25
        }
        
        # LLM需求解析Prompt
        self._requirement_parsing_prompt = PromptTemplate(
            input_variables=["user_input", "user_preferences"],
            template="""你是一个专业的活动规划助手，能够从用户的自然语言输入中提取结构化的规划需求。

用户输入：{user_input}

用户历史偏好：{user_preferences}

请分析用户输入，提取以下信息并以JSON格式输出：

1. scene_type: 场景类型（family/friends/couple/solo/sports/study/explore/team）
2. scene_name: 场景名称（中文）
3. people_count: 参与人数（数字）
4. age_groups: 年龄群体列表（child/adult/elder的组合）
5. relationships: 关系类型列表（如：family, friends, couple, colleagues）
6. time_range: 时间范围（上午/下午/晚上/全天/具体时间）
7. duration_hours: 预计时长（小时，数字）
8. distance_limit: 可接受的最大距离（公里，数字）
9. budget_min: 最低预算（元，数字）
10. budget_max: 最高预算（元，数字）
11. cuisine_preference: 餐饮偏好（如：川菜、火锅、健康餐、亲子友好等）
12. activity_preferences: 活动偏好列表（如：户外、安静、文化、刺激等）
13. special_requirements: 特殊需求列表（如：无障碍设施、儿童座椅、安静环境等）

注意：
- 如果用户没有明确提到某些信息，使用你的常识推断
- duration_hours默认为4（半天）
- distance_limit默认为3公里
- age_groups：如果有儿童则包含child，有老人则包含elder，其余为adult
- 输出必须是有效的JSON格式，不要包含任何其他文字"""
        )
        
        # LLM行程规划Prompt
        self._planning_prompt = PromptTemplate(
            input_variables=["scene_info", "constraints", "activities", "restaurants", 
                           "user_preferences", "observation"],
            template="""你是一个专业的行程规划师，基于以下信息设计最优的周末活动行程。

场景信息：
{scene_info}

约束条件：
{constraints}

可用活动场地：
{activities}

可用餐厅：
{restaurants}

用户偏好：
{user_preferences}

观察结果（工具执行汇总）：
{observation}

请设计一个完整的行程规划，要求：

1. 行程结构灵活，不强制固定段数，根据场景和时长自由安排
2. 考虑活动之间的通勤时间和距离
3. 合理分配时间，避免赶场或空闲
4. 选择评分高、排队时间短的场地
5. 餐饮选择要匹配人群需求（如亲子选儿童友好餐厅）
6. 参考观察结果中的天气和排队信息进行优化

请以JSON格式输出行程规划：

{{
    "title": "行程标题",
    "structure": "行程结构描述",
    "steps": [
        {{
            "step_id": "步骤编号",
            "type": "activity/restaurant/transport",
            "name": "名称",
            "venue_id": "场地ID（如有）",
            "start_time": "开始时间（HH:MM）",
            "end_time": "结束时间（HH:MM）",
            "location": "经纬度",
            "address": "地址",
            "duration_minutes": "持续分钟数",
            "notes": "备注说明"
        }}
    ],
    "total_duration": "总时长（分钟）",
    "total_distance": "总通勤距离（米）",
    "cost_estimate": "费用估算",
    "reasoning": "规划思路说明"
}}

重要：
- 时间安排要合理，确保各环节有足够时间
- 通勤时间要计算在内
- 输出必须是有效的JSON格式"""
        )
        
        # LLM反思Prompt
        self._reflection_prompt = PromptTemplate(
            input_variables=["plan", "constraints"],
            template="""请审查以下行程规划，检查可能存在的问题：

行程规划：
{plan}

约束条件：
{constraints}

请检查以下方面：
1. 时长是否合理？是否有赶场风险？
2. 通勤距离是否过远？是否有更近的替代方案？
3. 餐厅选择是否匹配餐饮偏好？
4. 是否有场地可能满员或休息？
5. 行程结构是否适合场景（亲子需要休闲节奏，团建可以紧凑）？

请以JSON格式输出审查结果：

{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "improved_plan": 改进后的行程规划（如有问题）
}}

如果没有问题，improved_plan可以使用原计划。"""
        )
    
    @property
    def llm(self):
        """懒加载LLM模型"""
        if self._llm is None:
            from langchain_ollama import OllamaLLM
            self._llm = OllamaLLM(model=settings.llm_model, temperature=settings.llm_temperature)
        return self._llm
    
    def _parse_scene_constraints_llm(self, user_input: str, user_preferences: dict = None, 
                                    scene_type: str = None) -> dict:
        """使用LLM进行结构化需求解析
        
        Args:
            user_input: 用户自然语言输入
            user_preferences: 用户偏好
            scene_type: 指定的场景类型（可选）
            
        Returns:
            包含场景信息和约束条件的字典
        """
        logger.info(f"[PlanningAgent] 使用LLM解析需求 - 输入: {user_input[:50]}...")
        
        user_preferences = user_preferences or {}
        
        # 如果指定了场景类型，在Prompt中加入约束
        scene_constraint = ""
        if scene_type:
            scene_name = self.scene_mapping.get(scene_type, scene_type)
            scene_constraint = f"\n注意：用户明确指定了场景类型为【{scene_name}】，请据此识别。\n"
        
        try:
            chain = self._requirement_parsing_prompt | self.llm
            
            enhanced_input = user_input + scene_constraint
            
            result = chain.invoke({
                "user_input": enhanced_input,
                "user_preferences": json.dumps(user_preferences, ensure_ascii=False)
            })
            
            logger.debug(f"[PlanningAgent] LLM需求解析结果: {result[:200]}...")
            
            parsed = json.loads(result)
            
            # 如果用户指定了场景类型，优先使用指定的场景
            if scene_type:
                scene_type = parsed.get("scene_type", scene_type)
                scene_name = parsed.get("scene_name", self.scene_mapping.get(scene_type, scene_type))
            else:
                scene_type = parsed.get("scene_type", "solo")
                scene_name = parsed.get("scene_name", "个人休闲")
            
            scene_info = {
                "scene_type": scene_type,
                "scene_name": scene_name,
                "people_count": parsed.get("people_count", 1),
                "age_groups": parsed.get("age_groups", ["adult"]),
                "relationships": parsed.get("relationships", []),
                "activity_preferences": parsed.get("activity_preferences", []),
                "special_requirements": parsed.get("special_requirements", [])
            }
            
            constraints = {
                "time_range": parsed.get("time_range", "下午"),
                "duration_hours": float(parsed.get("duration_hours", 4.0)),
                "distance_limit": float(parsed.get("distance_limit", 3.0)),
                "budget_min": float(parsed.get("budget_min", 0)),
                "budget_max": float(parsed.get("budget_max", 1000)),
                "cuisine_preference": parsed.get("cuisine_preference", ""),
                "max_waiting_time": settings.max_waiting_time
            }
            
            logger.info(f"[PlanningAgent] LLM解析成功 - 场景: {scene_info['scene_name']}, 人数: {scene_info['people_count']}")
            
            return {
                "scene_info": scene_info,
                "constraints": constraints,
                "parsing_method": "llm"
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"[PlanningAgent] LLM解析失败: {e}，使用规则解析")
            return self._parse_scene_constraints_rules(user_input, user_preferences, scene_type)
        except Exception as e:
            logger.error(f"[PlanningAgent] LLM解析异常: {e}，使用规则解析")
            return self._parse_scene_constraints_rules(user_input, user_preferences, scene_type)
    
    def _parse_scene_constraints_rules(self, user_input: str, user_preferences: dict = None) -> dict:
        """基于规则的需求解析（降级方案）"""
        logger.info(f"[PlanningAgent] 使用规则解析需求 - 输入: {user_input}")
        
        scene_info = self._identify_scene_rules(user_input)
        constraints = self._extract_constraints_rules(user_input, scene_info)
        
        return {
            "scene_info": scene_info,
            "constraints": constraints,
            "parsing_method": "rules"
        }
    
    def _parse_scene_constraints(self, user_input: str, user_preferences: dict = None) -> dict:
        """解析场景约束条件（主入口）
        
        优先使用LLM解析，失败时降级到规则解析
        """
        return self._parse_scene_constraints_llm(user_input, user_preferences)
    
    def _identify_scene_rules(self, user_input: str, scene_type: str = None) -> dict:
        """识别场景类型（规则版本，降级方案）"""
        if scene_type:
            scene_name = self.scene_mapping.get(scene_type, scene_type)
            return {
                "scene_type": scene_type,
                "scene_name": scene_name,
                "people_count": self._extract_people_count(user_input),
                "age_groups": [self._extract_age_group(user_input, scene_type)],
                "relationships": [],
                "activity_preferences": [],
                "special_requirements": []
            }
        
        input_lower = user_input.lower()
        
        if any(keyword in input_lower for keyword in ["女朋友", "男友", "对象", "情侣", "约会"]):
            return {
                "scene_type": "couple",
                "scene_name": "情侣约会",
                "people_count": 2,
                "age_groups": ["adult"],
                "relationships": ["couple"],
                "activity_preferences": [],
                "special_requirements": []
            }
        elif any(keyword in input_lower for keyword in ["亲子", "孩子", "儿童", "宝宝", "带娃", "小孩"]):
            return {
                "scene_type": "family",
                "scene_name": "亲子",
                "people_count": self._extract_people_count(user_input) or 2,
                "age_groups": ["child", "adult"],
                "relationships": ["family"],
                "activity_preferences": [],
                "special_requirements": ["儿童设施"]
            }
        elif any(keyword in input_lower for keyword in ["朋友", "聚会", "团建", "闺蜜", "哥们", "同学"]):
            return {
                "scene_type": "friends",
                "scene_name": "好友聚会",
                "people_count": self._extract_people_count(user_input) or 4,
                "age_groups": ["adult"],
                "relationships": ["friends"],
                "activity_preferences": [],
                "special_requirements": []
            }
        else:
            return {
                "scene_type": "solo",
                "scene_name": "个人休闲",
                "people_count": 1,
                "age_groups": ["adult"],
                "relationships": [],
                "activity_preferences": [],
                "special_requirements": []
            }
    
    def _identify_scene(self, user_input: str, scene_type: str = None) -> dict:
        """识别场景类型（兼容接口）"""
        return self._identify_scene_rules(user_input, scene_type)
    
    def _extract_people_count(self, user_input: str) -> int:
        """从输入中提取人数"""
        import re
        # 优先匹配明确的人数描述
        patterns = [r'(\d+)人', r'(\d+)个', r'(\d+)位', r'(\d+)名', r'(\d+)个朋友', r'(\d+)位朋友']
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return int(match.group(1))
        
        # 如果没有明确人数，从年龄描述中推断（通常亲子场景会说"带X岁孩子"）
        age_pattern = r'(\d+)岁'
        age_match = re.search(age_pattern, user_input)
        if age_match:
            # 带孩子通常意味着至少2人（大人+孩子）
            return 2
        
        return 0
    
    def _extract_age_group(self, user_input: str, scene_type: str) -> str:
        """提取年龄组"""
        input_lower = user_input.lower()
        if any(keyword in input_lower for keyword in ["儿童", "小孩", "宝宝", "幼儿园", "小学"]):
            return "child"
        elif any(keyword in input_lower for keyword in ["老人", "长辈", "父母"]):
            return "elder"
        elif scene_type == "family":
            return "child"
        return "adult"
    
    def _extract_constraints(self, user_input: str, scene_info: dict) -> dict:
        """提取约束条件"""
        input_lower = user_input.lower()
        
        # 时间约束
        time_range = "周末下午"
        duration_hours = 4.0
        
        if "上午" in input_lower:
            time_range = "上午"
        elif "下午" in input_lower:
            time_range = "下午"
        elif "晚上" in input_lower:
            time_range = "晚上"
        
        # 时长提取
        import re
        duration_match = re.search(r'(\d+)小时', input_lower)
        if duration_match:
            duration_hours = float(duration_match.group(1))
        elif "半天" in input_lower:
            duration_hours = 4.0
        
        # 距离约束
        distance_limit = settings.default_distance_limit
        distance_match = re.search(r'(\d+)公里', input_lower)
        if distance_match:
            distance_limit = float(distance_match.group(1))
        
        # 预算约束
        budget_min, budget_max = 0, 1000
        budget_match = re.search(r'(\d+)-(\d+)元', input_lower)
        if budget_match:
            budget_min, budget_max = float(budget_match.group(1)), float(budget_match.group(2))
        
        # 餐饮偏好
        cuisine_preference = self._extract_cuisine_preference(input_lower, scene_info)
        
        return {
            "time_range": time_range,
            "duration_hours": duration_hours,
            "distance_limit": distance_limit,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "cuisine_preference": cuisine_preference,
            "max_waiting_time": settings.max_waiting_time
        }
    
    def _extract_cuisine_preference(self, input_lower: str, scene_info: dict) -> str:
        """提取餐饮偏好"""
        # 场景默认偏好
        if scene_info["scene_type"] == "family":
            return "亲子友好"
        elif scene_info["scene_type"] == "couple":
            return "浪漫氛围"
        
        # 明确偏好
        preferences = {
            "减肥": "减肥餐",
            "健康": "健康餐", 
            "素食": "素食",
            "火锅": "火锅",
            "川菜": "川菜",
            "西餐": "西餐",
            "日料": "日料"
        }
        
        for keyword, preference in preferences.items():
            if keyword in input_lower:
                return preference
        
        return ""
    
    @log_performance("planning.generate_scene_plan")
    def generate_scene_plan(self, user_input: str, user_preferences: dict = None, 
                           scene_type: str = None, user_location: str = "") -> dict:
        """生成场景化活动计划（主入口）
        
        轻量Plan-and-Execute + 单轮ReAct + 后置反思模式：
        1. 需求解析 → 2. 工具决策 → 3. 批量执行 → 4. 观察汇总 → 5. 生成规划 → 6. 反思检查
        """
        logger.info(f"[Plan-Execute] 开始生成场景化计划 - 输入: {user_input[:50]}...")
        
        user_preferences = user_preferences or {}
        
        try:
            # ========== Step 1: 需求解析 (LLM) ==========
            logger.info("[Plan-Execute] Step 1/6: 需求解析...")
            analysis = self._parse_scene_constraints_llm(user_input, user_preferences, scene_type)
            scene_info = analysis["scene_info"]
            constraints = analysis["constraints"]
            parsing_method = analysis.get("parsing_method", "llm")
            
            logger.info(f"[Plan-Execute] 需求解析完成 - 场景: {scene_info['scene_name']}, 人数: {scene_info['people_count']}")
            
            # ========== Step 2: 工具决策 (LLM) ==========
            logger.info("[Plan-Execute] Step 2/6: 工具决策...")
            tool_calls = self._decide_tool_calls(scene_info, constraints)
            logger.info(f"[Plan-Execute] 工具决策完成 - 计划调用: {tool_calls}")
            
            # ========== Step 3: 批量执行 (工具调用) ==========
            logger.info("[Plan-Execute] Step 3/6: 批量执行工具调用...")
            tool_results = self._execute_tool_calls(tool_calls, scene_info, constraints, 
                                                  user_location, activities=None)
            
            # 提取工具结果
            activities = tool_results.get("activities", [])
            restaurants = tool_results.get("restaurants", [])
            queue_info = tool_results.get("queue_info", {})
            weather_info = tool_results.get("weather_info", {})
            route_info = tool_results.get("route_info", {})
            
            logger.info(f"[Plan-Execute] 工具执行完成 - 活动:{len(activities)}, 餐厅:{len(restaurants)}")
            
            # 兜底数据
            if not activities:
                activities = self._get_fallback_activities(scene_info, constraints)
            if not restaurants:
                restaurants = self._get_fallback_restaurants(scene_info, constraints)
            
            # ========== Step 4: 观察汇总 ==========
            logger.info("[Plan-Execute] Step 4/6: 观察汇总...")
            observation = self._summarize_observations(activities, restaurants, 
                                                     queue_info, weather_info, route_info)
            
            # ========== Step 5: 生成规划 (LLM) ==========
            logger.info("[Plan-Execute] Step 5/6: 生成行程规划...")
            plan = self._generate_plan_with_llm(scene_info, constraints, activities, 
                                               restaurants, user_preferences, observation)
            
            if not plan:
                logger.warning("[Plan-Execute] LLM规划失败，降级到规则规划")
                plan = self._generate_plan_with_rules(scene_info, constraints, 
                                                     activities, restaurants)
            
            # ========== Step 6: 反思检查 (LLM) ==========
            logger.info("[Plan-Execute] Step 6/6: 反思检查...")
            reflection = self._reflect_on_plan(plan, constraints)
            
            if not reflection.get("is_valid", True):
                logger.info("[Plan-Execute] 方案需要改进...")
                improved_plan = reflection.get("improved_plan")
                if improved_plan:
                    plan = improved_plan
            
            # 添加元数据
            plan["plan_id"] = f"plan-{uuid.uuid4().hex[:8]}"
            plan["scene_info"] = scene_info
            plan["parsing_method"] = parsing_method
            plan["planning_method"] = plan.get("planning_method", "unknown")
            
            self.save_plan(plan)
            
            return {
                "success": True,
                "plan": plan,
                "scene_info": scene_info,
                "constraints": constraints,
                "parsing_method": parsing_method,
                "reflection": reflection,
                "tool_calls": tool_calls,
                "observation": observation
            }
            
        except Exception as e:
            logger.error(f"[Plan-Execute] 生成场景化计划失败: {e}")
            return self._generate_fallback_plan(user_input)
    
    def _execute_tool_calls(self, tool_calls: list, scene_info: dict, constraints: dict,
                           user_location: str, activities: list = None) -> dict:
        """批量执行工具调用"""
        results = {
            "activities": [],
            "restaurants": [],
            "queue_info": {},
            "weather_info": {},
            "route_info": {}
        }
        
        for tool_name in tool_calls:
            logger.debug(f"[Tool Execution] 执行工具: {tool_name}")
            
            try:
                if tool_name == "search_activities":
                    results["activities"] = self._search_activities(
                        scene_info, constraints, user_location
                    )
                
                elif tool_name == "search_restaurants":
                    results["restaurants"] = self._search_restaurants(
                        scene_info, constraints, user_location
                    )
                
                elif tool_name == "check_queue":
                    acts = results["activities"] if results["activities"] else (activities or [])
                    venue_ids = [act.get("id") for act in acts if act.get("id")]
                    if venue_ids:
                        results["queue_info"] = self._check_multiple_queues(venue_ids)
                
                elif tool_name == "get_route":
                    acts = results["activities"] if results["activities"] else (activities or [])
                    if acts and user_location and acts[0].get("location"):
                        results["route_info"] = self.map_tool.get_route(
                            user_location, acts[0].get("location")
                        )
                
                elif tool_name == "get_weather":
                    from tools.weather_tool import WeatherTool
                    weather_tool = WeatherTool()
                    results["weather_info"] = weather_tool.get_weather("南京")
            
            except Exception as e:
                logger.warning(f"[Tool Execution] 工具 {tool_name} 执行失败: {e}")
        
        return results
    
    def _summarize_observations(self, activities: list, restaurants: list,
                               queue_info: dict, weather_info: dict, route_info: dict) -> dict:
        """汇总工具执行结果作为观察"""
        return {
            "activity_count": len(activities),
            "restaurant_count": len(restaurants),
            "queues_checked": len(queue_info),
            "has_weather": bool(weather_info),
            "has_route": bool(route_info),
            "top_activities": activities[:3],
            "top_restaurants": restaurants[:3]
        }
    
    def _decide_tool_calls(self, scene_info: dict, constraints: dict) -> List[str]:
        """LLM思考：决定需要调用哪些工具
        
        基于场景信息和约束条件，让LLM自主决定调用哪些工具
        """
        logger.info("[LLM Tool Decision] 让LLM决定工具调用...")
        
        available_tools = [
            {"name": "search_activities", "description": "搜索本地活动场地（亲子乐园、展览馆、公园等）"},
            {"name": "search_restaurants", "description": "搜索餐厅（支持减肥餐、亲子友好、火锅等）"},
            {"name": "check_queue", "description": "查询场地/餐厅排队人数和剩余空位"},
            {"name": "get_route", "description": "获取两地之间的路线和通勤时间"},
            {"name": "get_weather", "description": "查询天气情况"}
        ]
        
        prompt = PromptTemplate(
            input_variables=["scene_info", "constraints", "available_tools"],
            template="""你是一个智能规划助手，需要根据用户需求决定调用哪些工具。

场景信息：{scene_info}

约束条件：{constraints}

可用工具列表：
{available_tools}

请分析需求，决定需要调用哪些工具，并以JSON格式输出：

{{
    "thought": "你的思考过程：为什么需要这些工具",
    "tool_calls": ["工具名称1", "工具名称2", ...]
}}

注意：
- 工具名称必须从可用工具列表中选择
- 如果不需要调用任何工具，tool_calls为空数组
- 输出必须是有效的JSON格式"""
        )
        
        try:
            chain = prompt | self.llm
            
            result = chain.invoke({
                "scene_info": json.dumps(scene_info, ensure_ascii=False),
                "constraints": json.dumps(constraints, ensure_ascii=False),
                "available_tools": json.dumps(available_tools, ensure_ascii=False)
            })
            
            logger.debug(f"[LLM Tool Decision] LLM输出: {result[:200]}...")
            
            parsed = json.loads(result)
            tool_calls = parsed.get("tool_calls", [])
            thought = parsed.get("thought", "")
            
            logger.info(f"[LLM Tool Decision] LLM决定调用工具: {tool_calls}")
            if thought:
                logger.info(f"[LLM Tool Decision] 思考过程: {thought}")
            
            return tool_calls
            
        except json.JSONDecodeError as e:
            logger.warning(f"[LLM Tool Decision] JSON解析失败: {e}，使用默认工具")
            return self._get_default_tool_calls(scene_info)
        except Exception as e:
            logger.error(f"[LLM Tool Decision] LLM决策失败: {e}，使用默认工具")
            return self._get_default_tool_calls(scene_info)
    
    def _get_default_tool_calls(self, scene_info: dict) -> List[str]:
        """获取默认工具调用列表（降级方案）"""
        scene_type = scene_info.get("scene_type", "solo")
        tool_calls = ["search_activities", "search_restaurants"]
        
        if scene_type == "family" or "child" in scene_info.get("age_groups", []):
            tool_calls.append("check_queue")
        
        return tool_calls
    
    def _check_multiple_queues(self, venue_ids: list) -> dict:
        """批量检查多个场地的排队情况"""
        logger.info(f"[Queue Check] 批量检查排队情况 - 场地数量: {len(venue_ids)}")
        
        try:
            results = {}
            for venue_id in venue_ids[:5]:  # 最多检查5个
                queue_status = self.queue_tool.check_queue(venue_id)
                if queue_status:
                    results[venue_id] = queue_status
            return results
        except Exception as e:
            logger.warning(f"[Queue Check] 批量检查失败: {e}")
            return {}
    
    def _generate_plan_with_llm(self, scene_info: dict, constraints: dict,
                                activities: list, restaurants: list, 
                                user_preferences: dict, observation: dict = None) -> Optional[dict]:
        """使用LLM生成行程规划"""
        logger.info("[LLM Planning] 开始LLM驱动规划...")
        
        try:
            chain = self._planning_prompt | self.llm
            
            scene_info_str = json.dumps(scene_info, ensure_ascii=False)
            constraints_str = json.dumps(constraints, ensure_ascii=False)
            observation_str = json.dumps(observation or {}, ensure_ascii=False)
            activities_str = json.dumps(activities[:10], ensure_ascii=False)  # 限制数量
            restaurants_str = json.dumps(restaurants[:10], ensure_ascii=False)
            preferences_str = json.dumps(user_preferences, ensure_ascii=False)
            
            result = chain.invoke({
                "scene_info": scene_info_str,
                "constraints": constraints_str,
                "activities": activities_str,
                "restaurants": restaurants_str,
                "user_preferences": preferences_str,
                "observation": observation_str
            })
            
            logger.debug(f"[LLM Planning] LLM输出: {result[:200]}...")
            
            plan = json.loads(result)
            plan["planning_method"] = "llm"
            
            logger.info("[LLM Planning] LLM规划成功")
            return plan
            
        except json.JSONDecodeError as e:
            logger.warning(f"[LLM Planning] JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"[LLM Planning] LLM规划失败: {e}")
            return None
    
    def _reflect_on_plan(self, plan: dict, constraints: dict) -> dict:
        """LLM反思：检查方案质量"""
        logger.info("[Reflection] 开始方案反思...")
        
        try:
            chain = self._reflection_prompt | self.llm
            
            plan_str = json.dumps(plan, ensure_ascii=False)
            constraints_str = json.dumps(constraints, ensure_ascii=False)
            
            result = chain.invoke({
                "plan": plan_str,
                "constraints": constraints_str
            })
            
            reflection = json.loads(result)
            logger.info(f"[Reflection] 反思完成 - 有效: {reflection.get('is_valid')}")
            
            return reflection
            
        except Exception as e:
            logger.warning(f"[Reflection] 反思失败: {e}")
            return {"is_valid": True, "issues": [], "suggestions": []}
    
    def _search_activities(self, scene_info: dict, constraints: dict, user_location: str) -> list:
        """搜索活动场地"""
        try:
            activities = self.activity_tool.search_activities(
                scene_type=scene_info["scene_name"],
                city="南京",
                radius=constraints["distance_limit"],
                limit=10,
                user_location=user_location,
                sort_by="time"
            )
            # 过滤排队时间过长的场地
            max_wait = constraints.get("max_waiting_time", 20)
            return [a for a in activities if int(a.get("waiting_time", 0)) <= max_wait]
        except Exception as e:
            logger.warning(f"搜索活动失败: {e}")
            return []
    
    def _search_restaurants(self, scene_info: dict, constraints: dict, user_location: str) -> list:
        """搜索餐厅"""
        try:
            requirement = constraints.get("cuisine_preference", "")
            if not requirement:
                requirement = self._get_default_cuisine_requirement(scene_info["scene_type"])
            
            restaurants = self.restaurant_tool.search_restaurants(
                requirement=requirement,
                city="南京",
                radius=constraints["distance_limit"],
                limit=10
            )
            return restaurants
        except Exception as e:
            logger.warning(f"搜索餐厅失败: {e}")
            return []
    
    def _get_default_cuisine_requirement(self, scene_type: str) -> str:
        """获取场景默认餐饮需求"""
        defaults = {
            "family": "亲子友好",
            "friends": "多人团建",
            "couple": "情侣约会",
            "solo": "个人休闲"
        }
        return defaults.get(scene_type, "个人休闲")
    
    def _get_fallback_activities(self, scene_info: dict, constraints: dict) -> list:
        """获取兜底活动列表"""
        fallback_data = {
            "family": [
                {"name": "城市公园", "location": "118.783799,32.060255", "address": "市中心公园", 
                 "type": "公园", "rating": 4.5, "waiting_time": 0, "distance": 500}
            ],
            "friends": [
                {"name": "艺术展览馆", "location": "118.778934,32.058976", "address": "艺术区", 
                 "type": "展览馆", "rating": 4.8, "waiting_time": 10, "distance": 800}
            ],
            "couple": [
                {"name": "浪漫咖啡馆", "location": "118.782345,32.059876", "address": "情侣巷", 
                 "type": "咖啡馆", "rating": 4.7, "waiting_time": 5, "distance": 300}
            ],
            "solo": [
                {"name": "市图书馆", "location": "118.787654,32.061234", "address": "文化中心", 
                 "type": "图书馆", "rating": 4.5, "waiting_time": 0, "distance": 600}
            ]
        }
        return fallback_data.get(scene_info["scene_type"], fallback_data["solo"])
    
    def _get_fallback_restaurants(self, scene_info: dict, constraints: dict) -> list:
        """获取兜底餐厅列表"""
        fallback_data = {
            "family": [
                {"name": "亲子餐厅", "location": "118.785678,32.056789", "address": "亲子乐园旁", 
                 "type": "亲子友好", "rating": 4.6, "price_range": "60-100元", "distance": 600}
            ],
            "friends": [
                {"name": "特色火锅店", "location": "118.798765,32.045678", "address": "美食街", 
                 "type": "火锅", "rating": 4.7, "price_range": "80-150元", "distance": 900}
            ],
            "couple": [
                {"name": "法式餐厅", "location": "118.772345,32.053456", "address": "浪漫街区", 
                 "type": "西餐", "rating": 4.9, "price_range": "100-200元", "distance": 700}
            ],
            "solo": [
                {"name": "简餐店", "location": "118.792345,32.058765", "address": "商业街", 
                 "type": "简餐", "rating": 4.4, "price_range": "30-60元", "distance": 500}
            ]
        }
        return fallback_data.get(scene_info["scene_type"], fallback_data["solo"])
    
    def _generate_candidate_plans(self, scene_info: dict, constraints: dict,
                                  activities: list, restaurants: list, user_location: str) -> list:
        """生成多个候选方案"""
        candidates = []
        
        # 生成3个候选方案
        for i in range(min(3, len(activities))):
            activity = activities[i % len(activities)]
            restaurant = restaurants[i % len(restaurants)]
            
            plan = self._build_three_segment_plan(
                scene_info, constraints, activity, restaurant, user_location, i + 1
            )
            candidates.append(plan)
        
        return candidates
    
    def _build_three_segment_plan(self, scene_info: dict, constraints: dict,
                                  activity: dict, restaurant: dict, user_location: str,
                                  plan_index: int) -> dict:
        """构建三段式行程计划
        
        结构：游玩(2-2.5h) → 就餐(1.5h) → 轻休闲(1h)
        """
        base_time = self._get_base_time(constraints["time_range"])
        duration_minutes = int(constraints["duration_hours"] * 60)
        
        # 分配时间
        play_duration = min(int(duration_minutes * 0.5), 150)  # 最多2.5小时
        meal_duration = min(int(duration_minutes * 0.3), 90)   # 最多1.5小时
        relax_duration = duration_minutes - play_duration - meal_duration
        
        # 构建时间线
        current_time = base_time
        
        # 游玩阶段
        play_start = current_time
        current_time += timedelta(minutes=play_duration)
        play_end = current_time
        
        # 就餐阶段
        meal_start = current_time
        current_time += timedelta(minutes=meal_duration)
        meal_end = current_time
        
        # 轻休闲阶段
        relax_start = current_time
        current_time += timedelta(minutes=relax_duration)
        relax_end = current_time
        
        # 计算距离分数
        total_distance = activity.get("commute_distance", 0) + restaurant.get("distance", 0)
        distance_score = max(0, 100 - (total_distance / 100)) / 100
        
        # 体验分数（基于评分和排队时间）
        activity_rating = float(activity.get("rating", 0)) if activity.get("rating") else 0
        restaurant_rating = float(restaurant.get("rating", 0)) if restaurant.get("rating") else 0
        avg_rating = (activity_rating + restaurant_rating) / 8  # 归一化到0-1
        waiting_time = activity.get("waiting_time", 0) + restaurant.get("waiting_time", 0)
        wait_score = max(0, 1 - waiting_time / 60)  # 超过60分钟得0分
        experience_score = (avg_rating + wait_score) / 2
        
        # 节奏分数
        ideal_duration = 240  # 4小时基准
        rhythm_score = max(0, 1 - abs(duration_minutes - ideal_duration) / 120)
        
        # 综合评分
        total_score = (
            distance_score * self.score_weights["distance"] +
            experience_score * self.score_weights["experience"] +
            rhythm_score * self.score_weights["rhythm"]
        )
        
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        
        return {
            "plan_id": plan_id,
            "title": f"{scene_info['scene_name']}周末计划方案{plan_index}",
            "scene_info": scene_info,
            "score": round(total_score, 4),
            "score_details": {
                "distance": round(distance_score * self.score_weights["distance"], 4),
                "experience": round(experience_score * self.score_weights["experience"], 4),
                "rhythm": round(rhythm_score * self.score_weights["rhythm"], 4)
            },
            "duration": duration_minutes,
            "total_distance": total_distance,
            "cost_estimate": self._estimate_cost(scene_info, activity, restaurant),
            "steps": [
                {
                    "step_id": f"{plan_id}-play",
                    "type": "activity",
                    "name": activity["name"],
                    "venue_id": activity.get("id", ""),
                    "start_time": play_start.strftime("%H:%M"),
                    "end_time": play_end.strftime("%H:%M"),
                    "location": activity.get("location", ""),
                    "address": activity.get("address", ""),
                    "duration": play_duration,
                    "status": "pending",
                    "rating": activity.get("rating", ""),
                    "price_range": activity.get("cost", "")
                },
                {
                    "step_id": f"{plan_id}-meal",
                    "type": "restaurant",
                    "name": restaurant["name"],
                    "venue_id": restaurant.get("id", ""),
                    "start_time": meal_start.strftime("%H:%M"),
                    "end_time": meal_end.strftime("%H:%M"),
                    "location": restaurant.get("location", ""),
                    "address": restaurant.get("address", ""),
                    "duration": meal_duration,
                    "status": "pending",
                    "rating": restaurant.get("rating", ""),
                    "price_range": restaurant.get("cost", restaurant.get("price_range", ""))
                },
                {
                    "step_id": f"{plan_id}-relax",
                    "type": "relax",
                    "name": f"{self._get_relax_activity(scene_info)}",
                    "start_time": relax_start.strftime("%H:%M"),
                    "end_time": relax_end.strftime("%H:%M"),
                    "duration": relax_duration,
                    "status": "pending"
                }
            ],
            "schedule": self._build_schedule([play_start, meal_start, relax_start], 
                                           [play_duration, meal_duration, relax_duration])
        }
    
    def _get_base_time(self, time_range: str) -> datetime:
        """获取基准时间"""
        base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if time_range == "上午":
            base = base.replace(hour=9, minute=0)
        elif time_range == "下午":
            base = base.replace(hour=13, minute=0)
        elif time_range == "晚上":
            base = base.replace(hour=18, minute=0)
        else:
            # 默认周末下午
            base = base.replace(hour=13, minute=0)
        
        return base
    
    def _estimate_cost(self, scene_info: dict, activity: dict, restaurant: dict) -> str:
        """估算费用"""
        people = scene_info.get("people_count", 1)
        
        # 活动费用
        activity_cost = 0
        cost_str = activity.get("cost", "")
        if cost_str:
            # 提取价格范围
            import re
            match = re.search(r'(\d+)-(\d+)元', cost_str)
            if match:
                activity_cost = (int(match.group(1)) + int(match.group(2))) / 2 * people
            else:
                match = re.search(r'(\d+)元', cost_str)
                if match:
                    activity_cost = int(match.group(1)) * people
        
        # 餐饮费用
        restaurant_cost = 0
        price_range = restaurant.get("price_range", restaurant.get("cost", ""))
        if price_range:
            import re
            match = re.search(r'(\d+)-(\d+)元', price_range)
            if match:
                restaurant_cost = (int(match.group(1)) + int(match.group(2))) / 2 * people
            else:
                match = re.search(r'(\d+)元', price_range)
                if match:
                    restaurant_cost = int(match.group(1)) * people
        
        total = activity_cost + restaurant_cost
        
        if total < 100:
            return f"{int(total)}元以内"
        elif total < 300:
            return f"{int(total * 0.8)}-{int(total * 1.2)}元"
        else:
            return f"{int(total * 0.9)}-{int(total * 1.1)}元"
    
    def _get_relax_activity(self, scene_info: dict) -> str:
        """获取轻休闲活动建议"""
        activities = {
            "family": "公园散步",
            "friends": "甜品下午茶",
            "couple": "浪漫散步",
            "solo": "咖啡小憩"
        }
        return activities.get(scene_info["scene_type"], "休闲放松")
    
    def _build_schedule(self, start_times: list, durations: list) -> list:
        """构建时间安排"""
        schedule = []
        for i, (start_time, duration) in enumerate(zip(start_times, durations)):
            end_time = start_time + timedelta(minutes=duration)
            schedule.append({
                "time": start_time.strftime("%H:%M"),
                "description": self._get_schedule_description(i, start_time, end_time)
            })
        return schedule
    
    def _get_schedule_description(self, index: int, start_time, end_time) -> str:
        """获取时间安排描述"""
        descriptions = [
            f"前往活动场地 ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')})",
            f"午餐时间 ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')})",
            f"休闲放松 ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')})"
        ]
        return descriptions[index]
    
    def _select_best_plan(self, candidates: list) -> dict:
        """选择最优方案"""
        if not candidates:
            return self._generate_default_plan({})
        
        # 按综合评分排序
        sorted_plans = sorted(candidates, key=lambda x: x["score"], reverse=True)
        
        best_plan = sorted_plans[0]
        logger.info(f"[PlanningAgent] 选择最优方案 - plan_id: {best_plan['plan_id']}, 评分: {best_plan['score']}")
        
        return best_plan
    
    def _generate_plan_with_rules(self, scene_info: dict, constraints: dict,
                                  activities: list, restaurants: list) -> dict:
        """使用规则生成行程规划（降级方案）"""
        logger.info("[Rules Planning] 开始规则规划...")
        
        base_time = self._get_base_time(constraints["time_range"])
        duration_minutes = int(constraints["duration_hours"] * 60)
        
        play_duration = min(int(duration_minutes * 0.5), 150)
        meal_duration = min(int(duration_minutes * 0.3), 90)
        relax_duration = duration_minutes - play_duration - meal_duration
        
        current_time = base_time
        
        play_start = current_time
        current_time += timedelta(minutes=play_duration)
        play_end = current_time
        
        meal_start = current_time
        current_time += timedelta(minutes=meal_duration)
        meal_end = current_time
        
        relax_start = current_time
        current_time += timedelta(minutes=relax_duration)
        relax_end = current_time
        
        activity = activities[0] if activities else {}
        restaurant = restaurants[0] if restaurants else {}
        
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        
        return {
            "plan_id": plan_id,
            "title": f"{scene_info['scene_name']}周末计划",
            "structure": "游玩 → 就餐 → 轻休闲",
            "steps": [
                {
                    "step_id": f"{plan_id}-play",
                    "type": "activity",
                    "name": activity.get("name", "待定"),
                    "venue_id": activity.get("id", ""),
                    "start_time": play_start.strftime("%H:%M"),
                    "end_time": play_end.strftime("%H:%M"),
                    "location": activity.get("location", ""),
                    "address": activity.get("address", ""),
                    "duration_minutes": play_duration,
                    "notes": ""
                },
                {
                    "step_id": f"{plan_id}-meal",
                    "type": "restaurant",
                    "name": restaurant.get("name", "待定"),
                    "venue_id": restaurant.get("id", ""),
                    "start_time": meal_start.strftime("%H:%M"),
                    "end_time": meal_end.strftime("%H:%M"),
                    "location": restaurant.get("location", ""),
                    "address": restaurant.get("address", ""),
                    "duration_minutes": meal_duration,
                    "notes": ""
                },
                {
                    "step_id": f"{plan_id}-relax",
                    "type": "activity",
                    "name": self._get_relax_activity(scene_info),
                    "start_time": relax_start.strftime("%H:%M"),
                    "end_time": relax_end.strftime("%H:%M"),
                    "duration_minutes": relax_duration,
                    "notes": ""
                }
            ],
            "total_duration": duration_minutes,
            "total_distance": 0,
            "cost_estimate": "待估算",
            "reasoning": "基于规则的简单规划",
            "planning_method": "rules"
        }
    
    def _generate_fallback_plan(self, user_input: str) -> dict:
        """生成兜底计划（完全失败时）"""
        logger.warning("[PlanningAgent] 生成兜底计划")
        
        return {
            "success": True,
            "plan": {
                "plan_id": f"plan-{uuid.uuid4().hex[:8]}",
                "title": "周末活动计划",
                "steps": [],
                "total_duration": 0,
                "reasoning": "系统繁忙，请稍后再试"
            },
            "scene_info": {"scene_type": "solo", "scene_name": "个人休闲"},
            "constraints": {"duration_hours": 4.0},
            "parsing_method": "fallback"
        }
    
    @log_performance("planning.generate_plan")
    def generate_plan(self, parsed_input: dict, user_preferences: dict) -> dict:
        """生成活动计划（兼容旧接口）"""
        logger.info(f"[PlanningAgent] 兼容模式生成计划 - 输入: {parsed_input}, 偏好: {user_preferences}")
        
        user_input = parsed_input.get("input", json.dumps(parsed_input))
        result = self.generate_scene_plan(user_input, user_preferences)
        
        if result.get("success"):
            plan = result["plan"]
            # 转换为旧格式
            return {
                "plan_id": plan["plan_id"],
                "title": plan["title"],
                "schedule": plan.get("schedule", []),
                "activities": [{
                    "name": step["name"],
                    "time": f"{step['start_time']}-{step['end_time']}",
                    "location": step.get("address", step.get("location", "")),
                    "description": f"{step['name']}（{step.get('duration', 0)}分钟）",
                    "travel_time": step.get("travel_time", "")
                } for step in plan.get("steps", []) if step["type"] == "activity"],
                "restaurants": [{
                    "name": step["name"],
                    "time": step["start_time"],
                    "location": step.get("address", step.get("location", "")),
                    "cuisine": step.get("type", ""),
                    "price_range": step.get("price_range", "")
                } for step in plan.get("steps", []) if step["type"] == "restaurant"],
                "transportation": "建议根据实时路况选择出行方式",
                "estimated_cost": plan.get("cost_estimate", "")
            }
        else:
            return self._generate_default_plan(parsed_input)
    
    def _generate_default_plan(self, parsed_input: dict) -> dict:
        """生成默认计划"""
        logger.info("[PlanningAgent] 生成默认计划")
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
                {"name": activity, "time": "10:00-16:00", "location": location, 
                 "description": f"在{location}进行{activity}"}
            ],
            "restaurants": [
                {"name": "推荐餐厅", "time": "12:00", "location": f"{location}附近", 
                 "cuisine": "中餐", "price_range": "适中"}
            ],
            "transportation": "建议自驾或乘坐公共交通",
            "estimated_cost": "300-500元"
        }
    
    def validate_plan(self, plan: dict) -> tuple[bool, str]:
        """验证计划合理性"""
        if not plan.get("plan_id"):
            return False, "计划ID缺失"
        if not plan.get("steps") and not plan.get("activities"):
            return False, "活动列表为空"
        return True, "验证通过"
    
    def save_plan(self, plan: dict) -> bool:
        """保存计划"""
        if plan.get("plan_id"):
            self._plans[plan["plan_id"]] = plan
            logger.info(f"[PlanningAgent] 计划已保存 - plan_id: {plan['plan_id']}")
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
