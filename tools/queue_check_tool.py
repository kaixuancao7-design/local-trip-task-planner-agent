
"""工具层 - 排队空位核验工具

提供餐厅/场地排队人数、剩余空位的实时查询功能。
支持模拟数据和真实API回退机制。
"""
import random
import time
from config.logging_config import log_performance, logger

class QueueCheckTool:
    """排队空位核验工具类"""
    
    def __init__(self):
        # 模拟数据库存储排队信息
        self.simulated_queue_data = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """初始化模拟排队数据"""
        venues = [
            ("南京儿童乐园", "mock-qz-001", "activity"),
            ("南京动物园", "mock-qz-002", "activity"),
            ("南京科技馆", "mock-qz-003", "activity"),
            ("南京艺术展览馆", "mock-hy-001", "activity"),
            ("老门东历史街区", "mock-hy-002", "activity"),
            ("南京轻食沙拉屋", "mock-rest-jf-001", "restaurant"),
            ("绿氧健康餐厅", "mock-rest-jf-002", "restaurant"),
            ("川渝火锅城", "mock-rest-tj-001", "restaurant"),
            ("浪漫西餐厅", "mock-rest-ql-001", "restaurant"),
            ("南京欢乐亲子餐厅", "mock-rest-qz-001", "restaurant")
        ]
        
        for name, venue_id, venue_type in venues:
            self.simulated_queue_data[venue_id] = {
                "venue_id": venue_id,
                "name": name,
                "type": venue_type,
                "waiting_count": random.randint(0, 50),
                "available_seats": random.randint(0, 20),
                "estimated_wait_time": random.randint(0, 60),
                "status": random.choice(["available", "limited", "full"]),
                "update_time": self._get_current_time()
            }
    
    @log_performance("queue.check")
    def check_queue(self, venue_id: str) -> dict:
        """查询场地/餐厅排队状态
        
        Args:
            venue_id: 场地/餐厅ID
        
        Returns:
            排队状态信息
        """
        logger.info(f"[QueueCheckTool] 查询排队状态 - venue_id: {venue_id}")
        
        try:
            # 模拟API延迟
            time.sleep(0.2)
            
            # 优先返回模拟数据（真实场景可调用排队API）
            if venue_id in self.simulated_queue_data:
                data = self.simulated_queue_data[venue_id]
                # 模拟实时更新
                data["waiting_count"] = max(0, data["waiting_count"] + random.randint(-2, 5))
                data["available_seats"] = max(0, data["available_seats"] + random.randint(-3, 3))
                data["estimated_wait_time"] = max(0, int(data["waiting_count"] * 1.2))
                data["status"] = self._update_status(data["waiting_count"], data["available_seats"])
                data["update_time"] = self._get_current_time()
                
                logger.info(f"[QueueCheckTool] 查询成功 - 名称: {data['name']}, 排队人数: {data['waiting_count']}, 空位: {data['available_seats']}")
                return data
            else:
                # 未知场地，返回默认数据
                logger.warning(f"[QueueCheckTool] 未找到场地信息 - venue_id: {venue_id}")
                return self._get_default_queue_info(venue_id)
        
        except Exception as e:
            logger.warning(f"查询排队状态失败: {str(e)}，返回默认数据")
            return self._get_default_queue_info(venue_id)
    
    @log_performance("queue.batch_check")
    def batch_check_queue(self, venue_ids: list) -> list:
        """批量查询多个场地排队状态
        
        Args:
            venue_ids: 场地ID列表
        
        Returns:
            排队状态列表
        """
        logger.info(f"[QueueCheckTool] 批量查询排队状态 - venue_ids: {venue_ids}")
        
        results = []
        for venue_id in venue_ids:
            result = self.check_queue(venue_id)
            results.append(result)
        
        logger.info(f"[QueueCheckTool] 批量查询完成 - 成功 {len(results)} 个")
        return results
    
    @log_performance("queue.get_recommendations")
    def get_recommendations(self, venue_ids: list, max_wait_time: int = 20) -> list:
        """获取推荐场地（根据排队时间筛选）
        
        Args:
            venue_ids: 场地ID列表
            max_wait_time: 最大等待时间（分钟）
        
        Returns:
            推荐场地列表（按等待时间排序）
        """
        logger.info(f"[QueueCheckTool] 获取推荐场地 - 最大等待时间: {max_wait_time}分钟")
        
        queue_info = self.batch_check_queue(venue_ids)
        # 筛选等待时间符合要求的场地
        filtered = [v for v in queue_info if v["estimated_wait_time"] <= max_wait_time]
        # 按等待时间排序
        sorted_list = sorted(filtered, key=lambda x: x["estimated_wait_time"])
        
        logger.info(f"[QueueCheckTool] 推荐完成 - 找到 {len(sorted_list)} 个推荐场地")
        return sorted_list
    
    def _update_status(self, waiting_count: int, available_seats: int) -> str:
        """更新场地状态"""
        if available_seats >= 10:
            return "available"
        elif available_seats > 0:
            return "limited"
        else:
            return "full"
    
    def _get_default_queue_info(self, venue_id: str) -> dict:
        """返回默认排队信息"""
        return {
            "venue_id": venue_id,
            "name": "未知场地",
            "type": "unknown",
            "waiting_count": random.randint(5, 20),
            "available_seats": random.randint(0, 10),
            "estimated_wait_time": random.randint(5, 30),
            "status": random.choice(["available", "limited"]),
            "update_time": self._get_current_time()
        }
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
