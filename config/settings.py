import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field("2024-12-01-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: str = Field("gpt-4.1", alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Cloudinary
    cloudinary_cloud_name: str = Field(..., alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(..., alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(..., alias="CLOUDINARY_API_SECRET")
    
    # Instagram Graph API
    instagram_user_id: str = Field(..., alias="INSTAGRAM_USER_ID")
    instagram_access_token: str = Field(..., alias="INSTAGRAM_ACCESS_TOKEN")
    instagram_base_url: str = "https://graph.instagram.com/v20.0"
    
    # Paths & Defaults
    history_file_path: str = "data/content_history.json"
    rendered_slides_dir: str = "rendered_slides"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()