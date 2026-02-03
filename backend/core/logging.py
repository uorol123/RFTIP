"""
日志配置模块 - Structured Logging Configuration

Provides centralized logging configuration for the RFTIP application.
Supports both development (colored console) and production (JSON file) logging.
"""
import logging
import sys
import json
import time
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from pythonjsonlogger import jsonlogger

from core.config import get_settings

settings = get_settings()


class RequestIdFilter(logging.Filter):
    """Filter to add request_id to log records if available"""

    def filter(self, record):
        # Try to get request_id from context var or add default
        record.request_id = getattr(record, "request_id", "N/A")
        return True


class ContextualFormatter(logging.Formatter):
    """Custom formatter that adds context information to logs"""

    def format(self, record):
        # Add extra context
        record.app_name = settings.app_name
        record.app_version = settings.app_version
        record.environment = "development" if settings.debug else "production"

        return super().format(record)


class JsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter for structured logging in production"""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["app"] = settings.app_name
        log_record["version"] = settings.app_version
        log_record["environment"] = "development" if settings.debug else "production"

        # Add timestamp if not present
        if "timestamp" not in log_record:
            log_record["timestamp"] = datetime.utcnow().isoformat()

        # Add request_id if available
        log_record["request_id"] = getattr(record, "request_id", "N/A")

        # Add error details for exceptions
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": record.exc_info[1].args[0] if record.exc_info[1] else None,
            }


def setup_logging() -> logging.Logger:
    """
    Setup application logging with appropriate handlers and formatters

    Returns:
        logging.Logger: Configured application logger
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Get root logger
    logger = logging.getLogger(settings.app_name)
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Remove any existing handlers
    logger.handlers.clear()

    # Console handler for development
    if settings.debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Colored formatter for console
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler for all environments
    log_file = log_dir / f"{settings.app_name}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Use JSON formatter in production, colored text in development
    if settings.debug:
        file_formatter = ContextualFormatter(
            "%(asctime)s | %(levelname)-8s | %(app_name)s | %(environment)s | %(name)s | %(funcName)s:%(lineno)d | %(request_id)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        file_formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )

    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Separate error log file
    error_log_file = log_dir / f"{settings.app_name}-errors.log"
    error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)

    # Security event log
    security_log_file = log_dir / "security.log"
    security_handler = logging.FileHandler(security_log_file, encoding="utf-8")
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(file_formatter)

    # Create security logger
    security_logger = logging.getLogger(f"{settings.app_name}.security")
    security_logger.handlers.clear()
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f"{settings.app_name}.{name}")


def get_security_logger() -> logging.Logger:
    """
    Get the security event logger

    Returns:
        logging.Logger: Security logger instance
    """
    return logging.getLogger(f"{settings.app_name}.security")


def log_request(logger: logging.Logger, method: str, path: str, status_code: int = None,
                duration_ms: float = None, request_id: str = None, **extra):
    """
    Log an HTTP request with context

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        request_id: Request identifier
        **extra: Additional context
    """
    log_data = {
        "type": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "request_id": request_id,
        **extra
    }

    # Create log message
    msg = f"{method} {path}"
    if status_code:
        msg += f" - {status_code}"
    if duration_ms:
        msg += f" ({duration_ms:.2f}ms)"

    # Set log level based on status code
    if status_code and status_code >= 500:
        logger.error(msg, extra={"request_id": request_id, **log_data})
    elif status_code and status_code >= 400:
        logger.warning(msg, extra={"request_id": request_id, **log_data})
    else:
        logger.info(msg, extra={"request_id": request_id, **log_data})


def log_security_event(event_type: str, user_id: int = None, ip_address: str = None,
                       details: Dict[str, Any] = None):
    """
    Log a security-related event

    Args:
        event_type: Type of security event (e.g., "login_success", "login_failed", "permission_denied")
        user_id: User ID if applicable
        ip_address: Client IP address
        details: Additional event details
    """
    security_logger = get_security_logger()

    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat(),
        **(details or {})
    }

    security_logger.info(
        f"Security event: {event_type}",
        extra=log_data
    )


def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None,
              request_id: str = None):
    """
    Log an error with full context

    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional context
        request_id: Request identifier
    """
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "request_id": request_id
    }

    logger.error(
        f"Error: {type(error).__name__}: {str(error)}",
        exc_info=error,
        extra={"request_id": request_id, **log_data}
    )


# Initialize logging on module import
app_logger = setup_logging()
