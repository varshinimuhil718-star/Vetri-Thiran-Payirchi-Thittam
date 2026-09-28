from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    database_url: str = Field(
        default="sqlite:///./fitbuddy.db",
        validation_alias="DATABASE_URL",
    )
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
    )
    workout_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias="GEMINI_WORKOUT_MODEL",
    )
    tip_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias="GEMINI_TIP_MODEL",
    )
    mock_ai: bool = Field(default=False, validation_alias="MOCK_AI")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
