"""
应用配置模块
所有配置从 .env 文件读取，代码中不保留任何默认值
"""
import os
from pathlib import Path
from typing import List
from types import SimpleNamespace
from functools import lru_cache

# 加载 .env 文件
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CORS Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")

# Application Settings
APP_NAME = os.getenv("APP_NAME", "RFTIP API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SLOW_REQUEST_THRESHOLD_MS = int(os.getenv("SLOW_REQUEST_THRESHOLD_MS", "1000"))

# MinIO Settings
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Redis Settings
REDIS_URL = os.getenv("REDIS_URL")

# SMTP Settings
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "False").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "RFTIP Team")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

# Verification Code Settings
VERIFICATION_CODE_LENGTH = int(os.getenv("VERIFICATION_CODE_LENGTH", "6"))
VERIFICATION_CODE_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", "5"))
LOG_VERIFICATION_CODE = os.getenv("LOG_VERIFICATION_CODE", "True").lower() == "true"


def get_cors_origins() -> List[str]:
    """将 CORS_ORIGINS 字符串转换为列表"""
    return [origin.strip() for origin in CORS_ORIGINS.split(",")]


def check_required_config() -> List[str]:
    """检查必需的配置项是否已设置"""
    required = {
        "DATABASE_URL": DATABASE_URL,
        "SECRET_KEY": SECRET_KEY,
    }
    missing = [name for name, value in required.items() if not value]
    return missing


@lru_cache()
def get_settings():
    """
    获取配置对象（向后兼容）
    返回包含所有配置的 SimpleNamespace 对象
    """
    return SimpleNamespace(
        # Database
        database_url=DATABASE_URL,

        # Security
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,

        # CORS
        cors_origins=CORS_ORIGINS,

        # Application
        app_name=APP_NAME,
        app_version=APP_VERSION,
        debug=DEBUG,
        slow_request_threshold_ms=SLOW_REQUEST_THRESHOLD_MS,

        # MinIO
        minio_endpoint=MINIO_ENDPOINT,
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        minio_bucket=MINIO_BUCKET,
        minio_secure=MINIO_SECURE,

        # Redis
        redis_url=REDIS_URL,

        # SMTP
        smtp_enabled=SMTP_ENABLED,
        smtp_host=SMTP_HOST,
        smtp_port=SMTP_PORT,
        smtp_user=SMTP_USER,
        smtp_password=SMTP_PASSWORD,
        smtp_from=SMTP_FROM,
        smtp_from_name=SMTP_FROM_NAME,
        smtp_use_tls=SMTP_USE_TLS,

        # Verification Code
        verification_code_length=VERIFICATION_CODE_LENGTH,
        verification_code_expire_minutes=VERIFICATION_CODE_EXPIRE_MINUTES,
        log_verification_code=LOG_VERIFICATION_CODE,
    )
