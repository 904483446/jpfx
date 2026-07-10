from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Competitor Intelligence Workspace API"
    api_v1_prefix: str = "/api/v1"


settings = Settings()
