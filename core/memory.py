"""
增强版长期记忆管理模块
支持：向量检索、LLM摘要、知识图谱、遗忘机制
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from collections import Counter
import hashlib


class EnhancedMemoryManager:
    """增强版长期记忆管理器"""

    def __init__(
        self,
        user_id: str,
        storage_dir: str = "./data/memory",
        llm=None,  # LangChain LLM instance
        vector_store=None,  # Vector store for semantic retrieval
    ):
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.llm = llm
        self.vector_store = vector_store

        # 记忆文件路径
        self.memory_file = self.storage_dir / f"{user_id}_memory.json"
        self.index_file = self.storage_dir / f"{user_id}_index.json"

        # 加载或初始化记忆
        self.memory = self._load_memory()
        self.index = self._load_index()

    def _load_memory(self) -> Dict[str, Any]:
        """加载记忆"""
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._init_memory()

    def _load_index(self) -> Dict[str, Any]:
        """加载索引"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "skill_index": {},  # 技能 -> 对话ID映射
            "topic_index": {},  # 主题 -> 对话ID映射
            "emotion_index": {},  # 情绪类型 -> 时间戳映射
            "entity_index": {},  # 实体 -> 相关记忆映射
        }

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
                "graduation_year": "",
            },

            # 技能追踪（带熟练度）
            "skills": {},  # {skill_name: {level, last_mentioned, practice_count}}

            # 兴趣方向
            "interests": [],

            # 成长目标（带进度）
            "goals": [],  # [{goal, status, progress, created_at, deadline}]

            # 短期记忆（最近对话）
            "short_term": [],  # 最近5轮对话

            # 长期记忆（压缩摘要）
            "long_term": [],  # LLM生成的摘要

            # 情绪档案
            "emotion_profile": {
                "dominant_emotions": [],
                "emotion_history": [],
                "triggers": {},  # 情绪触发词统计
            },

            # 关键里程碑
            "milestones": [],

            # 学习路径
            "learning_path": {
                "completed": [],
                "in_progress": [],
                "recommended": [],
            },

            # 知识图谱节点
            "knowledge_nodes": {},  # {entity: {type, relations, importance}}
        }

    def _save_memory(self):
        """保存记忆"""
        self.memory["updated_at"] = datetime.now().isoformat()
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def _save_index(self):
        """保存索引"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    # ==================== 档案管理 ====================

    def update_profile(self, profile: Dict[str, Any]):
        """更新用户档案"""
        self.memory["profile"].update(profile)
        self._save_memory()

    def get_profile(self) -> Dict[str, Any]:
        """获取用户档案"""
        return self.memory.get("profile", {})

    # ==================== 技能追踪 ====================

    async def update_skills(self, skills: List[str], context: str = ""):
        """更新技能列表，带上下文"""
        now = datetime.now().isoformat()
        for skill in skills:
            if skill not in self.memory["skills"]:
                self.memory["skills"][skill] = {
                    "level": "beginner",
                    "first_mentioned": now,
                    "last_mentioned": now,
                    "practice_count": 1,
                    "contexts": [context[:100]] if context else [],
                }
            else:
                self.memory["skills"][skill]["last_mentioned"] = now
                self.memory["skills"][skill]["practice_count"] += 1
                if context and len(self.memory["skills"][skill]["contexts"]) < 5:
                    self.memory["skills"][skill]["contexts"].append(context[:100])

        # 更新索引
        for skill in skills:
            if skill not in self.index["skill_index"]:
                self.index["skill_index"][skill] = []
            self.index["skill_index"][skill].append(now)

        self._save_memory()
        self._save_index()

    def get_skill_level(self, skill: str) -> str:
        """获取技能熟练度"""
        skill_data = self.memory["skills"].get(skill, {})
        count = skill_data.get("practice_count", 0)
        if count >= 10:
            return "expert"
        elif count >= 5:
            return "intermediate"
        elif count >= 2:
            return "beginner"
        return "interested"

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """获取所有技能及其熟练度"""
        result = []
        for skill, data in self.memory["skills"].items():
            result.append({
                "name": skill,
                "level": self.get_skill_level(skill),
                "practice_count": data.get("practice_count", 0),
            })
        return sorted(result, key=lambda x: x["practice_count"], reverse=True)

    # ==================== 短期记忆 ====================

    async def add_short_term(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Dict[str, Any] = None
    ):
        """添加短期记忆"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response[:500],  # 截断
            "metadata": metadata or {},
        }
        self.memory["short_term"].append(entry)

        # 只保留最近10轮
        if len(self.memory["short_term"]) > 10:
            # 将旧记忆压缩到长期记忆
            old_entries = self.memory["short_term"][:-10]
            await self._consolidate_to_long_term(old_entries)
            self.memory["short_term"] = self.memory["short_term"][-10:]

        self._save_memory()

    def get_short_term_context(self, limit: int = 5) -> str:
        """获取短期记忆上下文"""
        recent = self.memory["short_term"][-limit:]
        if not recent:
            return ""

        context_parts = []
        for entry in recent:
            context_parts.append(f"用户: {entry['user'][:100]}")
            context_parts.append(f"助手: {entry['assistant'][:100]}")

        return "\n".join(context_parts)

    # ==================== 长期记忆（LLM摘要）====================

    async def _consolidate_to_long_term(self, entries: List[Dict]):
        """将短期记忆压缩为长期记忆"""
        if not entries or not self.llm:
            return

        # 使用LLM生成摘要
        conversation_text = "\n".join([
            f"用户: {e['user']}\n助手: {e['assistant']}"
            for e in entries
        ])

        try:
            from langchain_core.messages import HumanMessage
            summary_prompt = f"""请将以下对话压缩为简洁的记忆摘要，保留关键信息：

{conversation_text}

摘要格式：
1. 主题：一句话概括
2. 关键信息：提取的用户信息、技能、目标等
3. 重要事件：值得记住的对话亮点
"""

            response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
            summary = response.content

            long_term_entry = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "original_count": len(entries),
                "date_range": {
                    "start": entries[0]["timestamp"],
                    "end": entries[-1]["timestamp"],
                }
            }
            self.memory["long_term"].append(long_term_entry)

            # 只保留最近20条长期记忆
            if len(self.memory["long_term"]) > 20:
                self.memory["long_term"] = self.memory["long_term"][-20:]

        except Exception as e:
            print(f"Memory consolidation error: {e}")

    def get_long_term_context(self) -> str:
        """获取长期记忆摘要"""
        summaries = self.memory.get("long_term", [])
        if not summaries:
            return ""

        return "\n\n".join([
            f"[{s['timestamp'][:10]}] {s['summary']}"
            for s in summaries[-5:]  # 最近5条摘要
        ])

    # ==================== 情绪追踪 ====================

    async def record_emotion(self, emotion: str, intensity: float, trigger: str):
        """记录情绪事件"""
        now = datetime.now().isoformat()

        # 记录历史
        event = {
            "timestamp": now,
            "emotion": emotion,
            "intensity": intensity,
            "trigger": trigger[:100],
        }
        self.memory["emotion_profile"]["emotion_history"].append(event)

        # 只保留最近30条
        if len(self.memory["emotion_profile"]["emotion_history"]) > 30:
            self.memory["emotion_profile"]["emotion_history"] = \
                self.memory["emotion_profile"]["emotion_history"][-30:]

        # 更新触发词统计
        trigger_words = trigger.split()[:5]
        for word in trigger_words:
            if len(word) > 1:
                self.memory["emotion_profile"]["triggers"][word] = \
                    self.memory["emotion_profile"]["triggers"].get(word, 0) + 1

        # 更新主导情绪
        self._update_dominant_emotions()

        # 更新索引
        if emotion not in self.index["emotion_index"]:
            self.index["emotion_index"][emotion] = []
        self.index["emotion_index"][emotion].append(now)

        self._save_memory()
        self._save_index()

    def _update_dominant_emotions(self):
        """更新主导情绪"""
        history = self.memory["emotion_profile"]["emotion_history"]
        if not history:
            return

        recent = history[-20:]  # 最近20次
        emotion_counts = Counter(e["emotion"] for e in recent)

        self.memory["emotion_profile"]["dominant_emotions"] = [
            {"emotion": e, "count": c}
            for e, c in emotion_counts.most_common(3)
        ]

    def get_emotion_trend(self) -> Dict[str, Any]:
        """获取情绪趋势分析"""
        history = self.memory["emotion_profile"]["emotion_history"]
        if not history:
            return {"trend": "unknown", "data": []}

        recent = history[-10:]
        negative_emotions = ["anxious", "frustrated", "sad", "worried", "stressed"]
        negative_count = sum(1 for e in recent if e["emotion"] in negative_emotions)

        # 计算平均强度
        avg_intensity = sum(e.get("intensity", 0.5) for e in recent) / len(recent)

        if negative_count >= 6:
            trend = "concerning"
        elif negative_count >= 3:
            trend = "needs_attention"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "negative_ratio": negative_count / len(recent),
            "avg_intensity": avg_intensity,
            "dominant": self.memory["emotion_profile"]["dominant_emotions"],
            "triggers": dict(Counter(
                self.memory["emotion_profile"]["triggers"]
            ).most_common(5)),
        }

    # ==================== 知识图谱 ====================

    async def add_knowledge_node(self, entity: str, entity_type: str, relations: List[str]):
        """添加知识节点"""
        if entity not in self.memory["knowledge_nodes"]:
            self.memory["knowledge_nodes"][entity] = {
                "type": entity_type,
                "relations": relations,
                "importance": 1,
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }
        else:
            self.memory["knowledge_nodes"][entity]["relations"].extend(relations)
            self.memory["knowledge_nodes"][entity]["importance"] += 1
            self.memory["knowledge_nodes"][entity]["last_updated"] = datetime.now().isoformat()

        # 更新实体索引
        if entity not in self.index["entity_index"]:
            self.index["entity_index"][entity] = []
        self.index["entity_index"][entity].append(datetime.now().isoformat())

        self._save_memory()
        self._save_index()

    def get_related_knowledge(self, entity: str) -> List[str]:
        """获取相关知识点"""
        node = self.memory["knowledge_nodes"].get(entity)
        if node:
            return node.get("relations", [])
        return []

    # ==================== 里程碑管理 ====================

    def add_milestone(self, event_type: str, description: str, importance: int = 1):
        """添加里程碑"""
        milestone = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "importance": importance,
        }
        self.memory["milestones"].append(milestone)
        self._save_memory()

    def get_recent_milestones(self, limit: int = 10) -> List[Dict]:
        """获取最近里程碑"""
        return self.memory.get("milestones", [])[-limit:]

    # ==================== 目标管理 ====================

    def add_goal(self, goal: str, deadline: str = None):
        """添加目标"""
        goal_entry = {
            "goal": goal,
            "status": "active",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "deadline": deadline,
            "sub_tasks": [],
        }
        self.memory["goals"].append(goal_entry)
        self._save_memory()

    def update_goal_progress(self, goal_index: int, progress: int):
        """更新目标进度"""
        if 0 <= goal_index < len(self.memory["goals"]):
            self.memory["goals"][goal_index]["progress"] = min(100, progress)
            if progress >= 100:
                self.memory["goals"][goal_index]["status"] = "completed"
                self.add_milestone("goal_completed", self.memory["goals"][goal_index]["goal"])
            self._save_memory()

    def get_active_goals(self) -> List[Dict]:
        """获取活跃目标"""
        return [g for g in self.memory.get("goals", []) if g["status"] == "active"]

    # ==================== 综合上下文 ====================

    def get_full_context(self) -> Dict[str, Any]:
        """获取完整记忆上下文"""
        return {
            "profile": self.get_profile(),
            "skills": self.get_all_skills(),
            "interests": self.memory.get("interests", []),
            "active_goals": self.get_active_goals(),
            "recent_conversations": self.get_short_term_context(3),
            "long_term_summary": self.get_long_term_context(),
            "emotion_trend": self.get_emotion_trend(),
            "recent_milestones": self.get_recent_milestones(5),
            "knowledge_entities": list(self.memory.get("knowledge_nodes", {}).keys())[:10],
        }

    def get_context_for_prompt(self) -> str:
        """生成用于LLM Prompt的记忆上下文"""
        context = self.get_full_context()

        parts = []

        # 用户档案
        profile = context["profile"]
        if profile.get("nickname"):
            parts.append(f"用户昵称: {profile['nickname']}")
        if profile.get("grade"):
            parts.append(f"年级: {profile['grade']}")
        if profile.get("major"):
            parts.append(f"专业: {profile['major']}")
        if profile.get("target"):
            parts.append(f"求职目标: {profile['target']}")

        # 技能
        if context["skills"]:
            skills_str = ", ".join([f"{s['name']}({s['level']})" for s in context["skills"][:5]])
            parts.append(f"已知技能: {skills_str}")

        # 目标
        if context["active_goals"]:
            goals_str = "; ".join([g["goal"] for g in context["active_goals"][:3]])
            parts.append(f"当前目标: {goals_str}")

        # 情绪趋势
        emotion = context["emotion_trend"]
        if emotion["trend"] != "stable":
            parts.append(f"情绪状态: {emotion['trend']}")

        # 长期记忆
        if context["long_term_summary"]:
            parts.append(f"历史摘要: {context['long_term_summary'][:300]}")

        return "\n".join(parts)

    # ==================== 遗忘机制 ====================

    def apply_forgetting(self):
        """应用遗忘机制 - 清理过期或低重要性的记忆"""
        now = datetime.now()
        retention_days = 90  # 保留90天

        # 清理过期的情绪历史
        emotion_history = self.memory["emotion_profile"]["emotion_history"]
        cutoff = (now - timedelta(days=retention_days)).isoformat()
        self.memory["emotion_profile"]["emotion_history"] = [
            e for e in emotion_history
            if e["timestamp"] > cutoff
        ]

        # 清理低重要性的知识节点
        knowledge_nodes = self.memory["knowledge_nodes"]
        self.memory["knowledge_nodes"] = {
            k: v for k, v in knowledge_nodes.items()
            if v["importance"] >= 2 or v["last_updated"] > cutoff
        }

        self._save_memory()

    # ==================== 向量检索（如果有向量数据库）====================

    async def semantic_search(self, query: str, k: int = 5) -> List[Dict]:
        """语义搜索相关记忆"""
        if not self.vector_store:
            return []

        try:
            results = await self.vector_store.asimilarity_search(query, k=k)
            return [{"content": r.page_content, "metadata": r.metadata} for r in results]
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    async def add_to_vector_store(self, text: str, metadata: Dict = None):
        """添加到向量数据库"""
        if not self.vector_store:
            return

        try:
            await self.vector_store.aadd_texts([text], metadatas=[metadata or {}])
        except Exception as e:
            print(f"Vector store add error: {e}")


# 保持向后兼容
MemoryManager = EnhancedMemoryManager