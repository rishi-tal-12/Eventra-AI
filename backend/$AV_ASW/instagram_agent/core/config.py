"""
core/config.py
--------------
Single settings object loaded from .env via pydantic-settings.
Import `settings` anywhere in the project.
"""

'''from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    OPENAI_API_KEY: str = ""

    # Instagram
    IG_ACCESS_TOKEN: str        = ""
    IG_BUSINESS_ACCOUNT_ID: str = ""
    IG_PAGE_ID: str             = ""

    # Image hosting
    CLOUDINARY_CLOUD_NAME:  str = ""
    CLOUDINARY_API_KEY:     str = ""
    CLOUDINARY_API_SECRET:  str = ""

    # App
    DATABASE_URL: str = "sqlite:///./instagram_agent.db"
    LOG_LEVEL: str    = "INFO"


settings = Settings()'''

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM — now using Ollama locally
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str    = "llama3.2"

    # Instagram (leave blank until you need it)
    IG_ACCESS_TOKEN: str        = ""
    IG_BUSINESS_ACCOUNT_ID: str = ""
    IG_PAGE_ID: str             = ""

    # Cloudinary (leave blank until you need it)
    CLOUDINARY_CLOUD_NAME:  str = ""
    CLOUDINARY_API_KEY:     str = ""
    CLOUDINARY_API_SECRET:  str = ""

    DATABASE_URL: str = "sqlite:///./instagram_agent.db"
    LOG_LEVEL: str    = "INFO"

settings = Settings()
