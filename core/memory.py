"""
长期记忆管理模块
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class MemoryManager:
    """长期记忆管理器"""

    def __init__(self, user_id: str, storage_dir: str = "./data/memory"):
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 记忆文件路径
        self.memory_file = self.storage_dir / f"{user_id}_memory.json"

        # 加载或初始化记忆
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """加载记忆"""
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._init_memory()

    def _init_memory(self) -> Dict[str, Any]:
        """初始化记忆结构"""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),

            # 基础档案
            "profile": {
                "nickname": "",
                "grade": "",
                "major": "",
                "university": "",
                "target": "",
            },

            # 技能追踪
            "skills": [],

            # 兴趣方向
            "interests": [],

            # 成长目标
            "goals": [],

            # 情绪记录
            "emotion_history": [],

            # 对话摘要
            "conversation_summaries": [],

            # 关键事件
            "milestones": [],

            # 学习进度
            "learning_progress": {},
        }

    def _save_memory(self):
        """保存记忆"""
        self.memory["updated_at"] = datetime.now().isoformat()
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def update_profile(self, profile: Dict[str, Any]):
        """更新用户档案"""
        self.memory["profile"].update(profile)
        self._save_memory()

    async def update_skills(self, new_skills: List[str]):
        """更新技能列表"""
        current_skills = set(self.memory.get("skills", []))
        added_skills = [s for s in new_skills if s not in current_skills]

        if added_skills:
            self.memory["skills"] = list(current_skills | set(new_skills))
            # 记录里程碑
            self._add_milestone("skill_update", f"新增技能关注: {', '.join(added_skills)}")
            self._save_memory()

    async def record_emotion_event(self, emotion: str, trigger: str):
        """记录情绪事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "trigger": trigger[:100],  # 截取前100字符
        }
        self.memory["emotion_history"].append(event)

        # 只保留最近20条
        if len(self.memory["emotion_history"]) > 20:
            self.memory["emotion_history"] = self.memory["emotion_history"][-20:]

        self._save_memory()

    async def save_conversation(self, user_message: str, assistant_response: str):
        """保存对话记录"""
        # 简单实现：保存关键信息
        # 实际项目中可以使用 LLM 生成摘要
        summary = {
            "timestamp": datetime.now().isoformat(),
            "user_message_preview": user_message[:50],
            "response_preview": assistant_response[:50],
        }
        self.memory["conversation_summaries"].append(summary)

        # 只保留最近50条
        if len(self.memory["conversation_summaries"]) > 50:
            self.memory["conversation_summaries"] = self.memory["conversation_summaries"][-50:]

        self._save_memory()

    def _add_milestone(self, event_type: str, description: str):
        """添加里程碑"""
        milestone = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
        }
        self.memory["milestones"].append(milestone)

    def get_memory_context(self) -> Dict[str, Any]:
        """获取记忆上下文"""
        return {
            "profile": self.memory.get("profile", {}),
            "skills": self.memory.get("skills", []),
            "interests": self.memory.get("interests", []),
            "goals": self.memory.get("goals", []),
            "recent_emotions": self.memory.get("emotion_history", [])[-5:],
            "milestones": self.memory.get("milestones", [])[-10:],
        }

    def get_emotion_trend(self) -> Dict[str, Any]:
        """获取情绪趋势"""
        recent_emotions = self.memory.get("emotion_history", [])[-10:]
        if not recent_emotions:
            return {"trend": "stable", "recent_count": 0}

        anxious_count = sum(
            1 for e in recent_emotions
            if e.get("emotion") in ["anxious", "slightly_anxious"]
        )

        if anxious_count >= 5:
            return {"trend": "increasing_anxiety", "recent_count": anxious_count}
        elif anxious_count >= 2:
            return {"trend": "some_anxiety", "recent_count": anxious_count}
        return {"trend": "stable", "recent_count": anxious_count}