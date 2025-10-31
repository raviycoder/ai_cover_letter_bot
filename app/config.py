from pydantic import Field
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    TELE_BOT_KEY: str
    APPWRITE_ENDPOINT: str
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    OPENROUTER_API_KEY: str | None = Field(default=None)
    GEMINI_API_KEY: str | None = Field(default=None)
    ENV: str = Field(default="production")

    class Config:
        env_file = ".env"


settings = AppSettings()