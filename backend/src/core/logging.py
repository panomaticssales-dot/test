"""
Logging configuration for HDR Blender backend.
"""
import logging
import logging.handlers
from pathlib import Path
from src.core.config import Config


def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("hdr_blender")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=Config.LOGS_DIR / "hdr_blender.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
