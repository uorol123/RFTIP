import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "RFTIP API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database Settings
    database_url: str = "mysql+pymysql://root:password@localhost:3306/rftip_db"

    # Security Settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging Settings
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "json"  # json or text
    log_dir: str = "logs"
    log_max_bytes: int = 10485760  # 10MB
    log_backup_count: int = 5
    log_request_body: bool = False  # Whether to log request bodies (security consideration)
    log_response_body: bool = False  # Whether to log response bodies (security consideration)
    slow_request_threshold_ms: float = 1000.0  # Threshold for slow request logging

    # File Upload Settings
    max_upload_size_mb: int = 100
    allowed_file_extensions: list[str] = [".csv", ".xlsx", ".xls"]
    upload_dir: str = "uploads"

    # SMTP 邮件配置
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None

    # Error Handling Settings
    include_error_details: bool = False  # Include stack traces in error responses (dev only)
    enable_error_notifications: bool = False  # Send notifications for critical errors

    # Performance Monitoring
    enable_performance_logging: bool = True
    enable_query_logging: bool = False  # Log SQL queries (dev only)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def logs_path(self) -> Path:
        """Get the logs directory path."""
        path = Path(self.log_dir)
        path.mkdir(exist_ok=True)
        return path

    @property
    def uploads_path(self) -> Path:
        """Get the uploads directory path."""
        path = Path(self.upload_dir)
        path.mkdir(exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    return Settings()
