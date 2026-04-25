"""领域模型定义

定义业务领域核心实体和值对象。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class UserPreferences:
    """用户偏好领域模型"""
    user_id: str
    preferences: Dict[str, str] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class Activity:
    """活动领域模型"""
    id: str
    name: str
    location: str
    start_time: str
    end_time: str
    description: str = ""
    travel_time: str = ""

@dataclass
class Restaurant:
    """餐厅领域模型"""
    id: str
    name: str
    location: str
    cuisine: str
    price_range: str
    rating: float = 0.0

@dataclass
class Plan:
    """计划领域模型"""
    plan_id: str
    user_id: str
    title: str
    activities: List[Activity] = field(default_factory=list)
    restaurants: List[Restaurant] = field(default_factory=list)
    transportation: str = ""
    estimated_cost: float = 0.0
    created_at: Optional[str] = None

@dataclass
class Itinerary:
    """行程单领域模型"""
    itinerary_id: str
    plan_id: str
    user_id: str
    status: str  # pending, confirmed, completed, cancelled
    activities: List[Activity] = field(default_factory=list)
    restaurants: List[Restaurant] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None