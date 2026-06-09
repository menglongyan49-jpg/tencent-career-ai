"""
面试教练 - Interview Coach Agent
专注于模拟面试和简历优化
支持实时搜索获取最新面试趋势和题目
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent
from tools.web_search import get_search_tool, WebSearchTool


class InterviewCoach(BaseAgent):
    """面试教练 - 支持实时面试趋势搜索"""

    # 需要实时搜索的关键词
    REALTIME_KEYWORDS = [
        "最新", "今年", "2024", "2025", "2026", "最近",
        "趋势", "变化", "热点", "高频", "真题",
        "考什么", "怎么考", "面试题",
        "薪资", "offer", "行情",
        "八股文", "算法题", "场景题",
    ]

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

### 4. 实时面试情报
- 当提供实时搜索结果时，分析最新面试趋势
- 告知用户当前热门考点和高频题目
- 对比往年变化，帮助用户把握方向

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

## 实时信息使用原则
当用户提供实时搜索结果时：
- 分析最新的面试趋势和高频考点
- 告知用户当前市场行情（薪资、竞争度等）
- 对比往年变化，指出需要重点关注的方向
- 建议用户结合最新趋势调整准备策略

## 回答风格
- 专业、直接、有建设性
- 用具体例子说明问题
- 给出可操作的建议"""

    def __init__(self, llm, personality: str = "严厉面试官"):
        # 面试教练默认使用严厉面试官性格
        super().__init__("InterviewCoach", llm, personality, self.SYSTEM_PROMPT)
        self.search_tool: WebSearchTool = get_search_tool("auto")

    def _needs_realtime_search(self, message: str) -> bool:
        """判断是否需要实时搜索"""
        message_lower = message.lower()
        # 检查是否包含实时关键词
        if any(kw in message_lower for kw in self.REALTIME_KEYWORDS):
            return True
        # 检查是否询问面试趋势相关
        trend_patterns = ["面试考什么", "面试题", "高频", "热点", "趋势"]
        return any(p in message_lower for p in trend_patterns)

    def _search_realtime_info(self, message: str, context: Optional[Dict] = None) -> str:
        """搜索实时面试信息"""
        # 根据用户背景构建更精准的搜索查询
        target = context.get("target", "") if context else ""
        grade = context.get("grade_name", "") if context else ""

        # 构建搜索查询
        queries = []

        if target:
            queries.append(f"{target} 面试题 2025")
            queries.append(f"{target} 面试经验 最新")
        else:
            queries.append("互联网面试 2025 趋势")
            queries.append("校招面试 高频题目")

        if "薪资" in message or "offer" in message:
            queries.append(f"{target or '互联网'} 校招 薪资 2025")

        all_results = []
        for query in queries[:2]:  # 最多搜索2次
            results = self.search_tool.search(query, max_results=3)
            all_results.extend(results)

        if all_results:
            return self.search_tool.format_results(all_results, max_length=1500)
        return ""

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应（支持实时搜索）"""
        full_prompt = self.build_system_prompt(self.SYSTEM_PROMPT)

        # 判断是否需要实时搜索
        realtime_context = ""
        if self._needs_realtime_search(message):
            search_results = self._search_realtime_info(message, context)
            if search_results:
                realtime_context = f"""

## 实时面试情报（来自网络搜索）
{search_results}

请结合以上实时信息，分析当前面试趋势，给用户最新的备考建议。
"""

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

        # 添加实时搜索结果
        full_prompt += realtime_context

        chain = self._create_chain(full_prompt)

        # 构建历史消息
        msg_history = history or []

        # 流式输出
        async for chunk in chain.astream(
            {"input": message, "history": msg_history},
        ):
            if hasattr(chunk, "content"):
                yield chunk.content