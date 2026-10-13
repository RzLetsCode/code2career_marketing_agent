import os
import requests
from dotenv import load_dotenv

load_dotenv()


class LinkedInPublisher:
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
        self.author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "").strip()
        self.api_version = "202601"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "LinkedIn-Version": self.api_version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

    def initialize_document_upload(self) -> tuple[str, str]:
        """Step 1: Reserve a document asset URN and get an upload URL."""
        url = "https://api.linkedin.com/rest/documents?action=initializeUpload"
        payload = {
            "initializeUploadRequest": {
                "owner": self.author_urn
            }
        }
        res = requests.post(url, headers=self.headers, json=payload)
        res.raise_for_status()
        data = res.json()["value"]
        return data["uploadUrl"], data["document"]

    def upload_pdf_binary(self, upload_url: str, pdf_path: str):
        """Step 2: Stream the binary PDF file to LinkedIn storage."""
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        upload_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/octet-stream",
        }
        res = requests.put(upload_url, headers=upload_headers, data=pdf_bytes)
        res.raise_for_status()

    def create_document_post(self, document_urn: str, caption: str, title: str) -> str:
        """Step 3: Publish the post referencing the uploaded document."""
        url = "https://api.linkedin.com/rest/posts"
        payload = {
            "author": self.author_urn,
            "commentary": caption,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "content": {
                "media": {
                    "title": title,
                    "id": document_urn
                }
            },
            "lifecycleState": "PUBLISHED"
        }
        res = requests.post(url, headers=self.headers, json=payload)
        res.raise_for_status()
        return res.headers.get("x-restli-id", "urn:li:post:success")

    def publish_carousel(self, pdf_path: str, caption: str, title: str = "Carousel") -> str:
        """Runs the full upload sequence and returns the published post URN."""
        print(f"[LinkedIn] Initializing document upload for: {pdf_path}")
        upload_url, document_urn = self.initialize_document_upload()

        print(f"[LinkedIn] Uploading PDF binary to storage...")
        self.upload_pdf_binary(upload_url, pdf_path)

        print(f"[LinkedIn] Publishing feed post with document {document_urn}...")
        post_urn = self.create_document_post(document_urn, caption, title)
        return post_urn