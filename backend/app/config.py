from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Sustainability Radar"
    database_url: str = "sqlite:///./radar.db"
    bls_api_key: str | None = None
    eia_api_key: str
    bls_years_back: int = 3
    eia_months_back: int = 36
    request_timeout_seconds: float = 30.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
