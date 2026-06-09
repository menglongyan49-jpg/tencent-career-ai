"""
Agent 调度器 - Orchestrator
负责协调多个 Agent 之间的工作流
"""
from typing import Optional, Dict, Any, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from config import get_config, GRADE_CONFIGS, PERSONALITY_CONFIGS

from agents.memory_router import MemoryRouter
from agents.career_navigator import CareerNavigator
from agents.emotional_supporter import EmotionalSupporter
from agents.interview_coach import InterviewCoach
from agents.tencent_expert import TencentExpert
from core.memory import MemoryManager


class Orchestrator:
    """Agent 调度器"""

    def __init__(self, user_id: str, personality: str = "全能导师"):
        self.user_id = user_id
        self.personality = personality
        self.config = get_config()

        # 初始化 LLM
        self.llm = self._init_llm()

        # 初始化 Agents
        self.memory_router = MemoryRouter(self.llm, personality)
        self.career_navigator = CareerNavigator(self.llm, personality)
        self.emotional_supporter = EmotionalSupporter(self.llm, personality)
        self.interview_coach = InterviewCoach(self.llm, personality)
        self.tencent_expert = TencentExpert(self.llm, personality)

        # Agent 映射
        self.agents = {
            "memory_router": self.memory_router,
            "career_navigator": self.career_navigator,
            "emotional_supporter": self.emotional_supporter,
            "interview_coach": self.interview_coach,
            "tencent_expert": self.tencent_expert,
        }

        # 记忆管理器
        self.memory_manager: Optional[MemoryManager] = None

    def _init_llm(self):
        """初始化大模型"""
        import os
        if self.config.llm_provider == "anthropic":
            return ChatAnthropic(
                model=self.config.llm_model,
                temperature=0.7,
                streaming=True,
            )
        elif self.config.llm_provider == "openai":
            return ChatOpenAI(
                model=self.config.llm_model,
                temperature=0.7,
                streaming=True,
                openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")

    def set_memory_manager(self, memory_manager: MemoryManager):
        """设置记忆管理器"""
        self.memory_manager = memory_manager

    def update_personality(self, personality: str):
        """更新所有 Agent 的性格"""
        self.personality = personality
        for agent in self.agents.values():
            agent.update_personality(personality)

    async def process(
        self,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理用户消息"""

        # 1. 路由分析
        routing_result = await self.memory_router.process(message)

        # 2. 更新记忆（使用增强版记忆系统）
        if self.memory_manager:
            # 提取实体并更新技能
            entities = routing_result.get("entities", {})
            if entities.get("skills"):
                await self.memory_manager.update_skills(entities["skills"], message)

            # 记录情绪事件
            emotion = routing_result.get("emotion", "neutral")
            emotion_score = routing_result.get("emotion_score", 0)
            if emotion_score >= 0.3:
                await self.memory_manager.record_emotion(emotion, emotion_score, message)

            # 添加知识节点
            if entities.get("topics"):
                for topic in entities["topics"]:
                    await self.memory_manager.add_knowledge_node(topic, "topic", [])

        # 3. 准备上下文（融入长期记忆）
        context = self._build_context(user_profile, routing_result)

        # 添加记忆上下文
        if self.memory_manager:
            context["memory_context"] = self.memory_manager.get_context_for_prompt()
            context["emotion_trend"] = self.memory_manager.get_emotion_trend()

        # 4. 路由到对应 Agent
        target_agent_name = routing_result["target_agent"]
        target_agent = self.agents.get(target_agent_name, self.career_navigator)

        # 5. 流式输出响应
        response_text = ""
        async for chunk in target_agent.process(message, context, history):
            response_text += chunk
            yield chunk

        # 6. 保存对话记录到短期记忆
        if self.memory_manager:
            await self.memory_manager.add_short_term(message, response_text, {
                "emotion": routing_result.get("emotion"),
                "agent": target_agent_name,
            })

    def _build_context(
        self,
        user_profile: Optional[Dict[str, Any]],
        routing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建上下文"""
        context = {}

        if user_profile:
            grade = user_profile.get("grade", "freshman")
            grade_config = GRADE_CONFIGS.get(grade, {})
            context.update({
                "grade": grade,
                "grade_name": grade_config.get("name", "大学生"),
                "stage": grade_config.get("stage", ""),
                "major": user_profile.get("major", ""),
                "target": user_profile.get("target", ""),
                "interests": user_profile.get("interests", []),
                "skills": user_profile.get("skills", []),
            })

        context.update({
            "emotion": routing_result.get("emotion", "neutral"),
            "emotion_score": routing_result.get("emotion_score", 0),
            "intents": routing_result.get("intents", []),
        })

        return context

    def get_welcome_message(self, user_profile: Dict[str, Any]) -> str:
        """生成欢迎语"""
        personality_config = PERSONALITY_CONFIGS.get(
            self.personality, PERSONALITY_CONFIGS["全能导师"]
        )
        grade = user_profile.get("grade", "freshman")
        grade_config = GRADE_CONFIGS.get(grade, {})
        nickname = user_profile.get("nickname", "同学")

        return f"""你好，{nickname}！🦆

我是你的专属成长伙伴「未来鹅」，很高兴认识你！

我看到你是{grade_config.get('name', '大学生')}，正处于**{grade_config.get('stage', '成长期')}**。

{personality_config['example']}

我可以帮你：
- 🎯 规划职业发展路径
- 💼 准备简历和面试
- 🏢 了解腾讯和互联网行业
- 💡 解答各种职业困惑

有什么想聊的吗？"""