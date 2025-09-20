from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    gemini_api_key: str
    max_file_size: int = 5 * 1024 * 1024 * 1024  # 5 GB
    allowed_video_extensions: list = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg"]
    upload_directory: str = "uploads"
    analysis_directory: str = "analysis_results"
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()