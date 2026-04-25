"""规划模块API端点

提供活动计划的生成和确认功能。
"""
from fastapi import APIRouter, HTTPException
from models.schemas import UserRequest, ConfirmRequest, PlanResponse, ExecutionResponse
from core.parser import InputParser
from core.planner import PlanningAgent
from core.executor import ExecutionAgent
from data.memory_manager import MemoryManager

router = APIRouter(prefix="/plan", tags=["规划"])

# 初始化核心组件
parser = InputParser()
planner = PlanningAgent()
executor = ExecutionAgent()
memory_manager = MemoryManager()

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(request: UserRequest):
    """生成活动计划"""
    try:
        # 1. 感知阶段：解析用户输入
        parsed_input = parser.parse(request.input)
        
        # 2. 记忆检索：获取用户偏好
        user_preferences = memory_manager.get_user_preferences(request.user_id)
        
        # 3. 规划与决策：生成计划
        plan = planner.generate_plan(parsed_input, user_preferences)
        
        # 4. 更新用户偏好（基于当前输入学习）
        memory_manager.update_user_preferences(request.user_id, parsed_input)
        
        return PlanResponse(
            success=True,
            message="计划生成成功",
            plan_id=plan.get("plan_id", ""),
            title=plan.get("title", ""),
            schedule=plan.get("schedule", []),
            activities=plan.get("activities", []),
            restaurants=plan.get("restaurants", []),
            transportation=plan.get("transportation", ""),
            estimated_cost=plan.get("estimated_cost", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecutionResponse)
async def execute_plan(request: ConfirmRequest):
    """执行计划，生成行程单"""
    try:
        # 简化实现：使用模拟数据
        plan_details = {
            "activities": [
                {"name": "紫金山爬山", "time": "09:30-12:00", "location": "紫金山"},
                {"name": "山顶观景", "time": "12:00-13:00", "location": "紫金山山顶"}
            ],
            "restaurants": [
                {"name": "紫金餐厅", "time": "13:30", "location": "紫金山脚下", "cuisine": "中餐", "price_range": "适中"}
            ]
        }
        
        itinerary = executor.execute_plan(request.plan_id, plan_details)
        
        return ExecutionResponse(
            success=True,
            message=itinerary.get("message", "执行成功"),
            itinerary_id=itinerary.get("itinerary_id", ""),
            status=itinerary.get("status", ""),
            details=itinerary.get("details", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))