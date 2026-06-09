"""
战术导航导师 - Career Navigator Agent
专注于硬核求职路径设计和技术能力对标
支持实时搜索获取最新技术趋势和岗位需求
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent
from tools.web_search import get_search_tool, WebSearchTool


class CareerNavigator(BaseAgent):
    """战术导航导师 - 支持实时技术趋势搜索"""

    # 需要实时搜索的关键词
    REALTIME_KEYWORDS = [
        "最新", "今年", "2024", "2025", "2026", "最近",
        "趋势", "前景", "发展", "未来", "行情",
        "热门", "需求", "缺口", "就业",
        "薪资", "待遇", "offer",
        "学什么", "技术栈", "方向",
        "大厂", "互联网",
    ]

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

### 4. 实时行业情报
- 当提供实时搜索结果时，分析最新技术趋势
- 告知用户当前热门方向和市场需求
- 对比往年变化，帮助用户把握职业方向

## 回答框架
1. **现状分析**：评估学生当前的能力水平
2. **差距识别**：对比目标岗位的核心要求
3. **行动建议**：给出具体可执行的提升方案
4. **资源推荐**：推荐学习资源和实践方向

## 实时信息使用原则
当用户提供实时搜索结果时：
- 分析当前技术趋势和热门方向
- 告知用户目标岗位的市场需求和薪资水平
- 对比往年变化，指出需要重点学习的技术
- 结合实时行情给出职业规划建议

## 注意事项
- 保持专业但不生硬
- 用数据和案例支撑观点
- 鼓励学生持续进步"""

    def __init__(self, llm, personality: str = "全能导师"):
        super().__init__("CareerNavigator", llm, personality, self.SYSTEM_PROMPT)
        self.search_tool: WebSearchTool = get_search_tool("auto")

    def _needs_realtime_search(self, message: str) -> bool:
        """判断是否需要实时搜索"""
        message_lower = message.lower()
        return any(kw in message_lower for kw in self.REALTIME_KEYWORDS)

    def _search_realtime_info(self, message: str, context: Optional[Dict] = None) -> str:
        """搜索实时职业/技术信息"""
        # 根据用户背景构建搜索查询
        target = context.get("target", "") if context else ""
        interests = context.get("interests", []) if context else []

        queries = []

        # 根据问题类型构建不同查询
        if "薪资" in message or "待遇" in message or "offer" in message:
            queries.append(f"{target or '互联网'} 校招 薪资 2025")
            queries.append(f"{target or '后端开发'} 应届生 薪资行情")

        if "趋势" in message or "前景" in message or "发展" in message:
            queries.append("互联网 技术趋势 2025")
            queries.append(f"{target or '程序员'} 职业发展 前景")

        if "学什么" in message or "技术栈" in message:
            queries.append(f"{target or '后端开发'} 技术栈 2025")
            queries.append("大厂 技术要求 最新")

        if "就业" in message or "需求" in message:
            queries.append("互联网 就业形势 2025")
            queries.append(f"{target or '技术岗'} 招聘需求")

        # 默认搜索
        if not queries:
            queries.append(f"{target} 职业发展 2025" if target else "互联网 职业规划 2025")

        all_results = []
        for query in queries[:2]:
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

## 实时行业情报（来自网络搜索）
{search_results}

请结合以上实时信息，分析当前行业趋势，给用户最新的职业规划建议。
"""

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