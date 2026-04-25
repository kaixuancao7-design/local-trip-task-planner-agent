from pydantic import BaseModel
from typing import List, Optional, Dict

class UserRequest(BaseModel):
    """用户请求模型"""
    user_id: str
    input: str

class PlanResponse(BaseModel):
    """计划响应模型"""
    success: bool
    message: str
    plan: Dict

class ConfirmRequest(BaseModel):
    """确认请求模型"""
    user_id: str
    plan_id: str

class ExecutionResponse(BaseModel):
    """执行响应模型"""
    success: bool
    message: str
    itinerary: Dict

class UserPreferences(BaseModel):
    """用户偏好模型"""
    preferred_restaurants: List[str] = []
    preferred_activities: List[str] = []
    budget_range: List[float] = [200, 500]
    time_preference: str = "上午"
    dietary_restrictions: List[str] = []
    past_experiences: List[Dict] = []