import os
import requests
from config.settings import settings
from core.logger import logger


class LinkedInPublisher:
    """Publishes technical PDF document carousels to LinkedIn feeds."""

    def __init__(self):
        self.access_token = settings.linkedin_access_token
        self.author_urn = settings.linkedin_author_urn
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    def publish_document(self, pdf_path: str, title: str, commentary: str) -> str:
        if not self.access_token or not self.author_urn:
            logger.info("LinkedIn: Credentials not set in settings. Skipping LinkedIn syndication.")
            return ""

        if not os.path.exists(pdf_path):
            logger.error(f"LinkedIn: Target PDF not found at {pdf_path}")
            return ""

        logger.info(f"LinkedIn: Initializing document upload for '{title}'...")

        # Step 1: Register upload with LinkedIn Asset API
        init_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        init_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
                "owner": self.author_urn,
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ]
            }
        }

        init_res = requests.post(init_url, json=init_payload, headers=self.headers).json()
        if "value" not in init_res:
            logger.error(f"LinkedIn upload registration failed: {init_res}")
            return ""

        upload_url = init_res["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = init_res["value"]["asset"]

        # Step 2: Upload raw PDF bytes
        logger.info("LinkedIn: Uploading document binary...")
        with open(pdf_path, "rb") as f:
            upload_res = requests.put(
                upload_url,
                data=f,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

        if upload_res.status_code not in [200, 201]:
            logger.error(f"LinkedIn binary upload failed with status {upload_res.status_code}")
            return ""

        # Step 3: Create UGC Post with document attachment
        logger.info("LinkedIn: Publishing document post to feed...")
        share_url = "https://api.linkedin.com/v2/ugcPosts"
        post_payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": commentary},
                    "shareMediaCategory": "DOCUMENT",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": commentary[:200]},
                            "media": asset_urn,
                            "title": {"text": title}
                        }
                    ]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        post_res = requests.post(share_url, json=post_payload, headers=self.headers).json()
        post_id = post_res.get("id", "")
        if post_id:
            logger.info(f"LinkedIn: Document published successfully! Post URN: {post_id}")
        else:
            logger.error(f"LinkedIn post creation failed: {post_res}")
        return post_id