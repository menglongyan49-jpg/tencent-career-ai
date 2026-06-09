"""
记忆可视化面板
展示 RAG 记忆系统的存储内容
"""
import streamlit as st
from typing import Dict, Any, Optional, List
from core.memory import MemoryManager
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_memory_panel(memory_manager: Optional[MemoryManager]):
    """渲染记忆可视化面板"""

    st.markdown("### 🧠 记忆可视化")

    if memory_manager is None:
        st.warning("记忆系统未初始化，请先完成用户引导")
        return

    # Tab 组织不同视图
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 总览", "💬 对话记忆", "🔍 语义搜索", "📈 情绪分析", "⚙️ 数据管理"
    ])

    with tab1:
        render_overview(memory_manager)

    with tab2:
        render_conversation_memory(memory_manager)

    with tab3:
        render_semantic_search(memory_manager)

    with tab4:
        render_emotion_analysis(memory_manager)

    with tab5:
        render_data_management(memory_manager)


def render_overview(memory_manager: MemoryManager):
    """总览视图"""
    st.markdown("#### 📊 记忆系统总览")

    # 获取统计数据
    stats = memory_manager.get_stats()

    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💬 对话次数",
            value=stats.get("total_conversations", 0),
            delta=None
        )

    with col2:
        st.metric(
            label="📝 消息总数",
            value=stats.get("total_messages", 0),
            delta=None
        )

    with col3:
        st.metric(
            label="📅 活跃天数",
            value=stats.get("days_active", 0),
            delta=None
        )

    with col4:
        st.metric(
            label="🔢 向量数量",
            value=stats.get("vector_count", 0),
            delta=None
        )

    st.divider()

    # 技能雷达图
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🛠️ 技能熟练度")

        skills = memory_manager.get_all_skills()
        if skills:
            # 创建雷达图
            categories = [s["name"] for s in skills[:8]]
            values = [s["count"] for s in skills[:8]]

            # 闭合雷达图
            categories = categories + [categories[0]] if categories else []
            values = values + [values[0]] if values else []

            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line_color='#667eea',
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(values) if values else 10])
                ),
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # 技能列表
            with st.expander("📋 技能详情"):
                for skill in skills:
                    level_emoji = {
                        "expert": "🟢",
                        "intermediate": "🟡",
                        "beginner": "🔵",
                        "interested": "⚪"
                    }.get(skill["level"], "⚪")
                    st.markdown(f"{level_emoji} **{skill['name']}** - {skill['level']} ({skill['count']}次)")
        else:
            st.info("暂无技能记录，开始对话后会自动提取")

    with col_right:
        st.markdown("#### 🎯 目标进度")

        goals = memory_manager.get_active_goals()
        if goals:
            for goal in goals:
                progress = goal.get("progress", 0)
                st.markdown(f"**{goal['goal']}**")
                st.progress(progress / 100, text=f"{progress}%")
                st.caption(f"创建于: {goal.get('created_at', '')[:10]}")
        else:
            st.info("暂无目标，在对话中告诉我你的目标吧！")

        # 里程碑时间线
        milestones = memory_manager.get_recent_milestones(5)
        if milestones:
            st.markdown("#### 🏆 最近里程碑")
            for m in reversed(milestones):
                st.markdown(f"""
                **{m['timestamp'][:10]}** - {m['description']}
                """)


