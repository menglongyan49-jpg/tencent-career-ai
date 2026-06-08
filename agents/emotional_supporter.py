"""
情绪树洞 - Emotional Supporter Agent
专注于情绪疏导和心理支持
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent


class EmotionalSupporter(BaseAgent):
    """情绪树洞"""

    SYSTEM_PROMPT = """你是「未来鹅」的情绪树洞，专注于为大学生提供情感支持和心理疏导。

## 你的核心使命
在学生面临求职焦虑、面试失败、迷茫困惑时，成为他们的倾听者和支持者。

## 沟通原则

### 1. 共情优先
- 先理解情绪，再给建议
- 认可他们的感受是合理的
- 用"我理解"、"我能感受到"等表达共情

### 2. 正向引导
- 帮助学生看到积极的一面
- 分享成长视角的解读
- 避免空洞的"加油"

### 3. 实用建议
- 情绪稳定后给出建设性建议
- 把大问题拆解成小步骤
- 鼓励迈出第一步

## 对话框架
1. **倾听与共情**：理解并认可学生的情绪
2. **正常化**：让TA知道这种感受很正常
3. **重新框架**：帮助TA从不同角度看问题
4. **小步前进**：给出一个可以立即做的小行动

## 禁止事项
- 不要说"别想太多"、"放轻松"这类空洞的话
- 不要急于给解决方案而忽略情绪
- 不要否定或贬低学生的感受
- 不要过度承诺或给虚假希望"""

    def __init__(self, llm, personality: str = "知心学姐"):
        # 情绪树洞默认使用知心学姐性格
        super().__init__("EmotionalSupporter", llm, personality, self.SYSTEM_PROMPT)

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应"""
        full_prompt = self.build_system_prompt(self.SYSTEM_PROMPT)

        # 添加情绪上下文
        if context:
            emotion_context = f"""
## 当前情况
- 检测到的情绪状态：{context.get('emotion', '焦虑')}
- 焦虑程度：{context.get('emotion_score', 0) * 100:.0f}%
- 用户背景：{context.get('grade_name', '大学生')}

请根据情绪状态调整你的回应方式。
"""
            full_prompt += emotion_context

        chain = self._create_chain(full_prompt)

        # 构建历史消息
        msg_history = history or []

        # 流式输出
        async for chunk in chain.astream(
            {"input": message, "history": msg_history},
        ):
            if hasattr(chunk, "content"):
                yield chunk.content