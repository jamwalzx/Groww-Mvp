"""
Application settings loaded from environment variables.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    llm_provider: str = "groq"          # "groq" | "openai" | "gemini" | "mock"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.0

    # API Keys
    groq_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Feature flags
    skip_rules_verified: bool = False

    # Eval
    eval_cost_cap_usd: float = 1.00

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://your-deployed-frontend.vercel.app",
    ]


settings = Settings()
