import chromadb
import json
import os
from chromadb.config import Settings
import config

class MemoryManager:
    def __init__(self):
        # 初始化ChromaDB
        self.client = chromadb.Client(
            Settings(
                persist_directory=config.CHROMA_DB_PATH,
                anonymized_telemetry=False
            )
        )
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(name=config.CHROMA_COLLECTION_NAME)
    
    def get_user_preferences(self, user_id):
        """获取用户偏好"""
        # 向量化用户ID
        results = self.collection.query(
            query_texts=[user_id],
            n_results=1
        )
        
        if results["documents"] and results["documents"][0]:
            try:
                preferences = json.loads(results["documents"][0][0])
                return preferences
            except json.JSONDecodeError:
                return self._get_default_preferences()
        else:
            # 如果没有找到，返回默认偏好
            return self._get_default_preferences()
    
    def update_user_preferences(self, user_id, preferences):
        """更新用户偏好"""
        # 检查用户是否已存在
        results = self.collection.query(
            query_texts=[user_id],
            n_results=1
        )
        
        if results["ids"] and results["ids"][0]:
            # 更新现有用户
            self.collection.update(
                ids=[results["ids"][0][0]],
                documents=[json.dumps(preferences, ensure_ascii=False)],
                metadatas=[{"user_id": user_id}]
            )
        else:
            # 添加新用户
            self.collection.add(
                ids=[user_id],
                documents=[json.dumps(preferences, ensure_ascii=False)],
                metadatas=[{"user_id": user_id}]
            )
    
    def _get_default_preferences(self):
        """获取默认偏好"""
        return {
            "preferred_restaurants": [],
            "preferred_activities": [],
            "budget_range": [200, 500],
            "time_preference": "上午",
            " dietary_restrictions": [],
            " past_experiences": []
        }
    
    def add_user_experience(self, user_id, experience):
        """添加用户体验"""
        preferences = self.get_user_preferences(user_id)
        if "past_experiences" not in preferences:
            preferences["past_experiences"] = []
        preferences["past_experiences"].append(experience)
        self.update_user_preferences(user_id, preferences)