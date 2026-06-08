"""
UI 模块初始化
"""
from ui.onboarding import render_onboarding
from ui.chat import render_chat
from ui.profile import render_profile
from ui.settings import render_settings

__all__ = [
    "render_onboarding",
    "render_chat",
    "render_profile",
    "render_settings",
]