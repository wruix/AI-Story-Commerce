"""AI Story Commerce — Application Configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AI Story Commerce"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ai_story_commerce.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File storage
    UPLOAD_DIR: str = "data/uploads"
    MATERIALS_DIR: str = "data/materials"
    OUTPUTS_DIR: str = "data/outputs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()