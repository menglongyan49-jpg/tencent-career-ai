"""
鹅厂专家 - Tencent Expert Agent
专注于腾讯业务、文化和岗位解读
支持实时网络搜索获取最新信息
"""
from typing import Optional, Dict, Any, AsyncGenerator, List
from agents.base_agent import BaseAgent
from tools.web_search import get_search_tool, WebSearchTool


class TencentExpert(BaseAgent):
    """鹅厂专家 - 支持实时信息搜索"""

    # 需要实时搜索的关键词
    REALTIME_KEYWORDS = [
        "校招", "招聘", "实习", "秋招", "春招", "暑期",
        "2024", "2025", "2026", "今年", "最新", "最近",
        "笔试", "面试时间", "offer", "薪资",
        "新闻", "动态", "变化", "调整",
    ]

    SYSTEM_PROMPT = """你是「未来鹅」的鹅厂专家，专注于为学生解答关于腾讯的一切问题。

## 你的知识范围

### 1. 业务板块
- **微信事业群 (WXG)**：微信、企业微信、微信支付、视频号
- **游戏事业群 (IEG)**：王者荣耀、和平精英、英雄联盟手游
- **云与智慧产业事业群 (CSIG)**：腾讯云、腾讯会议
- **平台与内容事业群 (PCG)**：QQ、腾讯视频、腾讯新闻
- **技术工程事业群 (TEG)**：AI Lab、优图实验室、基础架构

### 2. 企业文化
- 价值观：用户为本，科技向善
- 正直、进取、协作、创造
- 福利待遇、工作环境

### 3. 校招信息
- 暑期实习：3-5月开放
- 秋招：8-10月开放
- 春招：3-4月开放
- 面试流程：网申 → 笔试 → 技术面 → HR面 → offer

### 4. 岗位解读
- 技术类：后端、前端、算法、测试
- 产品类：产品经理、产品运营
- 设计类：UI/UX、视觉设计
- 游戏类：策划、开发、美术

## 实时信息使用原则
当用户提供实时搜索结果时：
- 优先引用搜索结果中的最新信息
- 标注信息来源，增加可信度
- 如搜索结果与知识库冲突，以搜索结果为准
- 提醒用户信息可能有变化，建议查看官网确认

## 回答原则
- 信息准确，来源权威
- 客观介绍，不夸大不贬低
- 结合学生背景给出针对性建议
- 传递腾讯的雇主品牌价值"""

    def __init__(self, llm, personality: str = "全能导师"):
        super().__init__("TencentExpert", llm, personality, self.SYSTEM_PROMPT)
        self.search_tool: WebSearchTool = get_search_tool("auto")

    def _needs_realtime_search(self, message: str) -> bool:
        """判断是否需要实时搜索"""
        message_lower = message.lower()
        return any(kw in message_lower for kw in self.REALTIME_KEYWORDS)

    def _search_realtime_info(self, message: str) -> str:
        """搜索实时信息"""
        # 构建搜索查询
        search_queries = [
            f"腾讯 {message}",
            f"腾讯校招 2025",
        ]

        all_results = []
        for query in search_queries[:1]:  # 只搜索一次，避免过多请求
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
            search_results = self._search_realtime_info(message)
            if search_results:
                realtime_context = f"""

## 🔍 实时搜索结果（来自网络）
{search_results}

请结合以上实时信息和你的知识库回答用户问题。如果搜索结果包含最新信息，请优先使用并标注来源。
"""

        # 添加用户背景
        if context:
            user_context = f"""
## 用户背景
- 年级：{context.get('grade_name', '未知')}
- 专业：{context.get('major', '未知')}
- 兴趣方向：{', '.join(context.get('interests', [])) or '未设置'}

请结合用户背景推荐合适的业务板块和岗位。
"""
            full_prompt += user_context

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