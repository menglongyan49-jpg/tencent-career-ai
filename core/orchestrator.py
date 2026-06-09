"""
增强版 Agent 调度器 - 支持多Agent协作
"""
from typing import Optional, Dict, Any, AsyncGenerator, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from config import get_config, GRADE_CONFIGS, PERSONALITY_CONFIGS

from agents.memory_router import MemoryRouter
from agents.career_navigator import CareerNavigator
from agents.emotional_supporter import EmotionalSupporter
from agents.interview_coach import InterviewCoach
from agents.tencent_expert import TencentExpert
from core.memory import MemoryManager


class Orchestrator:
    """增强版 Agent 调度器 - 支持多Agent协作"""

    # Agent 信息（用于UI展示）
    AGENT_INFO = {
        "career_navigator": {
            "name": "战术导航导师",
            "icon": "🧭",
            "description": "专注职业路径规划和技术能力对标",
            "color": "#4CAF50",
        },
        "emotional_supporter": {
            "name": "情绪树洞",
            "icon": "💝",
            "description": "温柔倾听，情绪疏导",
            "color": "#E91E63",
        },
        "interview_coach": {
            "name": "面试教练",
            "icon": "🎯",
            "description": "模拟面试场景，提升求职技巧",
            "color": "#FF9800",
        },
        "tencent_expert": {
            "name": "鹅厂专家",
            "icon": "🐧",
            "description": "腾讯业务、文化、岗位深度解读",
            "color": "#2196F3",
        },
    }

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

        # 当前活跃Agent（用于UI展示）
        self.current_agent: str = "career_navigator"
        self.agent_collaboration: List[str] = []  # 协作的Agent列表

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

    async def smart_routing(self, message: str, context: Dict) -> Dict[str, Any]:
        """智能路由 - 使用LLM进行意图分析"""

        # 首先检查是否是切换Agent的请求
        switch_keywords = {
            "鹅厂专家": "tencent_expert",
            "腾讯专家": "tencent_expert",
            "企鹅专家": "tencent_expert",
            "面试教练": "interview_coach",
            "面试官": "interview_coach",
            "面试导师": "interview_coach",
            "情绪树洞": "emotional_supporter",
            "情绪支持": "emotional_supporter",
            "心理导师": "emotional_supporter",
            "战术导师": "career_navigator",
            "职业导师": "career_navigator",
            "导航导师": "career_navigator",
            "全能导师": "career_navigator",
        }

        message_lower = message.lower()
        for keyword, agent_id in switch_keywords.items():
            if keyword in message and ("切换" in message or "转换" in message or "换成" in message or "变成" in message or "用" in message):
                return {
                    "primary_agent": agent_id,
                    "secondary_agents": [],
                    "intent": "切换Agent",
                    "emotion": "normal",
                    "emotion_intensity": 0,
                    "reasoning": f"用户请求切换到{keyword}",
                    "is_switch": True,
                }

        routing_prompt = f"""分析用户消息，判断应该由哪个专家Agent来回应。

用户消息: {message}

用户背景:
- 年级: {context.get('grade_name', '大学生')}
- 专业: {context.get('major', '未知')}
- 目标: {context.get('target', '未设置')}

可选的专家Agent:
1. career_navigator (战术导航导师) - 职业规划、技术学习、能力提升
2. emotional_supporter (情绪树洞) - 情绪倾诉、压力疏导、心理支持
3. interview_coach (面试教练) - 面试准备、简历优化、模拟面试
4. tencent_expert (鹅厂专家) - 腾讯业务、岗位解读、企业文化

请以JSON格式返回分析结果:
{{
    "primary_agent": "主要负责的agent名称",
    "secondary_agents": ["辅助协作的agent列表"],
    "intent": "用户意图描述",
    "emotion": "情绪状态(normal/anxious/frustrated/excited)",
    "emotion_intensity": 0.0-1.0,
    "reasoning": "路由理由"
}}

只返回JSON，不要其他内容。"""

        try:
            response = await self.llm.ainvoke([HumanMessage(content=routing_prompt)])
            import json
            # 尝试解析JSON
            content = response.content
            # 提取JSON部分
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            return result
        except Exception as e:
            # 降级到关键词路由
            return self.memory_router.route(message, context)

    async def process(
        self,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理用户消息 - 支持多Agent协作"""

        # 1. 准备基础上下文
        base_context = self._build_context(user_profile, {})

        # 2. 智能路由分析
        routing_result = await self.smart_routing(message, base_context)

        # 3. 更新记忆
        if self.memory_manager:
            entities = routing_result.get("entities", {})
            if entities.get("skills"):
                await self.memory_manager.update_skills(entities["skills"], message)

            emotion = routing_result.get("emotion", "normal")
            emotion_intensity = routing_result.get("emotion_intensity", 0)
            if emotion_intensity >= 0.3:
                await self.memory_manager.record_emotion(emotion, emotion_intensity, message)

        # 4. 确定主Agent和协作Agent
        primary_agent_name = routing_result.get("primary_agent", "career_navigator")
        secondary_agents = routing_result.get("secondary_agents", [])
        is_switch = routing_result.get("is_switch", False)

        # 验证agent名称有效性
        valid_agents = ["career_navigator", "emotional_supporter", "interview_coach", "tencent_expert"]
        if primary_agent_name not in valid_agents:
            primary_agent_name = "career_navigator"
        secondary_agents = [a for a in secondary_agents if a in valid_agents]

        self.current_agent = primary_agent_name
        self.agent_collaboration = secondary_agents

        # 5. 准备完整上下文
        context = self._build_context(user_profile, routing_result)
        if self.memory_manager:
            context["memory_context"] = self.memory_manager.get_context_for_prompt()
            context["emotion_trend"] = self.memory_manager.get_emotion_trend()

        # 6. 获取主Agent
        primary_agent = self.agents.get(primary_agent_name, self.career_navigator)

        # 6.5 如果是切换Agent请求，生成切换确认消息
        if is_switch:
            agent_info = self.AGENT_INFO.get(primary_agent_name, {})
            switch_response = f"""好的，已收到切换指令。现在我将以 **{agent_info.get('icon', '🤖')} {agent_info.get('name', 'AI助手')}** 的身份与你对话。

{agent_info.get('description', '')}

请告诉我你想了解什么？"""
            yield switch_response
            return

        # 7. 如果需要协作，先收集协作Agent的输入
        collaboration_context = ""
        if secondary_agents:
            collaboration_context = await self._gather_collaboration(
                message, context, secondary_agents
            )
            context["collaboration_input"] = collaboration_context

        # 8. 流式输出响应
        response_text = ""
        async for chunk in primary_agent.process(message, context, history):
            response_text += chunk
            yield chunk

        # 9. 保存对话记录
        if self.memory_manager:
            await self.memory_manager.add_short_term(message, response_text, {
                "emotion": routing_result.get("emotion"),
                "primary_agent": primary_agent_name,
                "collaboration_agents": secondary_agents,
            })

    async def _gather_collaboration(
        self,
        message: str,
        context: Dict,
        secondary_agents: List[str]
    ) -> str:
        """收集协作Agent的输入"""
        collaboration_inputs = []

        for agent_name in secondary_agents[:2]:  # 最多2个协作Agent
            agent = self.agents.get(agent_name)
            if agent:
                # 让协作Agent提供简短建议
                collab_prompt = f"""作为协作专家，请针对用户问题提供简短的专业建议（50字以内）：
用户问题: {message}
你的角色: {self.AGENT_INFO.get(agent_name, {}).get('name', agent_name)}"""

                try:
                    response = await self.llm.ainvoke([
                        SystemMessage(content=agent.build_system_prompt(agent.SYSTEM_PROMPT if hasattr(agent, 'SYSTEM_PROMPT') else "")),
                        HumanMessage(content=collab_prompt)
                    ])
                    collaboration_inputs.append({
                        "agent": agent_name,
                        "agent_name": self.AGENT_INFO.get(agent_name, {}).get('name', agent_name),
                        "suggestion": response.content[:100],
                    })
                except:
                    pass

        if collaboration_inputs:
            return "\n".join([
                f"[{inp['agent_name']}建议]: {inp['suggestion']}"
                for inp in collaboration_inputs
            ])
        return ""

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
            "emotion": routing_result.get("emotion", "normal"),
            "emotion_intensity": routing_result.get("emotion_intensity", 0),
            "intents": routing_result.get("intent", ""),
            "routing_reason": routing_result.get("reasoning", ""),
        })

        return context

    def get_current_agent_info(self) -> Dict[str, Any]:
        """获取当前活跃Agent信息（用于UI展示）"""
        info = self.AGENT_INFO.get(self.current_agent, self.AGENT_INFO["career_navigator"])
        info["agent_id"] = self.current_agent
        info["collaboration"] = [
            self.AGENT_INFO.get(a, {}).get("name", a)
            for a in self.agent_collaboration
        ]
        return info

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

**我的专家团队随时为你服务：**

🧭 **战术导航导师** - 职业路径规划、技术能力对标
💝 **情绪树洞** - 温柔倾听、情绪疏导
🎯 **面试教练** - 面试模拟、简历优化
🐧 **鹅厂专家** - 腾讯业务解读、岗位分析

有什么想聊的吗？"""