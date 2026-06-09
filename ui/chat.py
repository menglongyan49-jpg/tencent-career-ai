"""
对话界面 - 支持真正的流式输出 + 多Agent可视化
"""
import streamlit as st
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
from core.orchestrator import Orchestrator
from core.memory import MemoryManager
from config import PERSONALITY_CONFIGS


def render_chat(
    orchestrator: Orchestrator,
    memory_manager: Optional[MemoryManager],
    personality: str,
):
    """渲染对话界面"""

    # 头部信息 - 显示当前活跃Agent
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"### 💬 与 {personality} 对话")
    with col2:
        # 显示当前Agent
        agent_info = orchestrator.get_current_agent_info()
        agent_color = agent_info.get("color", "#667eea")
        st.markdown(f"""
        <div style="background: {agent_color}20; padding: 0.3rem 0.6rem; border-radius: 1rem; display: inline-block;">
            {agent_info['icon']} <b>{agent_info['name']}</b>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.caption(f"性格：{PERSONALITY_CONFIGS[personality]['style']}")

    # Agent团队展示
    with st.expander("🤖 我的专家团队", expanded=False):
        st.markdown("不同问题会自动路由到最合适的专家：")

        cols = st.columns(4)
        agent_list = [
            ("career_navigator", "🧭", "战术导航导师", "职业规划、技术学习"),
            ("emotional_supporter", "💝", "情绪树洞", "情绪疏导、心理支持"),
            ("interview_coach", "🎯", "面试教练", "面试准备、简历优化"),
            ("tencent_expert", "🐧", "鹅厂专家", "腾讯业务、岗位解读"),
        ]

        for i, (agent_id, icon, name, desc) in enumerate(agent_list):
            with cols[i]:
                is_active = agent_id == orchestrator.current_agent
                border_style = "2px solid #4CAF50" if is_active else "1px solid #ddd"
                bg_color = "#e8f5e9" if is_active else "#fafafa"

                st.markdown(f"""
                <div style="text-align: center; padding: 0.8rem; border: {border_style}; border-radius: 0.5rem; background: {bg_color};">
                    <div style="font-size: 1.5rem;">{icon}</div>
                    <div style="font-weight: bold; font-size: 0.9rem;">{name}</div>
                    <div style="font-size: 0.7rem; color: #666;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # 快捷问题（按Agent分类）
    st.markdown("**试试这些问题：**")

    quick_questions = [
        ("腾讯有哪些岗位适合我？", "🐧 鹅厂专家"),
        ("如何准备暑期实习面试？", "🎯 面试教练"),
        ("我最近很焦虑，能聊聊吗？", "💝 情绪树洞"),
        ("帮我规划一下职业发展路径", "🧭 战术导师"),
    ]

    cols = st.columns(2)
    for i, (q, agent_hint) in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(f"{q}", key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    st.divider()

    # 对话历史
    messages = st.session_state.get("messages", [])

    for msg in messages:
        with st.chat_message(msg["role"]):
            # 如果是助手消息，显示是哪个Agent回复的
            if msg["role"] == "assistant" and "agent" in msg:
                agent_data = Orchestrator.AGENT_INFO.get(msg["agent"], {})
                st.caption(f"{agent_data.get('icon', '🤖')} {agent_data.get('name', 'AI助手')}")
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("问我任何职业发展问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取 AI 响应
        with st.chat_message("assistant"):
            # 显示正在使用的Agent
            agent_info = orchestrator.get_current_agent_info()
            st.caption(f"{agent_info['icon']} {agent_info['name']} 正在思考...")

            response_placeholder = st.empty()
            full_response = ""

            # 获取用户档案
            user_profile = st.session_state.get("user_profile", {})

            # 构建历史消息
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in messages[-10:]  # 最近10条
            ]

            # 真正的流式输出
            try:
                async def stream_response():
                    nonlocal full_response
                    async for chunk in orchestrator.process(
                        prompt,
                        user_profile,
                        history,
                    ):
                        full_response += chunk
                        # 实时更新显示
                        response_placeholder.markdown(full_response + "▌")
                    return full_response

                # 运行流式输出
                full_response = asyncio.run(stream_response())
                # 最终显示（移除光标）
                response_placeholder.markdown(full_response)

                # 显示协作Agent（如果有）
                if orchestrator.agent_collaboration:
                    collab_names = [
                        Orchestrator.AGENT_INFO.get(a, {}).get("name", a)
                        for a in orchestrator.agent_collaboration
                    ]
                    st.caption(f"🤝 协作专家: {', '.join(collab_names)}")

            except Exception as e:
                st.error(f"发生错误: {str(e)}")
                # 如果流式输出失败，使用模拟响应
                full_response = get_mock_response(prompt, personality)
                response_placeholder.markdown(full_response)

        # 保存助手消息（包含Agent信息）
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "agent": orchestrator.current_agent,
        })


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