from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = ""
    redis_url: str = ""
    steam_api_key: str = ""
    igdb_client_id: str = ""
    igdb_client_secret: str = ""
    cors_origins: list[str] = []
    port: int = 8000


settings = Settings()
