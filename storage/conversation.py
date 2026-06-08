"""
对话历史存储模块
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class ConversationStorage:
    """对话历史存储"""

    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_dir / "conversations.db"
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON conversations(created_at)
            """)
            conn.commit()

    def save_message(
        self,
        user_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None
    ) -> int:
        """保存消息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO conversations (user_id, role, content, agent_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, role, content, agent_name))
            conn.commit()
            return cursor.lastrowid

    def get_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取对话历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT role, content, agent_name, created_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]

    def clear_history(self, user_id: str) -> bool:
        """清空对话历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM conversations WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            return True

    def get_message_count(self, user_id: str) -> int:
        """获取消息数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM conversations WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()[0]