"""
用户档案存储模块
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class UserProfileStorage:
    """用户档案存储"""

    def __init__(self, storage_dir: str = "./data/profiles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._init_index()

    def _init_index(self):
        """初始化索引"""
        if not self.index_file.exists():
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_index(self) -> Dict[str, str]:
        """加载索引"""
        with open(self.index_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_index(self, index: Dict[str, str]):
        """保存索引"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def create_profile(self, profile_data: Dict[str, Any]) -> str:
        """创建用户档案，返回用户ID"""
        user_id = str(uuid.uuid4())[:8]
        profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **profile_data,
        }

        # 保存档案文件
        profile_file = self.storage_dir / f"{user_id}.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        # 更新索引
        index = self._load_index()
        index[user_id] = profile_file.name
        self._save_index(index)

        return user_id

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户档案"""
        index = self._load_index()
        if user_id not in index:
            return None

        profile_file = self.storage_dir / index[user_id]
        if not profile_file.exists():
            return None

        with open(profile_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户档案"""
        profile = self.get_profile(user_id)
        if not profile:
            return False

        profile.update(updates)
        profile["updated_at"] = datetime.now().isoformat()

        profile_file = self.storage_dir / f"{user_id}.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        return True

    def delete_profile(self, user_id: str) -> bool:
        """删除用户档案"""
        index = self._load_index()
        if user_id not in index:
            return False

        profile_file = self.storage_dir / index[user_id]
        if profile_file.exists():
            profile_file.unlink()

        del index[user_id]
        self._save_index(index)

        return True