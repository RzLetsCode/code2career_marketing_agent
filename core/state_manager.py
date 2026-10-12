import json
import os
import tempfile
from datetime import datetime
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
        """Extracts clean topic strings whether stored as raw strings or objects."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_topics = data.get("published_topics", [])
                
                clean_topics = []
                for item in raw_topics:
                    if isinstance(item, str):
                        clean_topics.append(item.strip())
                    elif isinstance(item, dict) and "topic" in item:
                        clean_topics.append(item["topic"].strip())
                return clean_topics
        except Exception as e:
            logger.error(f"Failed to read state file: {e}")
            return []

    def record_publication(self, topic: str, media_id: str, keyword: str):
        """Saves a structured log and updates published_topics."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"published_topics": [], "logs": []}

        # Keep published_topics as clean strings for simple deduplication
        if topic not in data.get("published_topics", []):
            data.setdefault("published_topics", []).append(topic)

        # Keep rich history in logs
        data.setdefault("logs", []).append({
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "topic": topic,
            "media_id": media_id,
            "trigger_keyword": keyword
        })

        dir_name = os.path.dirname(os.path.abspath(self.filepath))
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2)
            temp_name = tf.name

        os.replace(temp_name, self.filepath)
        logger.info(f"State saved cleanly: '{topic}'")
