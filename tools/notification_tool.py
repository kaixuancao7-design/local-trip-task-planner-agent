
"""工具层 - 行程通知生成工具

提供标准化可分享行程文案生成功能。
支持多种格式输出：文本、HTML、Markdown、社交媒体分享文案。
"""
from config.logging_config import log_performance, logger

class NotificationTool:
    """行程通知生成工具类"""
    
    def __init__(self):
        # 场景模板
        self.templates = {
            "family": {
                "greeting": "👨‍👩‍👧‍👦 亲子周末计划已生成！",
                "farewell": "祝你们度过愉快的亲子时光！💕"
            },
            "friends": {
                "greeting": "👯‍♀️ 好友聚会计划已安排！",
                "farewell": "祝你们玩得开心！🎉"
            },
            "couple": {
                "greeting": "💑 浪漫约会计划已生成！",
                "farewell": "祝你们有个美好的约会！🌹"
            },
            "solo": {
                "greeting": "🧘 个人休闲计划已准备好！",
                "farewell": "享受独处时光！✨"
            }
        }
    
    @log_performance("notification.generate_text")
    def generate_text_notification(self, plan: dict, scene_type: str = "friends") -> str:
        """生成纯文本格式行程通知
        
        Args:
            plan: 计划数据
            scene_type: 场景类型（family/friends/couple/solo）
        
        Returns:
            文本格式行程通知
        """
        logger.info(f"[NotificationTool] 生成文本通知 - 场景: {scene_type}")
        
        template = self.templates.get(scene_type, self.templates["friends"])
        greeting = template["greeting"]
        farewell = template["farewell"]
        
        title = plan.get("title", "周末活动计划")
        estimated_cost = plan.get("estimated_cost", "")
        
        # 构建时间安排部分
        schedule_lines = []
        if plan.get("schedule"):
            for item in plan["schedule"]:
                time = item.get("time", "")
                desc = item.get("description", "")
                if time and desc:
                    schedule_lines.append(f"⏰ {time} - {desc}")
        
        # 构建活动部分
        activity_lines = []
        if plan.get("activities"):
            for activity in plan["activities"]:
                name = activity.get("name", "")
                time = activity.get("time", "")
                location = activity.get("location", "")
                if name:
                    line = f"📍 {name}"
                    if time:
                        line += f" ({time})"
                    if location:
                        line += f"\n   地址: {location}"
                    activity_lines.append(line)
        
        # 构建餐饮部分
        restaurant_lines = []
        if plan.get("restaurants"):
            for restaurant in plan["restaurants"]:
                name = restaurant.get("name", "")
                time = restaurant.get("time", "")
                cuisine = restaurant.get("cuisine", "")
                price_range = restaurant.get("price_range", "")
                if name:
                    line = f"🍽️ {name}"
                    if time:
                        line += f" ({time})"
                    if cuisine:
                        line += f" · {cuisine}"
                    if price_range:
                        line += f" · {price_range}"
                    restaurant_lines.append(line)
        
        # 交通建议
        transportation = plan.get("transportation", "")
        
        # 组合所有内容
        parts = [greeting, "", f"📋 {title}", ""]
        
        if schedule_lines:
            parts.append("📅 时间安排:")
            parts.extend(schedule_lines)
            parts.append("")
        
        if activity_lines:
            parts.append("🎯 活动安排:")
            parts.extend(activity_lines)
            parts.append("")
        
        if restaurant_lines:
            parts.append("🍴 餐饮推荐:")
            parts.extend(restaurant_lines)
            parts.append("")
        
        if transportation:
            parts.append(f"🚗 交通建议: {transportation}")
            parts.append("")
        
        if estimated_cost:
            parts.append(f"💰 预估费用: {estimated_cost}")
            parts.append("")
        
        parts.append(farewell)
        
        text = "\n".join(parts)
        logger.info(f"[NotificationTool] 文本通知生成完成")
        return text
    
    @log_performance("notification.generate_html")
    def generate_html_notification(self, plan: dict, scene_type: str = "friends") -> str:
        """生成HTML格式行程通知
        
        Args:
            plan: 计划数据
            scene_type: 场景类型
        
        Returns:
            HTML格式行程通知
        """
        logger.info(f"[NotificationTool] 生成HTML通知 - 场景: {scene_type}")
        
        template = self.templates.get(scene_type, self.templates["friends"])
        
        title = plan.get("title", "周末活动计划")
        estimated_cost = plan.get("estimated_cost", "")
        transportation = plan.get("transportation", "")
        
        schedule_html = ""
        if plan.get("schedule"):
            rows = []
            for item in plan["schedule"]:
                rows.append(f'<tr><td>{item.get("time", "")}</td><td>{item.get("description", "")}</td></tr>')
            schedule_html = f"""
            <div class="section">
                <h3>📅 时间安排</h3>
                <table class="schedule-table">
                    <thead><tr><th>时间</th><th>安排</th></tr></thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </div>
            """
        
        activities_html = ""
        if plan.get("activities"):
            items = []
            for activity in plan["activities"]:
                items.append(f"""
                <div class="activity-card">
                    <h4>📍 {activity.get("name", "")}</h4>
                    <p>⏰ {activity.get("time", "")}</p>
                    <p>🏠 {activity.get("location", "")}</p>
                    <p>{activity.get("description", "")}</p>
                </div>
                """)
            activities_html = f"""
            <div class="section">
                <h3>🎯 活动安排</h3>
                <div class="activities-grid">
                    {''.join(items)}
                </div>
            </div>
            """
        
        restaurants_html = ""
        if plan.get("restaurants"):
            items = []
            for restaurant in plan["restaurants"]:
                items.append(f"""
                <div class="restaurant-card">
                    <h4>🍽️ {restaurant.get("name", "")}</h4>
                    <p>⏰ {restaurant.get("time", "")}</p>
                    <p>🏠 {restaurant.get("location", "")}</p>
                    <p>🍳 {restaurant.get("cuisine", "")} · 💵 {restaurant.get("price_range", "")}</p>
                </div>
                """)
            restaurants_html = f"""
            <div class="section">
                <h3>🍴 餐饮推荐</h3>
                <div class="restaurants-grid">
                    {''.join(items)}
                </div>
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .greeting {{ font-size: 1.2em; color: #666; }}
        .title {{ font-size: 1.5em; font-weight: bold; color: #333; margin-top: 10px; }}
        .section {{ margin-top: 20px; }}
        .section h3 {{ color: #333; margin-bottom: 10px; }}
        .schedule-table {{ width: 100%; border-collapse: collapse; }}
        .schedule-table th, .schedule-table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #eee; }}
        .activity-card, .restaurant-card {{ background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
        .activity-card h4, .restaurant-card h4 {{ margin: 0 0 8px 0; color: #333; }}
        .activity-card p, .restaurant-card p {{ margin: 4px 0; color: #666; font-size: 0.9em; }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; }}
        .cost {{ font-weight: bold; color: #e74c3c; }}
        .transport {{ color: #3498db; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="greeting">{template["greeting"]}</div>
            <div class="title">{title}</div>
        </div>
        {schedule_html}
        {activities_html}
        {restaurants_html}
        <div class="section">
            {f'<p class="transport">🚗 {transportation}</p>' if transportation else ''}
            {f'<p class="cost">💰 预估费用: {estimated_cost}</p>' if estimated_cost else ''}
        </div>
        <div class="footer">{template["farewell"]}</div>
    </div>
</body>
</html>"""
        
        logger.info(f"[NotificationTool] HTML通知生成完成")
        return html
    
    @log_performance("notification.generate_markdown")
    def generate_markdown_notification(self, plan: dict, scene_type: str = "friends") -> str:
        """生成Markdown格式行程通知
        
        Args:
            plan: 计划数据
            scene_type: 场景类型
        
        Returns:
            Markdown格式行程通知
        """
        logger.info(f"[NotificationTool] 生成Markdown通知 - 场景: {scene_type}")
        
        template = self.templates.get(scene_type, self.templates["friends"])
        
        title = plan.get("title", "周末活动计划")
        plan_id = plan.get("plan_id", "")
        
        md = f"""# {template["greeting"]}

## 📋 {title}
{"**计划ID:** " + plan_id if plan_id else ""}

"""
        
        if plan.get("schedule"):
            md += "## 📅 时间安排\n\n"
            md += "| 时间 | 安排 |\n|------|------|\n"
            for item in plan["schedule"]:
                md += f"| {item.get('time', '')} | {item.get('description', '')} |\n"
            md += "\n"
        
        if plan.get("activities"):
            md += "## 🎯 活动安排\n\n"
            for activity in plan["activities"]:
                md += f"### 📍 {activity.get('name', '')}\n"
                md += f"- ⏰ 时间: {activity.get('time', '')}\n"
                md += f"- 🏠 地点: {activity.get('location', '')}\n"
                if activity.get('description'):
                    md += f"- 📝 描述: {activity.get('description')}\n"
                md += "\n"
        
        if plan.get("restaurants"):
            md += "## 🍴 餐饮推荐\n\n"
            for restaurant in plan["restaurants"]:
                md += f"### 🍽️ {restaurant.get('name', '')}\n"
                md += f"- ⏰ 时间: {restaurant.get('time', '')}\n"
                md += f"- 🏠 地点: {restaurant.get('location', '')}\n"
                md += f"- 🍳 菜系: {restaurant.get('cuisine', '')}\n"
                md += f"- 💵 价位: {restaurant.get('price_range', '')}\n"
                md += "\n"
        
        if plan.get("transportation"):
            md += f"## 🚗 交通建议\n\n{plan['transportation']}\n\n"
        
        if plan.get("estimated_cost"):
            md += f"## 💰 预估费用\n\n{plan['estimated_cost']}\n\n"
        
        md += f"---\n\n{template['farewell']}"
        
        logger.info(f"[NotificationTool] Markdown通知生成完成")
        return md
    
    @log_performance("notification.generate_social_share")
    def generate_social_share(self, plan: dict, scene_type: str = "friends") -> str:
        """生成社交媒体分享文案（适合微信、朋友圈等）
        
        Args:
            plan: 计划数据
            scene_type: 场景类型
        
        Returns:
            社交媒体分享文案
        """
        logger.info(f"[NotificationTool] 生成社交分享文案 - 场景: {scene_type}")
        
        template = self.templates.get(scene_type, self.templates["friends"])
        
        title = plan.get("title", "周末计划")
        estimated_cost = plan.get("estimated_cost", "")
        
        activities = plan.get("activities", [])
        restaurants = plan.get("restaurants", [])
        
        main_activity = activities[0]["name"] if activities else "活动"
        main_restaurant = restaurants[0]["name"] if restaurants else "餐厅"
        
        share_text = f"""{template["greeting"]}

📅 {title}

{template["farewell"]}
"""
        
        if activities:
            share_text += f"""
🎯 今日安排:
{activities[0]["name"]} ({activities[0].get("time", "")})
📍 {activities[0].get("location", "")}
"""
        
        if restaurants:
            share_text += f"""
🍴 美食推荐:
{restaurants[0]["name"]}
🍳 {restaurants[0].get("cuisine", "")} · 💵 {restaurants[0].get("price_range", "")}
"""
        
        if estimated_cost:
            share_text += f"""
💰 预估: {estimated_cost}
"""
        
        share_text += "\n👉 点击查看详情"
        
        logger.info(f"[NotificationTool] 社交分享文案生成完成")
        return share_text
    
    @log_performance("notification.generate_sms")
    def generate_sms_notification(self, plan: dict) -> str:
        """生成短信格式通知（简洁版）
        
        Args:
            plan: 计划数据
        
        Returns:
            短信格式通知
        """
        logger.info(f"[NotificationTool] 生成短信通知")
        
        title = plan.get("title", "活动计划")
        activities = plan.get("activities", [])
        
        if activities:
            activity = activities[0]
            sms = f"【活动提醒】{title}：{activity.get('name', '')}，{activity.get('time', '')}，{activity.get('location', '')}"
        else:
            sms = f"【活动提醒】{title}已生成，请查看详情"
        
        logger.info(f"[NotificationTool] 短信通知生成完成")
        return sms
