"""数据模型定义 - API Schema

定义API请求和响应的数据结构。
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# 请求模型
class UserRequest(BaseModel):
    """用户请求模型"""
    user_id: str = Field(..., description="用户唯一标识")
    input: str = Field(..., description="用户自然语言输入")

class ConfirmRequest(BaseModel):
    """确认请求模型"""
    user_id: str = Field(..., description="用户唯一标识")
    plan_id: str = Field(..., description="计划唯一标识")

class PreferenceUpdateRequest(BaseModel):
    """偏好更新请求"""
    user_id: str = Field(..., description="用户唯一标识")
    preferences: Dict[str, str] = Field(..., description="用户偏好键值对")

# 响应模型
class ParsedEntity(BaseModel):
    """解析后的实体"""
    location: str = Field("", description="地点")
    activity: str = Field("", description="活动")
    cuisine: str = Field("", description="餐饮偏好")
    relationship: str = Field("", description="关系")
    time: str = Field("", description="时间")

class PlanActivity(BaseModel):
    """计划活动"""
    name: str = Field(..., description="活动名称")
    time: str = Field(..., description="活动时间")
    location: str = Field(..., description="活动地点")
    travel_time: str = Field("", description="交通时间")
    description: str = Field("", description="活动描述")

class PlanRestaurant(BaseModel):
    """餐饮推荐"""
    name: str = Field(..., description="餐厅名称")
    time: str = Field(..., description="用餐时间")
    location: str = Field(..., description="餐厅位置")
    cuisine: str = Field("", description="菜系")
    price_range: str = Field("", description="价格区间")

class PlanResponse(BaseModel):
    """计划生成响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="提示信息")
    plan_id: str = Field("", description="计划唯一标识")
    title: str = Field("", description="计划标题")
    schedule: List[Dict[str, str]] = Field(default_factory=list, description="时间安排")
    activities: List[PlanActivity] = Field(default_factory=list, description="活动列表")
    restaurants: List[PlanRestaurant] = Field(default_factory=list, description="餐饮推荐")
    transportation: str = Field("", description="交通建议")
    estimated_cost: str = Field("", description="预估费用")

class ExecutionResponse(BaseModel):
    """执行响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="执行结果消息")
    itinerary_id: str = Field("", description="行程单唯一标识")
    status: str = Field("", description="执行状态")
    details: Dict = Field(default_factory=dict, description="行程详情")

class PreferencesResponse(BaseModel):
    """偏好查询响应"""
    success: bool = Field(..., description="是否成功")
    user_id: str = Field("", description="用户唯一标识")
    preferences: Dict[str, str] = Field(default_factory=dict, description="用户偏好")