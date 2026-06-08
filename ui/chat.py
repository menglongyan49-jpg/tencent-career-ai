"""
对话界面
"""
import streamlit as st
from typing import Optional, Dict, Any, AsyncGenerator
from core.orchestrator import Orchestrator
from core.memory import MemoryManager
from config import PERSONALITY_CONFIGS


def render_chat(
    orchestrator: Orchestrator,
    memory_manager: Optional[MemoryManager],
    personality: str,
):
    """渲染对话界面"""

    # 头部信息
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 💬 与 {personality} 对话")
    with col2:
        st.caption(f"性格：{PERSONALITY_CONFIGS[personality]['style']}")

    # 快捷问题
    st.markdown("**试试这些问题：**")
    quick_questions = [
        "腾讯有哪些岗位适合我？",
        "如何准备暑期实习面试？",
        "我最近很焦虑，能聊聊吗？",
        "帮我分析一下我的简历",
    ]

    cols = st.columns(2)
    for i, q in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    st.divider()

    # 对话历史
    messages = st.session_state.get("messages", [])

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("问我任何职业发展问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取 AI 响应
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            # 获取用户档案
            user_profile = st.session_state.get("user_profile", {})

            # 构建历史消息
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in messages[-10:]  # 最近10条
            ]

            # 流式输出
            import asyncio

            async def get_response():
                response_text = ""
                async for chunk in orchestrator.process(
                    prompt,
                    user_profile,
                    history,
                ):
                    response_text += chunk
                return response_text

            # 运行异步函数
            try:
                full_response = asyncio.run(get_response())
                response_placeholder.markdown(full_response)
            except Exception as e:
                # 如果流式输出失败，使用模拟响应
                full_response = get_mock_response(prompt, personality)
                response_placeholder.markdown(full_response)

        # 保存助手消息
        st.session_state.messages.append({"role": "assistant", "content": full_response})


def get_mock_response(message: str, personality: str) -> str:
    """获取模拟响应（用于演示）"""

    personality_style = PERSONALITY_CONFIGS.get(personality, PERSONALITY_CONFIGS["全能导师"])

    if "腾讯" in message or "鹅厂" in message:
        return f"""关于腾讯，让我给你介绍一下 🐧

**腾讯主要业务板块：**

📱 **微信事业群 (WXG)**
- 微信、企业微信、微信支付
- 适合：产品经理、后端开发

🎮 **游戏事业群 (IEG)**
- 王者荣耀、和平精英
- 适合：游戏策划、游戏开发

☁️ **云与智慧产业事业群 (CSIG)**
- 腾讯云、腾讯会议
- 适合：后端开发、解决方案架构师

{personality_style['example']}

想了解哪个具体方向？"""

    if "面试" in message or "简历" in message:
        return f"""关于求职准备，我有以下建议 📋

**简历优化要点：**
1. 使用 STAR 法则描述项目经历
2. 量化成果，用数据说话
3. 突出与目标岗位匹配的技能

**面试准备：**
1. 研究目标岗位的 JD
2. 准备 2-3 个核心项目故事
3. 练习常见面试题

{personality_style['example']}

需要我帮你模拟面试吗？"""

    if "焦虑" in message or "迷茫" in message or "压力" in message:
        return f"""我能感受到你现在的压力 😔

这种感受其实很正常，很多同学在求职季都会有类似的焦虑。你不是一个人在面对这些。

**试着这样想：**
- 把大目标拆成小步骤
- 每天进步一点点就好
- 失败也是成长的一部分

{personality_style['example']}

想聊聊具体是什么让你感到焦虑吗？"""

    return f"""你好！我是你的成长伙伴「未来鹅」🦆

{personality_style['example']}

我可以帮你：
- 🎯 规划职业发展路径
- 💼 准备简历和面试
- 🏢 了解腾讯和互联网行业
- 💡 解答各种职业困惑

有什么想聊的吗？"""