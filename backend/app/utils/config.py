from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    openai_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"          # "openai" | "anthropic"
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-sonnet-4-6"

    # Search
    exa_api_key: str = ""
    serper_api_key: str = ""
    search_provider: str = "exa"          # "exa" | "serper"

    # App
    max_file_size_mb: int = 10
    allowed_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def active_llm_api_key(self) -> str:
        return (
            self.groq_api_key
            if self.llm_provider == "openai"
            else self.anthropic_api_key
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()