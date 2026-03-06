from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    OPENAPI_URL: str = os.getenv("OPENAPI_URL", "https://superbfsi.com/openapi.yaml")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campaignx.db")
    CAMPAIGNX_API_KEY: str = os.getenv("CAMPAIGNX_API_KEY", "")
    CAMPAIGNX_BASE_URL: str = os.getenv("CAMPAIGNX_BASE_URL", "https://campaignx.superb.ai")
    
    class Config:
        extra = "ignore"  # ignore extra env arguments

settings = Settings()
