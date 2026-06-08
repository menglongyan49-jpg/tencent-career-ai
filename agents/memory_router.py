"""
记忆路由管家 - Memory Router Agent
负责意图识别、情绪检测、任务分发和记忆更新
"""
from typing import Optional, Dict, Any, List, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from config import ANXIETY_KEYWORDS, INTENT_KEYWORDS
from agents.base_agent import BaseAgent


class MemoryRouter(BaseAgent):
    """记忆路由管家"""

    ROUTING_RULES = {
        "emotion": "emotional_supporter",  # 情绪问题 → 情绪树洞
        "interview": "interview_coach",    # 面试问题 → 面试教练
        "tencent": "tencent_expert",       # 腾讯问题 → 鹅厂专家
        "career": "career_navigator",      # 职业问题 → 战术导师
        "technical": "career_navigator",   # 技术问题 → 战术导师
    }

    def __init__(self, llm, personality: str = "全能导师"):
        system_prompt = """你是「未来鹅」系统的记忆路由管家，负责：
1. 分析用户输入的意图
2. 检测用户情绪状态
3. 提取关键信息更新记忆
4. 将请求路由给合适的专业 Agent

你的输出是结构化的 JSON，不要直接回复用户。"""
        super().__init__("MemoryRouter", llm, personality, system_prompt)

    def detect_emotion(self, message: str) -> Tuple[str, float]:
        """检测情绪状态"""
        message_lower = message.lower()
        anxiety_count = sum(1 for kw in ANXIETY_KEYWORDS if kw in message_lower)

        if anxiety_count >= 2:
            return "anxious", 0.8
        elif anxiety_count == 1:
            return "slightly_anxious", 0.5
        return "neutral", 0.0

    def classify_intent(self, message: str) -> List[str]:
        """分类意图"""
        message_lower = message.lower()
        intents = []

        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                intents.append(intent)

        return intents if intents else ["general"]

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """提取关键实体"""
        entities = {}

        # 简单的关键词提取（实际项目中可使用 NER 模型）
        tech_keywords = ["Python", "Java", "Go", "React", "Vue", "算法", "后端", "前端", "产品"]
        for kw in tech_keywords:
            if kw.lower() in message.lower():
                entities.setdefault("skills", []).append(kw)

        return entities

    def route(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """路由决策"""
        # 情绪检测
        emotion, emotion_score = self.detect_emotion(message)

        # 意图分类
        intents = self.classify_intent(message)

        # 实体提取
        entities = self.extract_entities(message)

        # 路由决策
        # 如果情绪焦虑程度高，优先路由给情绪树洞
        if emotion_score >= 0.7:
            target_agent = "emotional_supporter"
            reason = "检测到高焦虑情绪，优先进行情绪疏导"
        else:
            # 根据意图路由
            for intent in intents:
                if intent in self.ROUTING_RULES:
                    target_agent = self.ROUTING_RULES[intent]
                    reason = f"检测到意图: {intent}"
                    break
            else:
                target_agent = "career_navigator"
                reason = "默认路由到战术导师"

        return {
            "emotion": emotion,
            "emotion_score": emotion_score,
            "intents": intents,
            "entities": entities,
            "target_agent": target_agent,
            "reason": reason,
        }

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """处理消息，返回路由信息"""
        return self.route(message, context)