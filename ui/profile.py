"""
档案面板界面
"""
import streamlit as st
from typing import Dict, Any, Optional
from core.memory import MemoryManager
from config import GRADE_CONFIGS


def render_profile(
    profile: Dict[str, Any],
    memory_manager: Optional[MemoryManager],
):
    """渲染档案面板"""

    st.markdown("### 📋 我的成长档案")

    # 基本信息卡片
    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 4rem;">🦆</div>
                <div style="font-size: 1.2rem; font-weight: bold;">
                    {}
                </div>
            </div>
            """.format(profile.get("nickname", "小鹅")), unsafe_allow_html=True)

        with col2:
            grade = profile.get("grade", "freshman")
            grade_config = GRADE_CONFIGS.get(grade, {})

            st.markdown(f"""
            **年级**：{grade_config.get('name', '未知')}

            **专业**：{profile.get('major', '未设置')}

            **学校**：{profile.get('university', '未设置')}

            **目标**：{profile.get('target', '未设置')}
            """)

    st.divider()

    # 当前阶段
    grade = profile.get("grade", "freshman")
    grade_config = GRADE_CONFIGS.get(grade, {})

    st.markdown("#### 📍 当前阶段")
    st.info(f"""
    **{grade_config.get('stage', '成长期')}**

    重点方向：
    - {grade_config.get('focus', ['持续成长'])[0] if grade_config.get('focus') else '持续成长'}
    """)

    # 兴趣方向
    st.markdown("#### ❤️ 兴趣方向")
    interests = profile.get("interests", [])
    if interests:
        cols = st.columns(min(len(interests), 3))
        for i, interest in enumerate(interests):
            with cols[i % 3]:
                st.tag(interest, color="primary")
    else:
        st.caption("暂未设置兴趣方向")

    # 成长目标
    st.markdown("#### 🎯 成长目标")
    goals = profile.get("goals", [])
    if goals:
        for goal in goals:
            st.markdown(f"- {goal}")
    else:
        st.caption("暂未设置成长目标")

    st.divider()

    # 记忆摘要（如果有）
    if memory_manager:
        st.markdown("#### 🧠 记忆摘要")

        memory_context = memory_manager.get_memory_context()

        # 技能追踪
        skills = memory_context.get("skills", [])
        if skills:
            st.markdown("**已关注技能：**")
            st.write(", ".join(skills))

        # 情绪趋势
        emotion_trend = memory_manager.get_emotion_trend()
        st.markdown("**情绪趋势：**")
        if emotion_trend["trend"] == "increasing_anxiety":
            st.warning(f"近期焦虑较多 ({emotion_trend['recent_count']} 次)")
        elif emotion_trend["trend"] == "some_anxiety":
            st.info(f"偶尔有些焦虑 ({emotion_trend['recent_count']} 次)")
        else:
            st.success("情绪状态稳定")

        # 里程碑
        milestones = memory_context.get("milestones", [])
        if milestones:
            st.markdown("**成长里程碑：**")
            for m in milestones[-5:]:
                st.caption(f"📅 {m['timestamp'][:10]} - {m['description']}")

    st.divider()

    # 编辑按钮
    if st.button("✏️ 编辑档案", use_container_width=True):
        st.info("编辑功能开发中...")