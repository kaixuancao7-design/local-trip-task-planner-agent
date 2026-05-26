
"""工具层 - 活动/餐厅预订工具

提供一键预约、下单、占位操作（Mock实现）。
支持活动门票预订和餐厅座位预订。
"""
import uuid
import time
from config.logging_config import log_performance, logger

class BookingTool:
    """预订工具类 - Mock实现"""
    
    def __init__(self):
        self.bookings = {}
        self.venue_capacity = {
            "mock-qz-001": {"max_capacity": 200},
            "mock-qz-002": {"max_capacity": 300},
            "mock-qz-003": {"max_capacity": 150},
            "mock-hy-001": {"max_capacity": 100},
            "mock-hy-002": {"max_capacity": 500},
            "mock-rest-jf-001": {"max_capacity": 50},
            "mock-rest-jf-002": {"max_capacity": 60},
            "mock-rest-tj-001": {"max_capacity": 100},
            "mock-rest-ql-001": {"max_capacity": 40},
            "mock-rest-qz-001": {"max_capacity": 80}
        }
    
    def _get_current_booked_count(self, venue_id: str) -> int:
        """动态计算当前已预订人数"""
        total_booked = 0
        for booking in self.bookings.values():
            if booking.get("venue_id") == venue_id and booking.get("status") not in ["cancelled", "expired"]:
                quantity = booking.get("quantity") or booking.get("guests") or 1
                total_booked += quantity
        return total_booked
    
    @log_performance("booking.create_activity_booking")
    def create_activity_booking(self, venue_id: str, user_id: str, date: str, 
                               time_slot: str, quantity: int = 1) -> dict:
        """预订活动门票
        
        Args:
            venue_id: 活动场地ID
            user_id: 用户ID
            date: 预订日期（YYYY-MM-DD）
            time_slot: 时间段（如 "10:00-12:00"）
            quantity: 人数
        
        Returns:
            预订结果
        """
        logger.info(f"[BookingTool] 创建活动预订 - venue_id: {venue_id}, user_id: {user_id}, date: {date}, time_slot: {time_slot}")
        
        try:
            capacity_info = self.venue_capacity.get(venue_id)
            if capacity_info:
                max_capacity = capacity_info["max_capacity"]
                current_booked = self._get_current_booked_count(venue_id)
                available = max_capacity - current_booked
                
                if available < quantity:
                    logger.warning(f"[BookingTool] 场地已满 - venue_id: {venue_id}, 剩余容量: {available}")
                    return {
                        "success": False,
                        "booking_ref": "",
                        "message": f"场地已满，剩余容量: {available}人",
                        "venue_id": venue_id,
                        "date": date,
                        "time_slot": time_slot,
                        "quantity": quantity
                    }
            
            # 生成预订号
            booking_ref = f"ACT-{uuid.uuid4().hex[:8].upper()}"
            
            booking = {
                "booking_ref": booking_ref,
                "venue_id": venue_id,
                "venue_type": "activity",
                "user_id": user_id,
                "date": date,
                "time_slot": time_slot,
                "quantity": quantity,
                "status": "confirmed",
                "created_at": self._get_current_time(),
                "expire_at": self._get_expire_time(date)
            }
            
            self.bookings[booking_ref] = booking
            logger.info(f"[BookingTool] 活动预订成功 - booking_ref: {booking_ref}")
            
            return booking
            
        except Exception as e:
            logger.error(f"创建活动预订失败: {str(e)}")
            return {
                "success": False,
                "booking_ref": "",
                "message": str(e),
                "venue_id": venue_id,
                "date": date,
                "time_slot": time_slot,
                "quantity": quantity
            }
    
    @log_performance("booking.create_restaurant_booking")
    def create_restaurant_booking(self, venue_id: str, user_id: str, date: str, 
                                 time_slot: str, guests: int = 2) -> dict:
        """预订餐厅座位
        
        Args:
            venue_id: 餐厅ID
            user_id: 用户ID
            date: 预订日期（YYYY-MM-DD）
            time_slot: 用餐时间（如 "12:00"）
            guests: 用餐人数
        
        Returns:
            预订结果
        """
        logger.info(f"[BookingTool] 创建餐厅预订 - venue_id: {venue_id}, user_id: {user_id}, date: {date}, time_slot: {time_slot}, guests: {guests}")
        
        try:
            capacity_info = self.venue_capacity.get(venue_id)
            if capacity_info:
                max_capacity = capacity_info["max_capacity"]
                current_booked = self._get_current_booked_count(venue_id)
                available = max_capacity - current_booked
                
                if available < guests:
                    logger.warning(f"[BookingTool] 餐厅已满 - venue_id: {venue_id}, 剩余座位: {available}")
                    return {
                        "success": False,
                        "booking_ref": "",
                        "message": f"餐厅已满，剩余座位: {available}个",
                        "venue_id": venue_id,
                        "date": date,
                        "time_slot": time_slot,
                        "guests": guests
                    }
            
            # 生成预订号
            booking_ref = f"RES-{uuid.uuid4().hex[:8].upper()}"
            
            booking = {
                "booking_ref": booking_ref,
                "venue_id": venue_id,
                "venue_type": "restaurant",
                "user_id": user_id,
                "date": date,
                "time_slot": time_slot,
                "guests": guests,
                "status": "booked",
                "created_at": self._get_current_time(),
                "expire_at": self._get_expire_time(date)
            }
            
            self.bookings[booking_ref] = booking
            logger.info(f"[BookingTool] 餐厅预订成功 - booking_ref: {booking_ref}")
            
            return {
                "success": True,
                "booking_ref": booking_ref,
                "venue_id": venue_id,
                "venue_type": "restaurant",
                "date": date,
                "time_slot": time_slot,
                "guests": guests
            }
            
        except Exception as e:
            logger.error(f"创建餐厅预订失败: {str(e)}")
            return {
                "success": False,
                "booking_ref": "",
                "message": str(e),
                "venue_id": venue_id,
                "date": date,
                "time_slot": time_slot,
                "guests": guests
            }
    
    @log_performance("booking.get_booking")
    def get_booking(self, booking_ref: str) -> dict:
        """查询预订详情
        
        Args:
            booking_ref: 预订号
        
        Returns:
            预订详情
        """
        logger.info(f"[BookingTool] 查询预订详情 - booking_ref: {booking_ref}")
        
        booking = self.bookings.get(booking_ref)
        if booking:
            logger.info(f"[BookingTool] 预订查询成功 - booking_ref: {booking_ref}, status: {booking['status']}")
            return booking
        else:
            logger.warning(f"[BookingTool] 预订不存在 - booking_ref: {booking_ref}")
            return {
                "success": False,
                "booking_ref": booking_ref,
                "message": "预订不存在"
            }
    
    @log_performance("booking.cancel_booking")
    def cancel_booking(self, booking_ref: str) -> bool:
        """取消预订
        
        Args:
            booking_ref: 预订号
        
        Returns:
            是否取消成功
        """
        logger.info(f"[BookingTool] 取消预订 - booking_ref: {booking_ref}")
        
        booking = self.bookings.get(booking_ref)
        if booking:
            venue_id = booking["venue_id"]
            booking["status"] = "cancelled"
            logger.info(f"[BookingTool] 预订已取消 - booking_ref: {booking_ref}")
            return True
        
        logger.warning(f"[BookingTool] 取消预订失败 - booking_ref: {booking_ref} 不存在")
        return False
    
    @log_performance("booking.get_user_bookings")
    def get_user_bookings(self, user_id: str) -> list:
        """获取用户所有预订
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户预订列表
        """
        logger.info(f"[BookingTool] 获取用户预订列表 - user_id: {user_id}")
        
        user_bookings = [b for b in self.bookings.values() if b.get("user_id") == user_id]
        logger.info(f"[BookingTool] 用户预订查询完成 - user_id: {user_id}, 数量: {len(user_bookings)}")
        
        return user_bookings
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_expire_time(self, date: str) -> str:
        """计算预订过期时间（预订日期当天23:59）"""
        return f"{date} 23:59:59"
