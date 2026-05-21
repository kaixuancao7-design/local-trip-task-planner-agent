"""规划模块API端点

提供活动计划的生成和确认功能。
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from models.schemas import UserRequest, ConfirmRequest, PlanResponse, ExecutionResponse
from core.parser import InputParser
from core.planner import PlanningAgent
from core.executor import ExecutionAgent
from data.memory_manager import MemoryManager
from config.logging_config import logger
import asyncio
import json

router = APIRouter(prefix="/plan", tags=["规划"])

# 初始化核心组件
parser = InputParser()
planner = PlanningAgent()
executor = ExecutionAgent()
memory_manager = MemoryManager()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()

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
        # 从planner获取真实的计划数据
        plan = planner.get_plan(request.plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="计划不存在")
        
        plan_details = {
            "activities": plan.get("activities", []),
            "restaurants": plan.get("restaurants", [])
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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点：处理计划生成的双向通信"""
    await manager.connect(websocket)
    logger.info("[WebSocket] 客户端连接已建立")
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            action = data.get("action")
            logger.info(f"[WebSocket] 收到客户端消息 - action: {action}")
            
            if action == "generate_plan":
                # 提取请求参数
                user_id = data.get("user_id")
                user_input = data.get("input")
                
                if not user_id or not user_input:
                    logger.warning("[WebSocket] 缺少必要参数")
                    await manager.send_personal_message(
                        {"type": "error", "message": "缺少必要参数"},
                        websocket
                    )
                    continue
                
                logger.info(f"[WebSocket] 开始生成计划 - user_id: {user_id}, input: {user_input[:50]}...")
                # 执行计划生成流程
                await execute_plan_generation(user_id, user_input, websocket)
            
            elif action == "cancel":
                # 取消任务（可扩展）
                logger.info("[WebSocket] 收到取消任务请求")
                await manager.send_personal_message(
                    {"type": "cancelled", "message": "任务已取消"},
                    websocket
                )
            
            else:
                logger.warning(f"[WebSocket] 未知操作: {action}")
                await manager.send_personal_message(
                    {"type": "error", "message": f"未知操作: {action}"},
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("[WebSocket] 客户端断开连接")
    except Exception as e:
        logger.error(f"[WebSocket] 错误: {e}")
        try:
            await manager.send_personal_message(
                {"type": "error", "message": str(e)},
                websocket
            )
        except:
            pass

async def execute_plan_generation(user_id: str, user_input: str, websocket: WebSocket):
    """执行计划生成流程，通过WebSocket实时推送状态"""
    logger.info(f"[WebSocket] 开始执行计划生成流程 - user_id: {user_id}")
    
    try:
        # Step 1: 解析用户输入
        logger.debug("[WebSocket] Step 1: 解析用户输入")
        await manager.send_personal_message({
            "type": "thinking",
            "step": 1,
            "message": "正在解析用户输入..."
        }, websocket)
        await asyncio.sleep(0.5)
        
        parsed_input = parser.parse({"input": user_input})
        logger.debug(f"[WebSocket] 用户输入解析完成 - 结果: {parsed_input}")
        
        # Step 2: 检索用户偏好
        logger.debug("[WebSocket] Step 2: 检索用户偏好")
        await manager.send_personal_message({
            "type": "thinking",
            "step": 2,
            "message": "正在检索用户偏好..."
        }, websocket)
        await asyncio.sleep(0.5)
        
        user_preferences = memory_manager.get_user_preferences(user_id)
        logger.debug(f"[WebSocket] 用户偏好检索完成 - 偏好: {user_preferences}")
        
        # Step 3: 生成计划
        logger.debug("[WebSocket] Step 3: 生成计划")
        await manager.send_personal_message({
            "type": "thinking", 
            "step": 3,
            "message": "正在调用LLM生成计划..."
        }, websocket)
        await asyncio.sleep(1)
        
        plan = planner.generate_plan(parsed_input, user_preferences)
        logger.info(f"[WebSocket] 计划生成完成 - plan_id: {plan.get('plan_id')}")
        
        # Step 4: 更新偏好
        logger.debug("[WebSocket] Step 4: 更新用户偏好")
        await manager.send_personal_message({
            "type": "thinking",
            "step": 4,
            "message": "正在更新用户偏好..."
        }, websocket)
        await asyncio.sleep(0.3)
        
        memory_manager.update_user_preferences(user_id, parsed_input)
        logger.debug("[WebSocket] 用户偏好更新完成")
        
        # Step 5: 返回最终结果
        logger.info("[WebSocket] 计划生成流程完成，发送结果")
        
        # 构建符合前端期望的响应格式
        response_data = {
            "type": "complete",
            "success": True,
            "message": "计划生成成功",
            "plan_id": plan.get("plan_id", ""),
            "title": plan.get("title", ""),
            "schedule": plan.get("schedule", []),
            "activities": plan.get("activities", []),
            "restaurants": plan.get("restaurants", []),
            "transportation": plan.get("transportation", ""),
            "estimated_cost": plan.get("estimated_cost", "")
        }
        
        await manager.send_personal_message(response_data, websocket)
        
    except Exception as e:
        logger.error(f"[WebSocket] 计划生成流程失败 - 错误: {e}")
        await manager.send_personal_message({
            "type": "error",
            "success": False,
            "message": str(e)
        }, websocket)