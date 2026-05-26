"""数据模型定义 - API Schema

定义API请求和响应的数据结构。
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

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

class ScenePlanRequest(BaseModel):
    """场景化计划请求"""
    user_id: str = Field(..., description="用户唯一标识")
    input: str = Field(..., description="用户自然语言输入")
    scene_type: Optional[str] = Field(None, description="场景类型（family/friends/couple/solo）")
    user_location: Optional[str] = Field(None, description="用户位置（经纬度）")

# 场景识别结果
class SceneInfo(BaseModel):
    """场景识别结果"""
    scene_type: str = Field(..., description="场景类型（family/friends/couple/solo）")
    scene_name: str = Field(..., description="场景名称（亲子/好友聚会/情侣约会/个人休闲）")
    people_count: int = Field(1, description="人数")
    age_group: str = Field("adult", description="年龄组（child/adult/elder）")
    relationship: str = Field("", description="关系类型")

# 约束条件
class Constraints(BaseModel):
    """约束条件"""
    time_range: str = Field("", description="时间范围")
    duration_hours: float = Field(4.0, description="预计时长（小时）")
    distance_limit: float = Field(3.0, description="距离限制（公里）")
    budget_min: float = Field(0.0, description="最低预算")
    budget_max: float = Field(1000.0, description="最高预算")
    cuisine_preference: str = Field("", description="餐饮偏好")
    max_waiting_time: int = Field(20, description="最大排队时间（分钟）")

# 场地信息
class VenueInfo(BaseModel):
    """场地信息"""
    id: str = Field(..., description="场地ID")
    name: str = Field(..., description="场地名称")
    location: str = Field(..., description="经纬度")
    address: str = Field("", description="详细地址")
    type: str = Field("", description="场地类型")
    price_range: str = Field("", description="价格区间")
    rating: float = Field(0.0, description="评分")
    waiting_time: int = Field(0, description="排队时间（分钟）")
    available: bool = Field(True, description="是否可用")
    commute_time: str = Field("", description="通勤时间")
    commute_distance: int = Field(0, description="通勤距离（米）")

# 预订结果
class BookingResult(BaseModel):
    """预订结果"""
    success: bool = Field(..., description="是否成功")
    booking_ref: str = Field("", description="预订号")
    venue_id: str = Field("", description="场地ID")
    venue_name: str = Field("", description="场地名称")
    date: str = Field("", description="预订日期")
    time_slot: str = Field("", description="时间段")
    guests: int = Field(1, description="人数")
    status: str = Field("pending", description="预订状态")
    message: str = Field("", description="提示信息")

# 行程步骤
class ItineraryStep(BaseModel):
    """行程步骤"""
    step_id: str = Field(..., description="步骤ID")
    type: str = Field(..., description="步骤类型（activity/restaurant/transport）")
    name: str = Field(..., description="名称")
    venue_id: str = Field("", description="场地ID")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    location: str = Field("", description="位置")
    address: str = Field("", description="地址")
    duration: int = Field(0, description="时长（分钟）")
    status: str = Field("pending", description="状态")
    booking_ref: str = Field("", description="预订号")

# 候选方案
class CandidatePlan(BaseModel):
    """候选方案"""
    plan_id: str = Field(..., description="方案ID")
    title: str = Field(..., description="方案标题")
    score: float = Field(0.0, description="综合评分")
    score_details: Dict[str, float] = Field(default_factory=dict, description="评分详情")
    duration: int = Field(0, description="总时长（分钟）")
    total_distance: int = Field(0, description="总距离（米）")
    steps: List[ItineraryStep] = Field(default_factory=list, description="行程步骤")
    cost_estimate: str = Field("", description="费用估算")

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