"""
设置面板界面
"""
import streamlit as st
from config import PERSONALITY_CONFIGS


def render_settings(current_personality: str) -> str:
    """渲染设置面板，返回新的性格选择"""

    st.markdown("### ⚙️ 设置")

    # 性格设置
    st.markdown("#### 🎭 导师性格")
    st.markdown("选择你喜欢的陪伴风格")

    personality = st.radio(
        "选择性格",
        options=list(PERSONALITY_CONFIGS.keys()),
        format_func=lambda x: f"{x}",
        index=list(PERSONALITY_CONFIGS.keys()).index(current_personality),
    )

    # 性格详情
    config = PERSONALITY_CONFIGS[personality]
    st.markdown(f"""
    **风格**：{config['style']}

    **基调**：{config['tone']}

    **Emoji使用**：{config['emoji_usage']}

    **对话示例**：
    > {config['example']}
    """)

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

    return personality