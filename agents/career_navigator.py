"""
战术导航导师 - Career Navigator Agent
专注于硬核求职路径设计和技术能力对标
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent


class CareerNavigator(BaseAgent):
    """战术导航导师"""

    SYSTEM_PROMPT = """你是「未来鹅」的战术导航导师，专注于帮助大学生规划职业发展路径。

## 你的核心能力

### 1. 能力对标分析
- 将学生的技能与真实岗位要求进行 Diff 对比
- 指出能力差距和提升方向
- 给出具体的学习建议

### 2. 职业路径规划
- 根据学生的年级和目标制定阶段性计划
- 推荐合适的项目实践方向
- 提供简历包装建议

### 3. 技术深度指导
- 解释技术在大厂的真实应用场景
- 指出面试中的高频考点
- 分享技术成长的方法论

## 回答框架
1. **现状分析**：评估学生当前的能力水平
2. **差距识别**：对比目标岗位的核心要求
3. **行动建议**：给出具体可执行的提升方案
4. **资源推荐**：推荐学习资源和实践方向

## 注意事项
- 保持专业但不生硬
- 用数据和案例支撑观点
- 鼓励学生持续进步"""

    def __init__(self, llm, personality: str = "全能导师"):
        super().__init__("CareerNavigator", llm, personality, self.SYSTEM_PROMPT)

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应"""
        full_prompt = self.build_system_prompt(self.SYSTEM_PROMPT)

        # 添加上下文信息
        if context:
            context_info = f"""
## 用户背景
- 年级：{context.get('grade_name', '未知')}
- 专业：{context.get('major', '未知')}
- 目标：{context.get('target', '未设置')}
- 兴趣：{', '.join(context.get('interests', [])) or '未设置'}
- 技能：{', '.join(context.get('skills', [])) or '未设置'}
"""
            full_prompt += context_info

        chain = self._create_chain(full_prompt)

        # 构建历史消息
        msg_history = history or []

        # 流式输出
        async for chunk in chain.astream(
            {"input": message, "history": msg_history},
        ):
            if hasattr(chunk, "content"):
                yield chunk.content