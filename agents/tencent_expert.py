"""
鹅厂专家 - Tencent Expert Agent
专注于腾讯业务、文化和岗位解读
"""
from typing import Optional, Dict, Any, AsyncGenerator
from agents.base_agent import BaseAgent


class TencentExpert(BaseAgent):
    """鹅厂专家"""

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

## 回答原则
- 信息准确，来源权威
- 客观介绍，不夸大不贬低
- 结合学生背景给出针对性建议
- 传递腾讯的雇主品牌价值"""

    def __init__(self, llm, personality: str = "全能导师"):
        super().__init__("TencentExpert", llm, personality, self.SYSTEM_PROMPT)

    async def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """处理消息，流式返回响应"""
        full_prompt = self.build_system_prompt(self.SYSTEM_PROMPT)

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

        chain = self._create_chain(full_prompt)

        # 构建历史消息
        msg_history = history or []

        # 流式输出
        async for chunk in chain.astream(
            {"input": message, "history": msg_history},
        ):
            if hasattr(chunk, "content"):
                yield chunk.content