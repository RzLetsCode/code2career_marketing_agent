import time
import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from core.logger import logger


class InstagramPublisher:
    def __init__(self):
        self.base_url = settings.instagram_base_url
        self.user_id = settings.instagram_user_id
        self.headers = {"Authorization": f"Bearer {settings.instagram_access_token}"}

    def _wait_for_container(self, container_id: str, timeout: int = 50) -> bool:
        status_url = f"{self.base_url}/{container_id}"
        params = {"fields": "status_code,status"}
        start = time.time()
        while time.time() - start < timeout:
            res = requests.get(status_url, headers=self.headers, params=params).json()
            status = res.get("status_code")
            if status == "FINISHED":
                return True
            elif status in ["ERROR", "EXPIRED"]:
                logger.error(f"Container {container_id} ingestion failed: {res}")
                return False
            time.sleep(3)
        logger.error(f"Timed out waiting for container {container_id}")
        return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=15))
    def _create_item_container(self, image_url: str) -> str:
        url = f"{self.base_url}/{self.user_id}/media"
        res = requests.post(
            url,
            headers=self.headers,
            data={"image_url": image_url, "is_carousel_item": "true"}
        ).json()
        if "id" not in res:
            raise RuntimeError(f"Error creating slide container: {res}")
        return res["id"]

    def publish_carousel(self, image_urls: List[str], caption: str) -> str:
        logger.info(f"Meta Publisher: Registering {len(image_urls)} slide containers...")
        item_ids = []
        for url in image_urls:
            item_id = self._create_item_container(url)
            item_ids.append(item_id)

        for item_id in item_ids:
            if not self._wait_for_container(item_id):
                raise RuntimeError(f"Slide item {item_id} failed processing.")

        logger.info("Meta Publisher: Creating Master Carousel Container...")
        master_url = f"{self.base_url}/{self.user_id}/media"
        carousel_res = requests.post(
            master_url,
            headers=self.headers,
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(item_ids),
                "caption": caption
            }
        ).json()

        if "id" not in carousel_res:
            raise RuntimeError(f"Failed to create Master Carousel: {carousel_res}")

        master_id = carousel_res["id"]
        if not self._wait_for_container(master_id):
            raise RuntimeError(f"Master container {master_id} not ready.")

        logger.info("Meta Publisher: Publishing carousel live to feed...")
        publish_url = f"{self.base_url}/{self.user_id}/media_publish"
        live_res = requests.post(
            publish_url,
            headers=self.headers,
            data={"creation_id": master_id}
        ).json()

        if "id" not in live_res:
            raise RuntimeError(f"Live publish failed: {live_res}")

        live_id = live_res["id"]
        logger.info(f"Meta Publisher: Carousel LIVE! Media ID: {live_id}")
        return live_id

    def publish_reel(self, video_url: str, caption: str) -> str:
        """Creates an Instagram REELS container, waits for Meta encoding, and publishes live."""
        logger.info("Meta Publisher: Initializing Instagram REELS container...")
        media_url = f"{self.base_url}/{self.user_id}/media"
        res = requests.post(
            media_url,
            headers=self.headers,
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true"
            }
        ).json()

        if "id" not in res:
            raise RuntimeError(f"Failed to create Reel container: {res}")

        container_id = res["id"]
        logger.info(f"Meta Publisher: Waiting for Reel container {container_id} to encode...")
        if not self._wait_for_container(container_id, timeout=180):
            raise RuntimeError(f"Reel container {container_id} failed or timed out during processing.")

        logger.info("Meta Publisher: Publishing Reel live to Instagram...")
        publish_url = f"{self.base_url}/{self.user_id}/media_publish"
        live_res = requests.post(
            publish_url,
            headers=self.headers,
            data={"creation_id": container_id}
        ).json()

        if "id" not in live_res:
            raise RuntimeError(f"Reel live publish failed: {live_res}")

        live_id = live_res["id"]
        logger.info(f"Meta Publisher: Reel LIVE! Media ID: {live_id}")
        return live_id


# Export both names to prevent import mismatches
Publisher = InstagramPublisher