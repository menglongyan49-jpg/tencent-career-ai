"""
情绪检测模块
"""
from typing import Tuple, List
from config import ANXIETY_KEYWORDS


class EmotionDetector:
    """情绪检测器"""

    # 扩展的情绪关键词
    EMOTION_KEYWORDS = {
        "anxious": [
            "焦虑", "担心", "害怕", "紧张", "恐慌", "不安",
            "压力", "崩溃", "绝望", "无助",
        ],
        "sad": [
            "难过", "伤心", "失落", "沮丧", "郁闷", "不开心",
        ],
        "angry": [
            "生气", "愤怒", "烦躁", "不爽", "讨厌",
        ],
        "happy": [
            "开心", "高兴", "兴奋", "满足", "顺利", "成功",
        ],
        "confused": [
            "迷茫", "困惑", "不知道", "不清楚", "搞不懂",
        ],
    }

    # 强度修饰词
    INTENSITY_MODIFIERS = {
        "very": ["很", "非常", "特别", "极其", "太"],
        "slightly": ["有点", "稍微", "一点", "些许"],
    }

    def detect(self, message: str) -> Tuple[str, float, List[str]]:
        """
        检测情绪
        返回: (情绪类型, 强度, 匹配的关键词)
        """
        message_lower = message.lower()
        detected_emotions = {}

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in message_lower]
            if matches:
                # 检查强度修饰词
                intensity = 0.5  # 默认中等强度
                for mod in self.INTENSITY_MODIFIERS["very"]:
                    if mod in message_lower:
                        intensity = 0.8
                        break
                for mod in self.INTENSITY_MODIFIERS["slightly"]:
                    if mod in message_lower:
                        intensity = 0.3
                        break

                detected_emotions[emotion] = {
                    "intensity": intensity,
                    "matches": matches,
                }

        if not detected_emotions:
            return "neutral", 0.0, []

        # 返回强度最高的情绪
        dominant_emotion = max(
            detected_emotions.items(),
            key=lambda x: x[1]["intensity"]
        )

        return (
            dominant_emotion[0],
            dominant_emotion[1]["intensity"],
            dominant_emotion[1]["matches"],
        )

    def is_anxious(self, message: str) -> Tuple[bool, float]:
        """判断是否焦虑"""
        emotion, intensity, _ = self.detect(message)
        is_anxiety = emotion in ["anxious", "confused"] or intensity >= 0.5
        return is_anxiety, intensity

    def get_emotion_summary(self, message: str) -> dict:
        """获取情绪摘要"""
        emotion, intensity, keywords = self.detect(message)
        return {
            "emotion": emotion,
            "intensity": intensity,
            "keywords": keywords,
            "needs_support": emotion in ["anxious", "sad", "confused"] and intensity >= 0.5,
        }