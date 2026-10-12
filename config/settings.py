from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_deployment_name: str = "gpt-4.1"

    # Cloudinary Asset Hosting
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    # Meta / Instagram Graph API
    instagram_user_id: str
    instagram_access_token: str
    instagram_base_url: str = "https://graph.facebook.com/v21.0"

    # LinkedIn (Optional cross-posting)
    linkedin_access_token: Optional[str] = ""
    linkedin_author_urn: Optional[str] = ""

    # Storage Paths
    history_file_path: str = "data/content_history.json"
    slides_output_dir: str = "rendered_slides"


settings = Settings()