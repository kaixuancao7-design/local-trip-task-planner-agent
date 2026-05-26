"""测试DeepSeek模型配置"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.planner import PlanningAgent
from config.settings import settings


def test_deepseek_config():
    """测试DeepSeek配置"""
    print("="*60)
    print("测试DeepSeek模型配置")
    print("="*60)
    
    print(f"LLM提供商: {settings.llm_provider}")
    print(f"LLM模型: {settings.llm_model}")
    print(f"API基础URL: {settings.deepseek_api_base}")
    print(f"API密钥已配置: {'是' if settings.deepseek_api_key and settings.deepseek_api_key != 'your_deepseek_api_key' else '否'}")
    
    if settings.deepseek_api_key == 'your_deepseek_api_key':
        print("\n⚠️  警告: 请在 .env 文件中配置您的DeepSeek API密钥")
        print("格式: DEEPSEEK_API_KEY=your_actual_api_key")
        return False
    
    return True


def test_llm_inference():
    """测试LLM推理"""
    print("\n" + "="*60)
    print("测试LLM推理")
    print("="*60)
    
    agent = PlanningAgent()
    
    try:
        # 测试简单推理
        result = agent._parse_scene_constraints_llm("周末带孩子出去玩")
        print(f"推理成功!")
        print(f"场景类型: {result.get('scene_info', {}).get('scene_type')}")
        print(f"场景名称: {result.get('scene_info', {}).get('scene_name')}")
        print(f"人数: {result.get('scene_info', {}).get('people_count')}")
        return True
    except Exception as e:
        print(f"推理失败: {e}")
        return False


def main():
    """主测试函数"""
    # 检查配置
    config_ok = test_deepseek_config()
    
    if not config_ok:
        print("\n请先配置DeepSeek API密钥")
        return
    
    # 测试LLM推理
    test_llm_inference()


if __name__ == "__main__":
    main()
