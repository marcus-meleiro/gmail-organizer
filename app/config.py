from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gmail Organizer"
    app_env: Literal["development", "production"] = "development"

    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "gmail_organizer"
    db_user: str = "postgres"
    db_password: str = "postgres"

    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    google_redirect_uri: str = "http://localhost:8000/oauth2callback"
    gmail_scopes: str = (
        "https://www.googleapis.com/auth/gmail.readonly,"
        "https://www.googleapis.com/auth/gmail.modify,"
        "https://www.googleapis.com/auth/gmail.labels"
    )

    default_label_work: str = "Trabalho"
    default_label_job: str = "Processo Seletivo"
    default_label_study: str = "Faculdade"
    default_label_promo: str = "Propaganda"
    default_label_bank: str = "Banco"
    default_label_other: str = "Outros"

    personal_account: str = ""
    professional_account: str = ""
    university_account: str = ""

    streamlit_port: int = 8501

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
