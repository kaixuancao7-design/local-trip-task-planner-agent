"""数据访问层 - 记忆管理器

负责管理用户偏好的存储和检索，使用Chroma向量数据库。
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import json
import uuid
from config.settings import settings

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chroma_db_path,
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )
    
    def save_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """保存用户偏好"""
        try:
            # 将偏好字典转换为JSON字符串作为文档
            document = json.dumps(preferences, ensure_ascii=False)
            
            # 使用用户ID作为文档ID
            self.collection.upsert(
                documents=[document],
                metadatas=[{"user_id": user_id, "type": "preferences"}],
                ids=[user_id]
            )
            return True
        except Exception as e:
            print(f"保存偏好失败: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> dict:
        """获取用户偏好"""
        try:
            results = self.collection.get(
                ids=[user_id],
                where={"user_id": user_id}
            )
            
            if results["documents"]:
                document = results["documents"][0]
                return json.loads(document)
            else:
                return self._get_default_preferences()
        except Exception as e:
            print(f"获取偏好失败: {e}")
            return self._get_default_preferences()
    
    def update_user_preferences(self, user_id: str, new_preferences: dict) -> bool:
        """更新用户偏好（增量更新）"""
        try:
            existing = self.get_user_preferences(user_id)
            existing.update(new_preferences)
            return self.save_user_preferences(user_id, existing)
        except Exception as e:
            print(f"更新偏好失败: {e}")
            return False
    
    def delete_user_preferences(self, user_id: str) -> bool:
        """删除用户偏好"""
        try:
            self.collection.delete(ids=[user_id])
            return True
        except Exception as e:
            print(f"删除偏好失败: {e}")
            return False
    
    def search_similar_users(self, preferences: dict, n_results: int = 3) -> list:
        """搜索相似用户偏好"""
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
            return similar_preferences
        except Exception as e:
            print(f"搜索相似用户失败: {e}")
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