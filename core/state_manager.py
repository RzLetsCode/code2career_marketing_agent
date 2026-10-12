import json
import os
import tempfile
from datetime import datetime, timezone
from typing import List, Dict, Any
from config.settings import settings
from core.logger import logger


class StateManager:
    """Manages content history, publication logs, and topic deduplication."""

    def __init__(self, filepath: str = settings.history_file_path):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"published_topics": [], "logs": []}, f, indent=2)

    def get_published_topics(self) -> List[str]:
        """Extracts sanitized topic strings from any legacy schema format."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                raw_topics = data
            elif isinstance(data, dict):
                raw_topics = data.get("published_topics", [])
            else:
                raw_topics = []

            sanitized_topics = []
            for item in raw_topics:
                if isinstance(item, str) and item.strip():
                    sanitized_topics.append(item.strip())
                elif isinstance(item, dict) and "topic" in item and item["topic"]:
                    sanitized_topics.append(str(item["topic"]).strip())

            return sanitized_topics
        except Exception as e:
            logger.error(f"Failed to read state file: {e}")
            return []

    def record_publication(self, topic: str, media_id: str, keyword: str):
        """Atomically persists the publication event and logs metadata."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if isinstance(raw_data, list):
                clean_topics = [
                    t if isinstance(t, str) else t.get("topic", "")
                    for t in raw_data
                ]
                data = {"published_topics": clean_topics, "logs": []}
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                data = {"published_topics": [], "logs": []}
        except Exception:
            data = {"published_topics": [], "logs": []}

        clean_topic = topic.strip()
        data.setdefault("published_topics", [])
        if clean_topic not in data["published_topics"]:
            data["published_topics"].append(clean_topic)

        data.setdefault("logs", []).append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": clean_topic,
            "media_id": media_id,
            "trigger_keyword": keyword.strip().upper()
        })

        # Atomic write to prevent file corruption during OS process termination
        dir_name = os.path.dirname(os.path.abspath(self.filepath))
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name

        os.replace(temp_name, self.filepath)
        logger.info(f"State updated: Topic '{clean_topic}' recorded atomically.")
