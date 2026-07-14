from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Competitor Intelligence Workspace API"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    test_database_url: str | None = None
    jwt_secret: str | None = None
    access_token_expire_days: int = 7
    auth_cookie_name: str = "access_token"
    auth_cookie_secure: bool = False
    cors_allowed_origins: str = "http://127.0.0.1:3000"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
