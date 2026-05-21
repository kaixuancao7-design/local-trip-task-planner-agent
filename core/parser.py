"""感知层 - 用户输入解析器

负责解析用户自然语言指令，提取关键实体和意图。
"""
from langchain_core.prompts import PromptTemplate
import json
from config.settings import settings
from config.logging_config import logger

class InputParser:
    """用户输入解析器"""
    
    def __init__(self):
        self._llm = None
    
    @property
    def llm(self):
        """懒加载LLM模型"""
        if self._llm is None:
            from langchain_ollama import OllamaLLM
            self._llm = OllamaLLM(model=settings.llm_model, temperature=settings.llm_temperature)
        return self._llm
    
    def parse(self, user_input: str) -> dict:
        """解析用户输入，提取关键实体"""
        logger.info(f"[InputParser] 开始解析用户输入 - 输入长度: {len(user_input)}")
        logger.debug(f"[InputParser] 用户输入内容: {user_input}")
        
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""请从以下用户输入中提取关键实体，以JSON格式输出：
            用户输入：{user_input}
            输出格式：{{"地点": "", "活动": "", "餐饮": "", "关系": "", "时间": "", "预算": "", "人数": ""}}"""
        )
        
        logger.debug("[InputParser] 调用LLM进行实体提取...")
        chain = prompt | self.llm
        result = chain.invoke({"user_input": user_input})
        logger.debug(f"[InputParser] LLM返回结果: {result}")
        
        try:
            parsed = json.loads(result)
            logger.info(f"[InputParser] 实体提取成功 - 地点: {parsed.get('地点')}, 活动: {parsed.get('活动')}")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"[InputParser] 实体提取解析失败，返回默认值 - 错误: {e}")
            return {
                "地点": "",
                "活动": "",
                "餐饮": "",
                "关系": "",
                "时间": "",
                "预算": "",
                "人数": ""
            }
    
    def extract_intent(self, user_input: str) -> str:
        """提取用户意图"""
        logger.info(f"[InputParser] 开始提取用户意图")
        
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""请分析用户输入的意图，返回以下之一：
            - plan: 规划活动
            - query: 查询信息
            - confirm: 确认执行
            - cancel: 取消计划
            - update: 更新偏好
            
            用户输入：{user_input}"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"user_input": user_input})
        intent = result.strip().lower()
        
        logger.info(f"[InputParser] 意图提取成功 - 意图: {intent}")
        return intent