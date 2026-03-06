from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — reads from .env file automatically."""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""  # Optional fallback
    DATABASE_URL: str = "sqlite:///./campaignx.db"
    CAMPAIGNX_API_KEY: str = ""
    CAMPAIGNX_BASE_URL: str = "https://campaignx.inxiteout.ai"
    DEMO_MODE: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
