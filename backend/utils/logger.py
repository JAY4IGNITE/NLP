"""Structured logger with credential sanitization and JSON formatting."""
import logging
import json
import sys
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """Custom JSON formatter with automated credential redaction."""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "structured_data") and isinstance(record.structured_data, dict):
            # Sanitize any keys that might contain sensitive tokens
            sanitized = {}
            for k, v in record.structured_data.items():
                if any(sec in k.lower() for sec in ("key", "token", "secret", "auth", "password")):
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = v
            log_data.update(sanitized)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logger(name: str = "campusai_backend") -> logging.Logger:
    """Setup and configure a structured logger instance."""
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        log.addHandler(handler)
        log.setLevel(logging.INFO)
    return log

logger = setup_logger()

def log_event(event_type: str, details: Dict[str, Any], level: str = "info"):
    """Emit a structured event log."""
    extra = {"structured_data": {"event": event_type, **details}}
    if level == "error":
        logger.error(f"Event: {event_type}", extra=extra)
    elif level == "warning":
        logger.warning(f"Event: {event_type}", extra=extra)
    else:
        logger.info(f"Event: {event_type}", extra=extra)
