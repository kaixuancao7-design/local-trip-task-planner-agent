"""测试场景化规划功能"""
from core.planner import PlanningAgent

planner = PlanningAgent()

print("=== 测试1: 亲子场景 ===")
result = planner.generate_scene_plan(
    user_input="周末带5岁孩子出去玩半天，想吃健康餐",
    scene_type="family"
)
print(f"场景: {result['scene_info']['scene_name']}")
print(f"人数: {result['scene_info']['people_count']}")
print(f"评分: {result['plan']['score']}")
print(f"费用估算: {result['plan']['cost_estimate']}")
print(f"候选方案数: {len(result['candidates'])}")
print("行程步骤:")
for step in result['plan']['steps']:
    print(f"  - {step['start_time']}-{step['end_time']}: {step['name']} ({step['duration']}分钟)")
print()

print("=== 测试2: 好友聚会场景 ===")
result = planner.generate_scene_plan(
    user_input="周末和4个朋友一起聚会，想吃火锅",
    scene_type="friends"
)
print(f"场景: {result['scene_info']['scene_name']}")
print(f"人数: {result['scene_info']['people_count']}")
print(f"评分: {result['plan']['score']}")
print(f"费用估算: {result['plan']['cost_estimate']}")
print("行程步骤:")
for step in result['plan']['steps']:
    print(f"  - {step['start_time']}-{step['end_time']}: {step['name']}")
print()

print("=== 测试3: 自动场景识别 ===")
result = planner.generate_scene_plan(
    user_input="周末和女朋友约会，想找个浪漫的地方"
)
print(f"自动识别场景: {result['scene_info']['scene_name']}")
print(f"约束条件: {result['constraints']}")
print(f"方案标题: {result['plan']['title']}")
print()

print("=== 测试完成 ===")
