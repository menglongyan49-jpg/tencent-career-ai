"""
Agent 基类
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import PERSONALITY_CONFIGS


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(
        self,
        name: str,
        llm,
        personality: str = "全能导师",
        system_prompt: str = "",
    ):
        self.name = name
        self.llm = llm
        self.personality = personality
        self.system_prompt = system_prompt
        self.personality_config = PERSONALITY_CONFIGS.get(personality, PERSONALITY_CONFIGS["全能导师"])

    def build_system_prompt(self, base_prompt: str) -> str:
        """构建带性格的系统提示词"""
        personality_style = self.personality_config["style"]
        personality_tone = self.personality_config["tone"]
        personality_emoji = self.personality_config["emoji_usage"]

        return f"""{base_prompt}

## 你的性格设定
- 沟通风格：{personality_style}
- 语言基调：{personality_tone}
- Emoji使用：{personality_emoji}

请始终保持这个性格设定，让对话自然流畅。
"""

    @abstractmethod
    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应"""
        pass

    def _create_chain(self, system_prompt: str):
        """创建对话链"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content="{input}"),
        ])
        return prompt | self.llm

    def update_personality(self, personality: str):
        """更新性格设定"""
        self.personality = personality
        self.personality_config = PERSONALITY_CONFIGS.get(personality, PERSONALITY_CONFIGS["全能导师"])