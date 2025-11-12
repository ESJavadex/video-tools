from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""  # Optional now
    openai_api_key: str = ""  # Optional now

    # AI Provider Selection (choose: "openai" or "gemini")
    ai_provider: str = "openai"  # Default to OpenAI
    openai_model: str = "gpt-4.1-mini"  # gpt-4.1-mini, gpt-4.1-mini-mini, or gpt-4-turbo

    # File handling
    max_file_size: int = 5 * 1024 * 1024 * 1024  # 5 GB
    allowed_video_extensions: list = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg"]
    upload_directory: str = "uploads"
    analysis_directory: str = "analysis_results"

    # CORS
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()