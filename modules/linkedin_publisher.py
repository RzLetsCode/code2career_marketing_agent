import os
import time
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

    # --- DOCUMENT CAROUSEL METHODS ---
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
        print(f"    [LinkedIn] Initializing document upload for: {pdf_path}", flush=True)
        upload_url, document_urn = self.initialize_document_upload()

        print("    [LinkedIn] Uploading PDF binary to storage...", flush=True)
        self.upload_pdf_binary(upload_url, pdf_path)

        print(f"    [LinkedIn] Publishing feed post with document {document_urn}...", flush=True)
        post_urn = self.create_document_post(document_urn, caption, title)
        return post_urn

    # --- NATIVE VIDEO METHODS ---
    def publish_video(self, video_path: str, caption: str, title: str = "Architecture Breakdown") -> str:
        """Uploads and publishes a native MP4 video post to LinkedIn."""
        file_size = os.path.getsize(video_path)
        print(f"    [LinkedIn Video] Initializing upload ({file_size} bytes)...", flush=True)

        # 1. Initialize Video Upload
        init_url = "https://api.linkedin.com/rest/videos?action=initializeUpload"
        init_payload = {
            "initializeUploadRequest": {
                "owner": self.author_urn,
                "fileSizeBytes": file_size,
                "uploadCaptions": False,
                "uploadThumbnail": False
            }
        }
        res = requests.post(init_url, headers=self.headers, json=init_payload)
        res.raise_for_status()
        val = res.json()["value"]
        video_urn = val["video"]
        upload_token = val.get("uploadToken", "")
        instructions = val["uploadInstructions"]

        # 2. Upload Binary Chunks & Record ETags
        print("    [LinkedIn Video] Streaming MP4 chunks...", flush=True)
        uploaded_part_ids = []
        with open(video_path, "rb") as f:
            for part in instructions:
                upload_url = part["uploadUrl"]
                first_byte = part["firstByte"]
                last_byte = part["lastByte"]
                f.seek(first_byte)
                chunk = f.read(last_byte - first_byte + 1)

                put_res = requests.put(
                    upload_url,
                    headers={"Content-Type": "application/octet-stream"},
                    data=chunk
                )
                put_res.raise_for_status()
                etag = put_res.headers.get("ETag", "").strip('"')
                uploaded_part_ids.append(etag)

        # 3. Finalize Upload
        print(f"    [LinkedIn Video] Finalizing {video_urn}...", flush=True)
        fin_url = "https://api.linkedin.com/rest/videos?action=finalizeUpload"
        fin_payload = {
            "finalizeUploadRequest": {
                "video": video_urn,
                "uploadToken": upload_token,
                "uploadedPartIds": uploaded_part_ids
            }
        }
        fin_res = requests.post(fin_url, headers=self.headers, json=fin_payload)
        fin_res.raise_for_status()

        # 4. Poll until Video Status is AVAILABLE
        status_url = f"https://api.linkedin.com/rest/videos/{requests.utils.quote(video_urn, safe='')}"
        for _ in range(15):
            time.sleep(4)
            stat_res = requests.get(status_url, headers=self.headers)
            if stat_res.status_code == 200:
                v_status = stat_res.json().get("status")
                if v_status == "AVAILABLE":
                    break
                elif v_status == "PROCESSING_FAILED":
                    raise RuntimeError(f"LinkedIn video processing failed: {stat_res.text}")

        # 5. Create Feed Post with Video URN
        print(f"    [LinkedIn Video] Creating feed post for {video_urn}...", flush=True)
        post_url = "https://api.linkedin.com/rest/posts"
        post_payload = {
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
                    "id": video_urn
                }
            },
            "lifecycleState": "PUBLISHED"
        }
        post_res = requests.post(post_url, headers=self.headers, json=post_payload)
        post_res.raise_for_status()
        return post_res.headers.get("x-restli-id", video_urn)