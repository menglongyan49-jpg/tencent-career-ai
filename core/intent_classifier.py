"""
意图分类模块
"""
from typing import List, Dict, Any
from config import INTENT_KEYWORDS


class IntentClassifier:
    """意图分类器"""

    # 扩展的意图关键词
    INTENT_PATTERNS = {
        "career": {
            "keywords": ["职业", "方向", "规划", "发展", "路径", "建议", "未来", "前景"],
            "questions": ["我该选什么方向", "怎么规划", "未来发展"],
        },
        "technical": {
            "keywords": ["技术", "代码", "项目", "架构", "算法", "学习", "框架", "语言"],
            "questions": ["怎么学", "用什么技术", "项目怎么做"],
        },
        "interview": {
            "keywords": ["面试", "简历", "笔试", "offer", "招聘", "校招", "实习"],
            "questions": ["怎么准备面试", "简历怎么写", "面试题"],
        },
        "tencent": {
            "keywords": ["腾讯", "鹅厂", "微信", "王者荣耀", "腾讯云", "QQ"],
            "questions": ["腾讯怎么样", "鹅厂面试", "腾讯岗位"],
        },
        "emotion": {
            "keywords": ["焦虑", "迷茫", "压力", "害怕", "担心", "紧张"],
            "questions": ["我很焦虑", "不知道怎么办", "压力很大"],
        },
        "greeting": {
            "keywords": ["你好", "在吗", "嗨", "hi", "hello"],
            "questions": [],
        },
    }

    def classify(self, message: str) -> List[Dict[str, Any]]:
        """
        分类意图
        返回: [{"intent": str, "confidence": float, "matched_keywords": list}]
        """
        message_lower = message.lower()
        detected_intents = []

        for intent, patterns in self.INTENT_PATTERNS.items():
            # 关键词匹配
            keyword_matches = [
                kw for kw in patterns["keywords"]
                if kw in message_lower
            ]

            # 问题模式匹配
            question_matches = [
                q for q in patterns.get("questions", [])
                if q in message_lower
            ]

            if keyword_matches or question_matches:
                # 计算置信度
                confidence = min(1.0, (len(keyword_matches) * 0.2 + len(question_matches) * 0.3))
                detected_intents.append({
                    "intent": intent,
                    "confidence": confidence,
                    "matched_keywords": keyword_matches + question_matches,
                })

        # 按置信度排序
        detected_intents.sort(key=lambda x: x["confidence"], reverse=True)

        return detected_intents if detected_intents else [{"intent": "general", "confidence": 0.3, "matched_keywords": []}]

    def get_primary_intent(self, message: str) -> str:
        """获取主要意图"""
        intents = self.classify(message)
        return intents[0]["intent"] if intents else "general"

    def has_intent(self, message: str, target_intent: str) -> bool:
        """判断是否包含特定意图"""
        intents = self.classify(message)
        return any(i["intent"] == target_intent for i in intents)