import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Inventario Recetas IA")
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./recipe_app.db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    llm_dry_run: bool = os.getenv("LLM_DRY_RUN", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


settings = Settings()

