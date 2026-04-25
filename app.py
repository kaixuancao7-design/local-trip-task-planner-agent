from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agent_core.planner import PlanningAgent
from agent_core.memory import MemoryManager
from agent_core.tools import MapTool, WeatherTool

app = FastAPI(
    title="Local Activity Agent",
    description="智能活动规划代理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化核心组件
memory_manager = MemoryManager()
map_tool = MapTool()
weather_tool = WeatherTool()
planning_agent = PlanningAgent(memory_manager, map_tool, weather_tool)

# 数据模型
class UserRequest(BaseModel):
    user_id: str
    input: str

class PlanResponse(BaseModel):
    success: bool
    message: str
    plan: dict

class ConfirmRequest(BaseModel):
    user_id: str
    plan_id: str

class ExecutionResponse(BaseModel):
    success: bool
    message: str
    itinerary: dict

@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(request: UserRequest):
    """生成活动计划"""
    try:
        # 1. 感知阶段：解析用户输入
        parsed_input = planning_agent.parse_input(request.input)
        
        # 2. 记忆检索：获取用户偏好
        user_preferences = memory_manager.get_user_preferences(request.user_id)
        
        # 3. 规划与决策：生成计划
        plan = planning_agent.generate_plan(parsed_input, user_preferences)
        
        return PlanResponse(
            success=True,
            message="计划生成成功",
            plan=plan
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/confirm", response_model=ExecutionResponse)
async def confirm_plan(request: ConfirmRequest):
    """确认并执行计划"""
    try:
        # 4. 执行与反馈：执行计划
        itinerary = planning_agent.execute_plan(request.plan_id)
        
        return ExecutionResponse(
            success=True,
            message="计划执行成功",
            itinerary=itinerary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """获取用户偏好"""
    try:
        preferences = memory_manager.get_user_preferences(user_id)
        return {"success": True, "preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)