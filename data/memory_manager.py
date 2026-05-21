"""数据访问层 - 记忆管理器

负责管理用户偏好的存储和检索，使用Chroma向量数据库。
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import json
import uuid
from config.settings import settings
from config.logging_config import logger

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        logger.info("[MemoryManager] 初始化记忆管理器")
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chroma_db_path,
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )
        logger.info(f"[MemoryManager] 记忆管理器初始化完成 - 集合: {settings.chroma_collection_name}")
    
    def save_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """保存用户偏好"""
        logger.info(f"[MemoryManager] 保存用户偏好 - user_id: {user_id}")
        logger.debug(f"[MemoryManager] 偏好内容: {preferences}")
        
        try:
            # 将偏好字典转换为JSON字符串作为文档
            document = json.dumps(preferences, ensure_ascii=False)
            
            # 使用用户ID作为文档ID
            self.collection.upsert(
                documents=[document],
                metadatas=[{"user_id": user_id, "type": "preferences"}],
                ids=[user_id]
            )
            logger.info(f"[MemoryManager] 用户偏好保存成功 - user_id: {user_id}")
            return True
        except Exception as e:
            logger.error(f"[MemoryManager] 保存偏好失败 - user_id: {user_id}, 错误: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> dict:
        """获取用户偏好"""
        logger.info(f"[MemoryManager] 获取用户偏好 - user_id: {user_id}")
        
        try:
            results = self.collection.get(
                ids=[user_id],
                where={"user_id": user_id}
            )
            
            if results["documents"]:
                document = results["documents"][0]
                preferences = json.loads(document)
                logger.info(f"[MemoryManager] 用户偏好获取成功 - user_id: {user_id}")
                logger.debug(f"[MemoryManager] 偏好内容: {preferences}")
                return preferences
            else:
                logger.info(f"[MemoryManager] 用户偏好不存在，返回默认值 - user_id: {user_id}")
                return self._get_default_preferences()
        except Exception as e:
            logger.error(f"[MemoryManager] 获取偏好失败 - user_id: {user_id}, 错误: {e}")
            return self._get_default_preferences()
    
    def update_user_preferences(self, user_id: str, new_preferences: dict) -> bool:
        """更新用户偏好（增量更新）"""
        logger.info(f"[MemoryManager] 更新用户偏好 - user_id: {user_id}")
        logger.debug(f"[MemoryManager] 新增偏好: {new_preferences}")
        
        try:
            existing = self.get_user_preferences(user_id)
            existing.update(new_preferences)
            result = self.save_user_preferences(user_id, existing)
            if result:
                logger.info(f"[MemoryManager] 用户偏好更新成功 - user_id: {user_id}")
            return result
        except Exception as e:
            logger.error(f"[MemoryManager] 更新偏好失败 - user_id: {user_id}, 错误: {e}")
            return False
    
    def delete_user_preferences(self, user_id: str) -> bool:
        """删除用户偏好"""
        logger.info(f"[MemoryManager] 删除用户偏好 - user_id: {user_id}")
        
        try:
            self.collection.delete(ids=[user_id])
            logger.info(f"[MemoryManager] 用户偏好删除成功 - user_id: {user_id}")
            return True
        except Exception as e:
            logger.error(f"[MemoryManager] 删除偏好失败 - user_id: {user_id}, 错误: {e}")
            return False
    
    def search_similar_users(self, preferences: dict, n_results: int = 3) -> list:
        """搜索相似用户偏好"""
        logger.info(f"[MemoryManager] 搜索相似用户 - 查询偏好: {preferences}, 结果数: {n_results}")
        
        try:
            query_text = json.dumps(preferences, ensure_ascii=False)
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            similar_preferences = []
            for doc in results["documents"][0]:
                try:
                    similar_preferences.append(json.loads(doc))
                except:
                    pass
            
            logger.info(f"[MemoryManager] 相似用户搜索完成 - 找到 {len(similar_preferences)} 个相似用户")
            return similar_preferences
        except Exception as e:
            logger.error(f"[MemoryManager] 搜索相似用户失败 - 错误: {e}")
            return []
    
    def _get_default_preferences(self) -> dict:
        """获取默认偏好"""
        return {
            "饮食偏好": "",
            "出行方式": "自驾",
            "预算范围": "适中",
            "活动类型": "休闲",
            "时间偏好": "上午",
            "是否早起": "否",
            "餐厅评分要求": "4.5以上"
        }