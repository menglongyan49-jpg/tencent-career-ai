"""
Streamlit 主入口
未来鹅 - 大学生职业成长 AI 陪伴体
"""
import streamlit as st
from typing import Optional
import json
import os

from config import get_config, PERSONALITY_CONFIGS, GRADE_CONFIGS
from core.orchestrator import Orchestrator
from core.memory import MemoryManager
from storage.user_profile import UserProfileStorage
from ui.onboarding import render_onboarding
from ui.chat import render_chat
from ui.profile import render_profile
from ui.settings import render_settings


def init_session_state():
    """初始化会话状态"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "is_onboarded" not in st.session_state:
        st.session_state.is_onboarded = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "personality" not in st.session_state:
        st.session_state.personality = "全能导师"
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = None


def main():
    """主函数"""
    config = get_config()

    # 页面配置
    st.set_page_config(
        page_title=config.title,
        page_icon="🦆",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 自定义样式
    st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .goose-avatar {
        font-size: 3rem;
        text-align: center;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
    }
    .emotion-support {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # 初始化会话状态
    init_session_state()

    # 初始化存储和核心组件
    profile_storage = UserProfileStorage()

    # 侧边栏
    with st.sidebar:
        st.markdown('<p class="goose-avatar">🦆</p>', unsafe_allow_html=True)
        st.markdown(f"### {config.title}")
        st.caption("大学生职业成长 AI 陪伴体")

        st.divider()

        # 导航
        page = st.radio(
            "导航",
            ["💬 对话", "📋 我的档案", "⚙️ 设置"],
            label_visibility="collapsed",
        )

        st.divider()

        # 用户状态
        if st.session_state.user_profile:
            profile = st.session_state.user_profile
            st.markdown("**当前状态**")
            st.info(f"""
            📚 {GRADE_CONFIGS.get(profile.get('grade', 'freshman'), {}).get('name', '大一')}
            🎯 {profile.get('target', '未设置')}
            🎭 {st.session_state.personality}
            """)

            if st.button("🔄 重新开始", use_container_width=True):
                st.session_state.is_onboarded = False
                st.session_state.user_profile = None
                st.session_state.messages = []
                st.rerun()

    # 主内容区
    if not st.session_state.is_onboarded:
        # 入口引导
        profile = render_onboarding()
        if profile:
            st.session_state.user_profile = profile
            st.session_state.is_onboarded = True
            st.session_state.user_id = profile_storage.create_profile(profile)
            # 初始化 Orchestrator
            st.session_state.orchestrator = Orchestrator(
                user_id=st.session_state.user_id,
                personality=st.session_state.personality,
            )
            # 初始化 RAG 记忆管理器（传入 LLM 用于摘要生成）
            st.session_state.memory_manager = MemoryManager(
                user_id=st.session_state.user_id,
                llm=st.session_state.orchestrator.llm,
            )
            # 设置记忆管理器到 Orchestrator
            st.session_state.orchestrator.set_memory_manager(st.session_state.memory_manager)
            st.rerun()
    else:
        # 主功能页面
        if page == "💬 对话":
            render_chat(
                orchestrator=st.session_state.orchestrator,
                memory_manager=st.session_state.memory_manager,
                personality=st.session_state.personality,
            )
        elif page == "📋 我的档案":
            render_profile(
                profile=st.session_state.user_profile,
                memory_manager=st.session_state.memory_manager,
            )
        elif page == "⚙️ 设置":
            new_personality = render_settings(
                current_personality=st.session_state.personality,
            )
            if new_personality != st.session_state.personality:
                st.session_state.personality = new_personality
                # 更新 Orchestrator 的性格
                if st.session_state.orchestrator:
                    st.session_state.orchestrator.update_personality(new_personality)
                st.rerun()


if __name__ == "__main__":
    main()