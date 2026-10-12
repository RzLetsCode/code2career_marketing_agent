import json
import os
import tempfile
from typing import List, Dict, Any
from config.settings import settings
from core.logger import logger

class StateManager:
    def __init__(self, filepath: str = settings.history_file_path):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"published_topics": [], "logs": []}, f, indent=2)

    def get_published_topics(self) -> List[str]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [str(item) for item in data]
                elif isinstance(data, dict):
                    return data.get("published_topics", [])
                return []
        except Exception as e:
            logger.error(f"Failed to read state file: {e}")
            return []

    def record_publication(self, topic: str, media_id: str, keyword: str):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    data = {"published_topics": raw, "logs": []}
                elif isinstance(raw, dict):
                    data = raw
                else:
                    data = {"published_topics": [], "logs": []}
        except Exception:
            data = {"published_topics": [], "logs": []}

        data.setdefault("published_topics", []).append(topic)
        data.setdefault("logs", []).append({
            "topic": topic,
            "media_id": media_id,
            "trigger_keyword": keyword
        })

        dir_name = os.path.dirname(os.path.abspath(self.filepath))
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2)
            temp_name = tf.name

        os.replace(temp_name, self.filepath)
        logger.info(f"State updated: Topic '{topic}' saved atomically.")