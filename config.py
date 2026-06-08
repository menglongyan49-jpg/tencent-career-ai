"""
配置管理模块
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()


class AppConfig(BaseModel):
    """应用配置"""
    title: str = "未来鹅"
    llm_provider: Literal["openai", "anthropic", "local"] = "anthropic"
    llm_model: str = "claude-3-sonnet-20240229"
    debug: bool = False
    chroma_persist_dir: str = "./data/chroma"


# 性格配置
PERSONALITY_CONFIGS = {
    "知心学姐": {
        "style": "温柔细腻，善解人意，像一个大姐姐一样关心你",
        "tone": "温暖、鼓励、共情",
        "emoji_usage": "适度使用可爱emoji",
        "example": "哎呀，听起来你最近压力有点大呢~ 慢慢来，我们一起想办法",
    },
    "硬核极客": {
        "style": "技术导向，直击痛点，不废话",
        "tone": "专业、简洁、深度",
        "emoji_usage": "极少使用emoji",
        "example": "Go在腾讯云的微服务架构中应用广泛，重点掌握GMP模型和并发模式",
    },
    "严厉面试官": {
        "style": "模拟真实面试场景，一针见血，不留情面",
        "tone": "严肃、专业、挑战性",
        "emoji_usage": "不使用emoji",
        "example": "你说的这个项目，具体解决了什么问题？你的贡献是什么？量化结果呢？",
    },
    "全能导师": {
        "style": "平衡专业与温度，既有深度又有温度",
        "tone": "专业、友好、引导性",
        "emoji_usage": "适度使用emoji",
        "example": "这个问题很有意思！让我从几个角度帮你分析一下 🎯",
    },
}

# 年级配置
GRADE_CONFIGS = {
    "freshman": {
        "name": "大一",
        "stage": "认知启蒙期",
        "focus": ["了解行业", "探索兴趣", "打好基础"],
    },
    "sophomore": {
        "name": "大二",
        "stage": "方向探索期",
        "focus": ["确定方向", "积累技能", "项目实践"],
    },
    "junior": {
        "name": "大三",
        "stage": "实习冲刺期",
        "focus": ["准备实习", "完善简历", "面试练习"],
    },
    "senior": {
        "name": "大四",
        "stage": "求职决胜期",
        "focus": ["秋招春招", "面试冲刺", "拿到offer"],
    },
    "graduate": {
        "name": "研究生",
        "stage": "职业选择期",
        "focus": ["研究方向", "求职准备", "毕业答辩"],
    },
}

# 情绪关键词
ANXIETY_KEYWORDS = [
    "焦虑", "担心", "害怕", "紧张", "迷茫", "困惑",
    "挂了", "失败", "不行", "不会", "太难", "压力",
    "没信心", "没希望", "来不及", "来不及了", "完蛋",
]

# 意图关键词
INTENT_KEYWORDS = {
    "career": ["职业", "方向", "规划", "发展", "路径", "建议"],
    "technical": ["技术", "代码", "项目", "架构", "算法", "学习"],
    "interview": ["面试", "简历", "笔试", "offer", "招聘", "校招"],
    "tencent": ["腾讯", "鹅厂", "微信", "游戏", "腾讯云", "QQ"],
    "emotion": ANXIETY_KEYWORDS,
}


def get_config() -> AppConfig:
    """获取应用配置"""
    return AppConfig(
        title=os.getenv("APP_TITLE", "未来鹅"),
        llm_provider=os.getenv("LLM_PROVIDER", "anthropic"),
        llm_model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"),
        debug=os.getenv("APP_DEBUG", "false").lower() == "true",
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
    )