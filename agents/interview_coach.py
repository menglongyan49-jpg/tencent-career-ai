"""
面试教练 - Interview Coach Agent
专注于模拟面试和简历优化
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent


class InterviewCoach(BaseAgent):
    """面试教练"""

    SYSTEM_PROMPT = """你是「未来鹅」的面试教练，专注于帮助大学生提升求职技能。

## 你的核心能力

### 1. 简历优化
- 分析简历的优缺点
- 指出项目经历的描述问题
- 给出具体的优化建议

### 2. 模拟面试
- 根据岗位类型设计面试问题
- 追问细节，模拟真实面试压力
- 给出回答反馈和改进建议

### 3. 面试技巧
- 分享常见面试题型和解法
- 教授 STAR 法则等回答框架
- 指导行为面试和技术面试的准备

## 面试模拟模式
当用户要求模拟面试时：
1. 先了解目标岗位
2. 按真实面试流程提问
3. 追问细节，不轻易放过模糊回答
4. 面试结束后给出详细反馈

## 简历分析框架
1. **整体评价**：简历的总体印象
2. **亮点识别**：找出写得好的部分
3. **问题指出**：具体指出需要改进的地方
4. **优化建议**：给出重写示例

## 回答风格
- 专业、直接、有建设性
- 用具体例子说明问题
- 给出可操作的建议"""

    def __init__(self, llm, personality: str = "严厉面试官"):
        # 面试教练默认使用严厉面试官性格
        super().__init__("InterviewCoach", llm, personality, self.SYSTEM_PROMPT)

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应"""
        full_prompt = self.build_system_prompt(self.SYSTEM_PROMPT)

        # 添加面试上下文
        if context:
            interview_context = f"""
## 用户背景
- 目标岗位：{context.get('target', '未设置')}
- 年级：{context.get('grade_name', '未知')}
- 已有技能：{', '.join(context.get('skills', [])) or '未设置'}

请根据目标岗位调整面试问题和建议。
"""
            full_prompt += interview_context

        chain = self._create_chain(full_prompt)

        # 构建历史消息
        msg_history = history or []

        # 流式输出
        async for chunk in chain.astream(
            {"input": message, "history": msg_history},
        ):
            if hasattr(chunk, "content"):
                yield chunk.content