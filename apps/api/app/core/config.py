from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "demo"
    APP_NAME: str = "PharmaBridge"
    DEMO_MODE: bool = True
    PHARMACY_TIMEZONE: str = "Asia/Kolkata"

    DATABASE_URL: str = "postgresql+asyncpg://pharmabridge:pharmabridge_dev_password@localhost:5432/pharmabridge"
    POSTGRES_DB: str = "pharmabridge"
    POSTGRES_USER: str = "pharmabridge"
    POSTGRES_PASSWORD: str = "pharmabridge_dev_password"

    SESSION_SECRET: str = "dev_session_secret_pb_local_environment_at_least_32_bytes_length"
    SESSION_COOKIE_NAME: str = "pharmabridge_session"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_ABSOLUTE_TTL_SECONDS: int = 28800
    SESSION_IDLE_TTL_SECONDS: int = 1800
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:8080"

    UPLOAD_DIRECTORY: str = "data/private-uploads"
    MAX_UPLOAD_BYTES: int = 10485760
    MAX_PDF_PAGES: int = 5
    UPLOAD_RETENTION_HOURS: int = 24

    VISION_PROVIDER: str = "tesseract"
    VISION_MODEL: str = ""
    GEMINI_API_KEY: str = ""
    EXTERNAL_VISION_ENABLED: bool = False

    JOB_CONCURRENCY: int = 2
    JOB_MAX_ATTEMPTS: int = 3
    JOB_LEASE_SECONDS: int = 120

    QUOTE_TTL_SECONDS: int = 300
    PRICE_MAX_AGE_DAYS: int = 30
    EXPIRY_BUFFER_DAYS: int = 30
    CATALOG_REFRESH_ENABLED: bool = False

    DEMO_ADMIN_PASSWORD: str = "DemoAdminPass123!"
    DEMO_PHARMACIST_PASSWORD: str = "DemoPharmacistPass123!"
    DEMO_ASSISTANT_PASSWORD: str = "DemoAssistantPass123!"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
