"""
设置面板界面 - 增强版
支持性格切换时的视觉反馈和实时预览
"""
import streamlit as st
from config import PERSONALITY_CONFIGS
import time


def render_settings(current_personality: str) -> str:
    """渲染设置面板，返回新的性格选择"""

    st.markdown("### ⚙️ 设置")

    # 性格设置
    st.markdown("#### 🎭 导师性格")
    st.markdown("选择你喜欢的陪伴风格")

    # 性格选择卡片（增强版）
    personality_options = list(PERSONALITY_CONFIGS.keys())
    current_index = personality_options.index(current_personality)

    personality = st.radio(
        "选择性格",
        options=personality_options,
        format_func=lambda x: f"{x}",
        index=current_index,
    )

    # 性格详情卡片
    config = PERSONALITY_CONFIGS[personality]

    # 根据性格类型设置不同的卡片颜色
    color_map = {
        "知心学姐": "#FFCDD2",  # 柔粉色
        "硬核极客": "#B3E5FC",  # 科技蓝
        "严厉面试官": "#CFD8DC",  # 灰色
        "全能导师": "#C8E6C9",  # 绿色
    }
    card_color = color_map.get(personality, "#F5F5F5")

    st.markdown(f"""
    <div style="background: {card_color}; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
        <p style="margin: 0; font-weight: bold;">{personality}</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{config['style']}</p>
    </div>
    """, unsafe_allow_html=True)

    # 性格特点标签
    st.markdown("**性格特点：**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"🗣️ {config['tone']}")
    with col2:
        st.caption(f"💬 {config['emoji_usage']}")
    with col3:
        st.caption("✅ 已选择" if personality == current_personality else "点击下方确认")

    # 对话风格预览
    with st.expander("💬 预览对话风格", expanded=True):
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #667eea;">
            <p style="margin: 0; font-style: italic;">"{config['example']}"</p>
        </div>
        """, unsafe_allow_html=True)

    # 切换确认按钮（带视觉反馈）
    if personality != current_personality:
        st.markdown("---")
        if st.button("🔄 确认切换性格", use_container_width=True, type="primary"):
            # 显示切换动画
            success_placeholder = st.empty()
            success_placeholder.success(f"✨ 已切换为「{personality}」风格！")
            time.sleep(0.5)
            return personality

    st.divider()

    # 其他设置
    st.markdown("#### 🔔 通知设置")
    enable_reminder = st.checkbox("开启成长提醒", value=True)
    enable_emotion_check = st.checkbox("情绪关怀提醒", value=True)

    st.markdown("#### 📊 数据管理")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("导出我的数据", use_container_width=True):
            st.info("数据导出功能开发中...")
    with col2:
        if st.button("清空对话历史", use_container_width=True):
            if st.session_state.get("messages"):
                st.session_state.messages = []
                st.success("对话历史已清空")

    st.divider()

    # 关于
    st.markdown("#### 📖 关于")
    st.markdown("""
    **未来鹅** - 大学生职业成长 AI 陪伴体

    版本：1.0.0

    将招聘前置为成长陪伴，在真实的情感链接中传递雇主品牌价值。
    """)

    return current_personality