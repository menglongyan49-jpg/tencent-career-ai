"""
入口引导界面
"""
import streamlit as st
from typing import Optional, Dict, Any
from config import PERSONALITY_CONFIGS, GRADE_CONFIGS


def render_onboarding() -> Optional[Dict[str, Any]]:
    """渲染入口引导界面"""

    st.markdown("""
    <style>
    .onboarding-header {
        text-align: center;
        padding: 2rem 0;
    }
    .goose-icon {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # 进度步骤
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1

    step = st.session_state.onboarding_step

    # 步骤指示器
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            if i + 1 <= step:
                st.success(f"✓ 步骤 {i + 1}")
            elif i + 1 == step:
                st.info(f"📍 步骤 {i + 1}")
            else:
                st.empty()

    st.divider()

    # 步骤内容
    if step == 1:
        return render_step_1()
    elif step == 2:
        return render_step_2()
    elif step == 3:
        return render_step_3()
    elif step == 4:
        return render_step_4()

    return None


def render_step_1() -> Optional[Dict[str, Any]]:
    """步骤1：基本信息"""

    st.markdown('<p class="goose-icon">🦆</p>', unsafe_allow_html=True)
    st.markdown("### 欢迎来到未来鹅！")
    st.markdown("让我们先认识一下你 👋")

    # 初始化表单数据
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}

    nickname = st.text_input("你的昵称", placeholder="给自己起个可爱的名字")
    university = st.text_input("学校（选填）", placeholder="你的大学名称")
    major = st.text_input("专业", placeholder="你的专业方向")

    if st.button("下一步 →", use_container_width=True, type="primary"):
        if nickname:
            st.session_state.form_data.update({
                "nickname": nickname,
                "university": university,
                "major": major,
            })
            st.session_state.onboarding_step = 2
            st.rerun()
        else:
            st.warning("请填写昵称")

    return None


def render_step_2() -> Optional[Dict[str, Any]]:
    """步骤2：年级选择"""

    st.markdown("### 你现在是几年级？")
    st.markdown("不同阶段有不同的成长路径")

    grade = st.radio(
        "选择年级",
        options=list(GRADE_CONFIGS.keys()),
        format_func=lambda x: f"{GRADE_CONFIGS[x]['name']} - {GRADE_CONFIGS[x]['stage']}",
        horizontal=False,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 上一步", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
    with col2:
        if st.button("下一步 →", use_container_width=True, type="primary"):
            st.session_state.form_data["grade"] = grade
            st.session_state.onboarding_step = 3
            st.rerun()

    return None


def render_step_3() -> Optional[Dict[str, Any]]:
    """步骤3：兴趣和目标"""

    st.markdown("### 你的兴趣和目标")

    # 兴趣选择
    st.markdown("**感兴趣的方向**（可多选）")
    interests = st.multiselect(
        "选择兴趣",
        options=[
            "产品经理", "技术开发", "数据分析", "UI设计", "运营推广",
            "游戏策划", "市场营销", "人力资源", "投资分析", "内容创作",
        ],
        default=st.session_state.form_data.get("interests", []),
        label_visibility="collapsed",
    )

    # 目标选择
    st.markdown("**成长目标**（可多选）")
    goals = st.multiselect(
        "选择目标",
        options=[
            "进入大厂工作", "获得实习经验", "提升专业技能", "了解行业动态",
            "明确职业方向", "准备求职面试", "拓展人脉资源", "探索创业机会",
        ],
        default=st.session_state.form_data.get("goals", []),
        label_visibility="collapsed",
    )

    # 目标岗位
    target = st.text_input(
        "目标岗位（选填）",
        placeholder="例如：后端开发、产品经理",
        value=st.session_state.form_data.get("target", ""),
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 上一步", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()
    with col2:
        if st.button("下一步 →", use_container_width=True, type="primary"):
            st.session_state.form_data.update({
                "interests": interests,
                "goals": goals,
                "target": target,
            })
            st.session_state.onboarding_step = 4
            st.rerun()

    return None


def render_step_4() -> Optional[Dict[str, Any]]:
    """步骤4：性格选择"""

    st.markdown("### 选择你的专属导师性格")
    st.markdown("不同性格的导师会给你不同风格的陪伴体验")

    # 性格选择卡片
    personality = st.radio(
        "选择性格",
        options=list(PERSONALITY_CONFIGS.keys()),
        format_func=lambda x: f"{x} - {PERSONALITY_CONFIGS[x]['style']}",
    )

    # 性格预览
    st.markdown("**预览对话风格：**")
    st.info(f"💬 \"{PERSONALITY_CONFIGS[personality]['example']}\"")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 上一步", use_container_width=True):
            st.session_state.onboarding_step = 3
            st.rerun()
    with col2:
        if st.button("🚀 开始探索", use_container_width=True, type="primary"):
            # 保存性格选择
            st.session_state.personality = personality
            st.session_state.form_data["personality"] = personality

            # 返回完整档案
            profile = st.session_state.form_data.copy()
            profile["skills"] = []

            # 清理临时数据
            del st.session_state.onboarding_step
            del st.session_state.form_data

            return profile

    return None