"""用户偏好API端点

提供用户偏好的查询和管理功能。
"""
from fastapi import APIRouter, HTTPException
from models.schemas import PreferenceUpdateRequest, PreferencesResponse
from data.memory_manager import MemoryManager

router = APIRouter(prefix="/preferences", tags=["偏好管理"])

memory_manager = MemoryManager()

@router.get("/{user_id}", response_model=PreferencesResponse)
async def get_user_preferences(user_id: str):
    """获取用户偏好"""
    try:
        preferences = memory_manager.get_user_preferences(user_id)
        return PreferencesResponse(
            success=True,
            user_id=user_id,
            preferences=preferences
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=PreferencesResponse)
async def update_user_preferences(request: PreferenceUpdateRequest):
    """更新用户偏好"""
    try:
        success = memory_manager.update_user_preferences(request.user_id, request.preferences)
        if success:
            preferences = memory_manager.get_user_preferences(request.user_id)
            return PreferencesResponse(
                success=True,
                user_id=request.user_id,
                preferences=preferences
            )
        else:
            raise HTTPException(status_code=500, detail="更新偏好失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user_preferences(user_id: str):
    """删除用户偏好"""
    try:
        success = memory_manager.delete_user_preferences(user_id)
        if success:
            return {"success": True, "message": "偏好删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除偏好失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))