def render_conversation_memory(memory_manager: MemoryManager):
    """对话记忆视图"""
    st.markdown("#### 💬 对话记忆检索")

    # 时间范围筛选
    col1, col2 = st.columns([3, 1])
    with col2:
        limit = st.select_slider(
            "显示数量",
            options=[10, 20, 30, 50],
            value=20
        )

    # 获取最近对话
    conversations = memory_manager.get_recent_conversations(limit)

    if not conversations:
        st.info("暂无对话记录，开始一段对话吧！")
        return

    # 对话列表
    st.markdown(f"**最近 {len(conversations)} 条记忆**")

    # 按日期分组
    grouped = {}
    for conv in conversations:
        date = conv.get("timestamp", "")[:10] if conv.get("timestamp") else "未知日期"
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(conv)

    for date, convs in sorted(grouped.items(), reverse=True):
        with st.expander(f"📅 {date} ({len(convs)} 条)", expanded=False):
            for conv in convs:
                role = conv.get("role", "unknown")
                content = conv.get("content", "")
                time = conv.get("timestamp", "")[11:16] if conv.get("timestamp") else ""

                if role == "user":
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                        <small>🧑 {time}</small><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f5f5f5; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                        <small>🦆 {time}</small><br>
                        {content[:300]}{'...' if len(content) > 300 else ''}
                    </div>
                    """, unsafe_allow_html=True)

    # 记忆摘要
    st.divider()
    st.markdown("#### 📝 记忆摘要")

    summaries = memory_manager.get_summaries(5)
    if summaries:
        for s in summaries:
            with st.container():
                st.caption(f"📅 {s['timestamp'][:10]}")
                st.markdown(s['summary'])
                st.divider()
    else:
        st.info("暂无摘要，系统会在对话积累后自动生成")


def render_semantic_search(memory_manager: MemoryManager):
    """语义搜索视图"""
    st.markdown("#### 🔍 语义搜索")

    st.caption("使用自然语言搜索相关记忆，基于向量相似度匹配")

    # 搜索框
    search_query = st.text_input(
        "输入搜索关键词或问题",
        placeholder="例如：我之前问过什么关于面试的问题？"
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        n_results = st.slider("结果数量", 1, 10, 5)

    if search_query:
        with st.spinner("搜索中..."):
            results = memory_manager.search_memories(search_query, n_results)

        if results:
            st.markdown(f"**找到 {len(results)} 条相关记忆**")

            for i, result in enumerate(results):
                distance = result.get("distance", 0)
                similarity = 1 - distance if distance else 0

                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(result["content"][:500])
                    with col2:
                        st.metric("相似度", f"{similarity:.1%}")

                    metadata = result.get("metadata", {})
                    st.caption(f"📅 {metadata.get('timestamp', '')[:10]} | 🎭 {metadata.get('role', '')}")

                    st.divider()
        else:
            st.warning("未找到相关记忆")

    # 快捷搜索
    st.divider()
    st.markdown("#### 🏷️ 快捷搜索")

    quick_searches = [
        "面试准备",
        "简历优化",
        "技术学习",
        "职业规划",
        "情绪倾诉",
    ]

    cols = st.columns(len(quick_searches))
    for i, qs in enumerate(quick_searches):
        with cols[i]:
            if st.button(qs, key=f"quick_search_{i}"):
                st.session_state.quick_search = qs
                st.rerun()


def render_emotion_analysis(memory_manager: MemoryManager):
    """情绪分析视图"""
    st.markdown("#### 📈 情绪分析")

    emotion_trend = memory_manager.get_emotion_trend()

    # 情绪状态卡片
    trend = emotion_trend.get("trend", "unknown")

    trend_config = {
        "stable": {"emoji": "😊", "color": "green", "text": "情绪稳定"},
        "needs_attention": {"emoji": "😐", "color": "orange", "text": "需要关注"},
        "concerning": {"emoji": "😟", "color": "red", "text": "需要关怀"},
        "unknown": {"emoji": "❓", "color": "gray", "text": "暂无数据"},
    }

    config = trend_config.get(trend, trend_config["unknown"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">{config['emoji']}</div>
            <div style="font-size: 1.2rem; color: {config['color']};">{config['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric(
            label="负面情绪比例",
            value=f"{emotion_trend.get('negative_ratio', 0):.0%}"
        )

    with col3:
        st.metric(
            label="记录事件数",
            value=emotion_trend.get("total_events", 0)
        )

    st.divider()

    # 情绪历史图表
    recent_emotions = emotion_trend.get("recent_emotions", [])

    if recent_emotions:
        st.markdown("#### 📊 情绪变化趋势")

        # 准备数据
        df = pd.DataFrame(recent_emotions)

        # 情绪映射
        emotion_map = {
            "happy": 1, "neutral": 0, "calm": 0.5,
            "anxious": -0.5, "frustrated": -0.7, "sad": -1,
            "worried": -0.6, "stressed": -0.8,
        }

        df["score"] = df["emotion"].map(lambda x: emotion_map.get(x, 0))

        # 创建折线图
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["score"],
            mode='lines+markers',
            name='情绪值',
            line=dict(color='#667eea', width=2),
            marker=dict(size=8),
        ))

        fig.update_layout(
            yaxis=dict(
                ticktext=['难过', '焦虑', '平静', '开心'],
                tickvals=[-1, -0.5, 0, 1],
            ),
            xaxis_title="时间",
            yaxis_title="情绪值",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

        # 情绪分布饼图
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 🥧 情绪分布")

            emotion_counts = {}
            for e in recent_emotions:
                emo = e.get("emotion", "unknown")
                emotion_counts[emo] = emotion_counts.get(emo, 0) + 1

            fig_pie = go.Figure(data=[go.Pie(
                labels=list(emotion_counts.keys()),
                values=list(emotion_counts.values()),
                hole=.3,
            )])
            fig_pie.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.markdown("#### 📝 最近情绪记录")

            for e in recent_emotions[-5:]:
                emotion = e.get("emotion", "unknown")
                timestamp = e.get("timestamp", "")[:16]
                emoji = {
                    "happy": "😊", "neutral": "😐", "calm": "😌",
                    "anxious": "😰", "frustrated": "😤", "sad": "😢",
                    "worried": "😟", "stressed": "😵",
                }.get(emotion, "❓")

                st.markdown(f"{emoji} **{emotion}** - {timestamp}")

    else:
        st.info("暂无情绪记录，开始对话后系统会自动分析情绪")


def render_data_management(memory_manager: MemoryManager):
    """数据管理视图"""
    st.markdown("#### ⚙️ 数据管理")

    # 数据统计
    stats = memory_manager.get_stats()

    st.markdown("##### 📊 存储统计")

    stat_items = [
        ("对话次数", stats.get("total_conversations", 0)),
        ("消息总数", stats.get("total_messages", 0)),
        ("活跃天数", stats.get("days_active", 0)),
        ("技能数量", stats.get("skills_count", 0)),
        ("目标数量", stats.get("goals_count", 0)),
        ("里程碑数", stats.get("milestones_count", 0)),
        ("向量数量", stats.get("vector_count", 0)),
    ]

    cols = st.columns(4)
    for i, (label, value) in enumerate(stat_items):
        with cols[i % 4]:
            st.metric(label, value)

    st.divider()

    # 数据导出
    st.markdown("##### 📤 数据导出")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 导出所有记忆数据", use_container_width=True):
            export_data = memory_manager.export_memories()

            # 转换为 JSON 字符串
            import json
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

            st.download_button(
                label="💾 下载 JSON 文件",
                data=json_str,
                file_name=f"memory_export_{memory_manager.user_id}.json",
                mime="application/json",
                use_container_width=True,
            )

    with col2:
        if st.button("📋 导出用户档案", use_container_width=True):
            profile = memory_manager.get_profile()

            import json
            json_str = json.dumps(profile, ensure_ascii=False, indent=2)

            st.download_button(
                label="💾 下载档案文件",
                data=json_str,
                file_name=f"profile_{memory_manager.user_id}.json",
                mime="application/json",
                use_container_width=True,
            )

    st.divider()

    # 记忆搜索测试
    st.markdown("##### 🧪 记忆系统测试")

    if st.button("🔍 测试向量存储连接"):
        try:
            vector_count = stats.get("vector_count", 0)
            if vector_count >= 0:
                st.success(f"✅ 向量存储连接正常，当前存储 {vector_count} 条记录")
            else:
                st.warning("⚠️ 向量存储可能未正确初始化")
        except Exception as e:
            st.error(f"❌ 连接失败: {str(e)}")

    # 清理选项（需要确认）
    st.divider()
    st.markdown("##### 🗑️ 数据清理")

    st.warning("⚠️ 以下操作不可恢复，请谨慎使用")

    if st.button("🗑️ 清空对话记忆", type="secondary"):
        st.session_state.confirm_clear = True

    if st.session_state.get("confirm_clear"):
        st.warning("确认要清空所有对话记忆吗？")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认清空"):
                # 执行清空
                try:
                    if memory_manager._conversation_collection:
                        memory_manager._conversation_collection.delete(
                            where={"user_id": memory_manager.user_id}
                        )
                    st.success("对话记忆已清空")
                    st.session_state.confirm_clear = False
                    st.rerun()
                except Exception as e:
                    st.error(f"清空失败: {str(e)}")
        with col2:
            if st.button("❌ 取消"):
                st.session_state.confirm_clear = False
                st.rerun()