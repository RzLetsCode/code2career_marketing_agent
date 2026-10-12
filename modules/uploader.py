import cloudinary
import cloudinary.uploader
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from core.logger import logger

class CloudinaryUploader:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def _upload_single(self, filepath: str) -> str:
        res = cloudinary.uploader.upload(
            filepath,
            folder="c2c_automated_carousels",
            overwrite=True,
            resource_type="image"
        )
        url = res.get("secure_url")
        if not url:
            raise ValueError(f"Cloudinary did not return a secure_url for {filepath}")
        return url

    def upload_all(self, file_paths: List[str]) -> List[str]:
        logger.info(f"Cloudinary: Uploading {len(file_paths)} slides to cloud storage...")
        urls = []
        for path in file_paths:
            secure_url = self._upload_single(path)
            urls.append(secure_url)
        logger.info("Cloudinary: All slides uploaded successfully.")
        return urls

# Export both names to prevent import mismatches
Uploader = CloudinaryUploader