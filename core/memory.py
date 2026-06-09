"""
RAG 增强版长期记忆管理模块
支持：向量检索、语义搜索、长期持久化存储
"""
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from collections import Counter
import hashlib


class RAGMemoryManager:
    """RAG 增强版长期记忆管理器

    存储架构：
    1. JSON 文件：用户档案、技能、目标、里程碑
    2. ChromaDB 向量数据库：对话记忆（支持语义检索）
    3. SQLite：对话日志（可选，用于备份）
    """

    def __init__(
        self,
        user_id: str,
        storage_dir: str = "./data/memory",
        llm=None,  # LangChain LLM instance for summarization
        embedding_model=None,  # Embedding model for vector storage
    ):
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.llm = llm
        self.embedding_model = embedding_model

        # 记忆文件路径
        self.profile_file = self.storage_dir / f"{user_id}_profile.json"
        self.vector_dir = self.storage_dir / "vector_db" / user_id

        # 初始化向量存储
        self._vector_store = None
        self._init_vector_store()

        # 加载或初始化档案
        self.profile = self._load_profile()

    # ==================== 向量存储初始化 ====================

    def _init_vector_store(self):
        """初始化 ChromaDB 向量存储（带降级处理）"""
        self._chroma_client = None
        self._conversation_collection = None
        self._summary_collection = None
        self._user_info_collection = None

        try:
            import chromadb
            from chromadb.config import Settings

            # 创建用户专属的向量数据库
            self.vector_dir.mkdir(parents=True, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.vector_dir),
                settings=Settings(anonymized_telemetry=False)
            )

            # 创建对话记忆集合
            self._conversation_collection = self._chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"hnsw:space": "cosine"}
            )

            # 创建知识摘要集合
            self._summary_collection = self._chroma_client.get_or_create_collection(
                name="summaries",
                metadata={"hnsw:space": "cosine"}
            )

            # 创建用户信息集合
            self._user_info_collection = self._chroma_client.get_or_create_collection(
                name="user_info",
                metadata={"hnsw:space": "cosine"}
            )

        except Exception as e:
            # ChromaDB 不可用时，使用 JSON 降级存储
            print(f"ChromaDB initialization failed, using JSON fallback: {e}")
            self._use_json_fallback = True
            self._json_conversations_file = self.storage_dir / f"{user_id}_conversations.json"
            self._init_json_fallback()
            return

        self._use_json_fallback = False

    def _init_json_fallback(self):
        """初始化 JSON 降级存储"""
        if hasattr(self, '_json_conversations_file') and self._json_conversations_file.exists():
            with open(self._json_conversations_file, "r", encoding="utf-8") as f:
                self._json_conversations = json.load(f)
        else:
            self._json_conversations = {
                "conversations": [],
                "summaries": [],
                "user_info": [],
            }
            self._save_json_fallback()

    def _save_json_fallback(self):
        """保存 JSON 降级存储"""
        if hasattr(self, '_json_conversations_file'):
            with open(self._json_conversations_file, "w", encoding="utf-8") as f:
                json.dump(self._json_conversations, f, ensure_ascii=False, indent=2)

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量"""
        if self.embedding_model:
            try:
                return self.embedding_model.embed_query(text)
            except:
                pass

        # 如果没有嵌入模型，ChromaDB 会使用默认的嵌入函数
        return None

    # ==================== 档案管理 ====================

    def _load_profile(self) -> Dict[str, Any]:
        """加载用户档案"""
        if self.profile_file.exists():
            with open(self.profile_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._init_profile()

    def _init_profile(self) -> Dict[str, Any]:
        """初始化档案结构"""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),

            # 基础信息
            "nickname": "",
            "grade": "",
            "major": "",
            "university": "",
            "target": "",
            "graduation_year": "",

            # 技能追踪
            "skills": {},  # {skill: {level, count, first_seen, last_seen}}

            # 兴趣方向
            "interests": [],

            # 成长目标
            "goals": [],

            # 统计信息
            "stats": {
                "total_conversations": 0,
                "total_messages": 0,
                "days_active": 0,
                "last_active": None,
            },

            # 情绪档案
            "emotion_stats": {
                "dominant_emotions": [],
                "total_negative_events": 0,
                "last_emotion": None,
            },

            # 里程碑
            "milestones": [],
        }

    def _save_profile(self):
        """保存用户档案"""
        self.profile["updated_at"] = datetime.now().isoformat()
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def update_profile(self, updates: Dict[str, Any]):
        """更新用户档案"""
        for key in ["nickname", "grade", "major", "university", "target", "graduation_year"]:
            if key in updates:
                self.profile[key] = updates[key]
        self._save_profile()

    def get_profile(self) -> Dict[str, Any]:
        """获取用户档案"""
        return {
            "nickname": self.profile.get("nickname", ""),
            "grade": self.profile.get("grade", ""),
            "major": self.profile.get("major", ""),
            "university": self.profile.get("university", ""),
            "target": self.profile.get("target", ""),
            "interests": self.profile.get("interests", []),
            "skills": list(self.profile.get("skills", {}).keys()),
            "goals": self.profile.get("goals", []),
        }

    # ==================== 对话记忆（向量存储）====================

    async def add_conversation(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Dict[str, Any] = None
    ):
        """添加对话记忆到向量数据库"""
        timestamp = datetime.now().isoformat()
        conversation_id = str(uuid.uuid4())

        # 更新统计
        self.profile["stats"]["total_conversations"] += 1
        self.profile["stats"]["total_messages"] += 2
        self.profile["stats"]["last_active"] = timestamp

        # 计算活跃天数
        created = datetime.fromisoformat(self.profile["created_at"])
        now = datetime.now()
        self.profile["stats"]["days_active"] = (now - created).days + 1

        # 存储用户消息
        user_doc_id = f"{conversation_id}_user"
        user_content = f"用户: {user_message}"

        if self._conversation_collection is not None:
            try:
                self._conversation_collection.add(
                    ids=[user_doc_id],
                    documents=[user_content],
                    metadatas=[{
                        "role": "user",
                        "timestamp": timestamp,
                        "conversation_id": conversation_id,
                        "user_id": self.user_id,
                        **(metadata or {})
                    }]
                )
            except Exception as e:
                print(f"Error adding user message to vector store: {e}")

        # 存储助手回复
        assistant_doc_id = f"{conversation_id}_assistant"
        assistant_content = f"助手: {assistant_response[:1000]}"  # 截断长回复

        if self._conversation_collection is not None:
            try:
                self._conversation_collection.add(
                    ids=[assistant_doc_id],
                    documents=[assistant_content],
                    metadatas=[{
                        "role": "assistant",
                        "timestamp": timestamp,
                        "conversation_id": conversation_id,
                        "user_id": self.user_id,
                        **(metadata or {})
                    }]
                )
            except Exception as e:
                print(f"Error adding assistant response to vector store: {e}")

        # 更新技能（从消息中提取）
        await self._extract_and_update_skills(user_message)

        # 保存档案
        self._save_profile()

        return conversation_id

    async def _extract_and_update_skills(self, message: str):
        """从消息中提取并更新技能"""
        # 简单的关键词匹配（可以用 LLM 增强）
        tech_keywords = [
            "Python", "Java", "Go", "JavaScript", "TypeScript", "React", "Vue",
            "Node.js", "Spring", "Django", "MySQL", "Redis", "MongoDB",
            "Docker", "Kubernetes", "AWS", "算法", "机器学习", "深度学习",
            "NLP", "CV", "前端", "后端", "全栈", "测试", "运维",
        ]

        message_lower = message.lower()
        for skill in tech_keywords:
            if skill.lower() in message_lower:
                if skill not in self.profile["skills"]:
                    self.profile["skills"][skill] = {
                        "level": "beginner",
                        "count": 1,
                        "first_seen": datetime.now().isoformat(),
                        "last_seen": datetime.now().isoformat(),
                    }
                else:
                    self.profile["skills"][skill]["count"] += 1
                    self.profile["skills"][skill]["last_seen"] = datetime.now().isoformat()
                    # 更新熟练度
                    count = self.profile["skills"][skill]["count"]
                    if count >= 10:
                        self.profile["skills"][skill]["level"] = "expert"
                    elif count >= 5:
                        self.profile["skills"][skill]["level"] = "intermediate"

    # ==================== RAG 语义检索 ====================

    def search_memories(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Dict = None
    ) -> List[Dict[str, Any]]:
        """语义搜索相关记忆"""
        if self._conversation_collection is None:
            return []

        try:
            # 构建查询条件
            where_filter = {"user_id": self.user_id}
            if filter_metadata:
                where_filter.update(filter_metadata)

            results = self._conversation_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )

            # 格式化结果
            memories = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    })

            return memories

        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近对话"""
        if self._conversation_collection is None:
            return []

        try:
            # 获取所有对话，按时间排序
            results = self._conversation_collection.get(
                where={"user_id": self.user_id},
                limit=limit * 2,  # 用户+助手消息
            )

            if not results or not results.get("documents"):
                return []

            # 合并并排序
            conversations = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results.get("metadatas") else {}
                conversations.append({
                    "content": doc,
                    "timestamp": metadata.get("timestamp", ""),
                    "role": metadata.get("role", "unknown"),
                })

            # 按时间排序
            conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return conversations[:limit]

        except Exception as e:
            print(f"Error getting recent conversations: {e}")
            return []

    # ==================== 记忆摘要（LLM 增强）====================

    async def generate_summary(self, days: int = 7) -> str:
        """生成指定时间段的记忆摘要"""
        if not self.llm:
            return ""

        # 获取最近对话
        recent = self.get_recent_conversations(limit=20)
        if not recent:
            return ""

        # 构建摘要提示
        conversation_text = "\n".join([
            f"{c['role']}: {c['content']}"
            for c in recent[:10]
        ])

        try:
            from langchain_core.messages import HumanMessage
            summary_prompt = f"""请分析以下用户与AI助手的对话记录，生成简洁的记忆摘要：

{conversation_text}

请提取：
1. 用户关注的主要话题
2. 用户提到的技能或学习方向
3. 用户的情绪状态
4. 任何重要的里程碑或成就

用简洁的中文回答（不超过200字）："""

            response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
            summary = response.content

            # 存储摘要到向量数据库
            if self._summary_collection is not None:
                summary_id = str(uuid.uuid4())
                self._summary_collection.add(
                    ids=[summary_id],
                    documents=[summary],
                    metadatas=[{
                        "timestamp": datetime.now().isoformat(),
                        "period_days": days,
                        "user_id": self.user_id,
                    }]
                )

            return summary

        except Exception as e:
            print(f"Error generating summary: {e}")
            return ""

    def get_summaries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取历史摘要"""
        if self._summary_collection is None:
            return []

        try:
            results = self._summary_collection.get(
                where={"user_id": self.user_id},
                limit=limit,
            )

            summaries = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results.get("metadatas") else {}
                    summaries.append({
                        "summary": doc,
                        "timestamp": metadata.get("timestamp", ""),
                    })

            return sorted(summaries, key=lambda x: x["timestamp"], reverse=True)

        except Exception as e:
            print(f"Error getting summaries: {e}")
            return []

    # ==================== 情绪追踪 ====================

    async def record_emotion(self, emotion: str, intensity: float, trigger: str):
        """记录情绪事件"""
        # 存储到用户信息集合
        if self._user_info_collection is not None:
            emotion_id = str(uuid.uuid4())
            self._user_info_collection.add(
                ids=[emotion_id],
                documents=[f"情绪: {emotion}, 触发: {trigger[:100]}"],
                metadatas=[{
                    "type": "emotion",
                    "emotion": emotion,
                    "intensity": intensity,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": self.user_id,
                }]
            )

        # 更新统计
        negative_emotions = ["anxious", "frustrated", "sad", "worried", "stressed", "焦虑", "沮丧", "难过"]
        if emotion in negative_emotions:
            self.profile["emotion_stats"]["total_negative_events"] += 1

        self.profile["emotion_stats"]["last_emotion"] = {
            "emotion": emotion,
            "timestamp": datetime.now().isoformat(),
        }

        self._save_profile()

    def get_emotion_trend(self) -> Dict[str, Any]:
        """获取情绪趋势"""
        if self._user_info_collection is None:
            return {"trend": "unknown", "data": []}

        try:
            results = self._user_info_collection.get(
                where={
                    "user_id": self.user_id,
                    "type": "emotion"
                },
                limit=20,
            )

            if not results or not results.get("documents"):
                return {"trend": "stable", "data": []}

            emotions = []
            negative_emotions = ["anxious", "frustrated", "sad", "worried", "stressed", "焦虑", "沮丧", "难过"]

            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results.get("metadatas") else {}
                emotions.append({
                    "emotion": metadata.get("emotion", "unknown"),
                    "intensity": metadata.get("intensity", 0.5),
                    "timestamp": metadata.get("timestamp", ""),
                })

            # 计算趋势
            negative_count = sum(1 for e in emotions if e["emotion"] in negative_emotions)
            total = len(emotions)

            if total == 0:
                trend = "stable"
            elif negative_count / total >= 0.5:
                trend = "concerning"
            elif negative_count / total >= 0.3:
                trend = "needs_attention"
            else:
                trend = "stable"

            return {
                "trend": trend,
                "negative_ratio": negative_count / total if total > 0 else 0,
                "recent_emotions": emotions[:5],
                "total_events": len(emotions),
            }

        except Exception as e:
            print(f"Error getting emotion trend: {e}")
            return {"trend": "unknown", "data": []}

    # ==================== 技能管理 ====================

    async def update_skills(self, skills: List[str], context: str = ""):
        """更新技能列表"""
        for skill in skills:
            if skill not in self.profile["skills"]:
                self.profile["skills"][skill] = {
                    "level": "beginner",
                    "count": 1,
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                }
            else:
                self.profile["skills"][skill]["count"] += 1
                self.profile["skills"][skill]["last_seen"] = datetime.now().isoformat()

        self._save_profile()

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """获取所有技能"""
        result = []
        for skill, data in self.profile.get("skills", {}).items():
            result.append({
                "name": skill,
                "level": data.get("level", "beginner"),
                "count": data.get("count", 0),
            })
        return sorted(result, key=lambda x: x["count"], reverse=True)

    # ==================== 目标管理 ====================

    def add_goal(self, goal: str, deadline: str = None):
        """添加目标"""
        goal_entry = {
            "goal": goal,
            "status": "active",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "deadline": deadline,
        }
        self.profile["goals"].append(goal_entry)
        self._save_profile()

    def get_active_goals(self) -> List[Dict]:
        """获取活跃目标"""
        return [g for g in self.profile.get("goals", []) if g.get("status") == "active"]

    # ==================== 里程碑管理 ====================

    def add_milestone(self, event_type: str, description: str):
        """添加里程碑"""
        milestone = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
        }
        self.profile["milestones"].append(milestone)
        self._save_profile()

    def get_recent_milestones(self, limit: int = 10) -> List[Dict]:
        """获取最近里程碑"""
        return self.profile.get("milestones", [])[-limit:]

    # ==================== 知识节点 ====================

    async def add_knowledge_node(self, entity: str, entity_type: str, relations: List[str]):
        """添加知识节点到向量数据库"""
        if self._user_info_collection is None:
            return

        node_id = str(uuid.uuid4())
        content = f"{entity_type}: {entity}, 相关: {', '.join(relations)}"

        self._user_info_collection.add(
            ids=[node_id],
            documents=[content],
            metadatas=[{
                "type": "knowledge",
                "entity": entity,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
            }]
        )

    # ==================== 综合上下文（用于 LLM Prompt）====================

    def get_context_for_prompt(self) -> str:
        """生成用于 LLM Prompt 的记忆上下文"""
        parts = []

        # 用户档案
        profile = self.get_profile()
        if profile.get("nickname"):
            parts.append(f"用户昵称: {profile['nickname']}")
        if profile.get("grade"):
            parts.append(f"年级: {profile['grade']}")
        if profile.get("major"):
            parts.append(f"专业: {profile['major']}")
        if profile.get("target"):
            parts.append(f"求职目标: {profile['target']}")

        # 技能
        skills = self.get_all_skills()
        if skills:
            skills_str = ", ".join([f"{s['name']}({s['level']})" for s in skills[:5]])
            parts.append(f"已知技能: {skills_str}")

        # 目标
        goals = self.get_active_goals()
        if goals:
            goals_str = "; ".join([g["goal"] for g in goals[:3]])
            parts.append(f"当前目标: {goals_str}")

        # 情绪趋势
        emotion = self.get_emotion_trend()
        if emotion["trend"] != "stable":
            parts.append(f"情绪状态: {emotion['trend']}")

        # 统计信息
        stats = self.profile.get("stats", {})
        if stats.get("total_conversations", 0) > 0:
            parts.append(f"已对话次数: {stats['total_conversations']}")

        return "\n".join(parts)

    def get_memory_context(self) -> Dict[str, Any]:
        """获取完整记忆上下文（兼容旧接口）"""
        return {
            "profile": self.get_profile(),
            "skills": [s["name"] for s in self.get_all_skills()],
            "interests": self.profile.get("interests", []),
            "goals": [g["goal"] for g in self.get_active_goals()],
            "recent_emotions": self.get_emotion_trend().get("recent_emotions", []),
            "milestones": self.get_recent_milestones(),
        }

    # ==================== 短期记忆（兼容接口）====================

    async def add_short_term(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Dict[str, Any] = None
    ):
        """添加短期记忆（实际存储到向量数据库）"""
        return await self.add_conversation(user_message, assistant_response, metadata)

    # ==================== 数据导出/导入 ====================

    def export_memories(self) -> Dict[str, Any]:
        """导出所有记忆数据"""
        return {
            "profile": self.profile,
            "recent_conversations": self.get_recent_conversations(limit=50),
            "summaries": self.get_summaries(limit=10),
            "exported_at": datetime.now().isoformat(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        stats = self.profile.get("stats", {})
        return {
            "total_conversations": stats.get("total_conversations", 0),
            "total_messages": stats.get("total_messages", 0),
            "days_active": stats.get("days_active", 0),
            "skills_count": len(self.profile.get("skills", {})),
            "goals_count": len(self.get_active_goals()),
            "milestones_count": len(self.profile.get("milestones", [])),
            "vector_count": self._conversation_collection.count() if self._conversation_collection else 0,
        }


# 保持向后兼容
MemoryManager = RAGMemoryManager
EnhancedMemoryManager = RAGMemoryManager