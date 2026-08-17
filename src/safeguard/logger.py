"""
Logging configuration for safeguard.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "safeguard") -> logging.Logger:
    """Set up and return a configured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    log_dir = Path.home() / ".safeguard" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"safeguard_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


class MediaLogger:
    """Wrapper around standard logging for media events."""

    def __init__(self):
        self._logger = setup_logger()

    def debug(self, message: str):
        """Log debug message."""
        self._logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self._logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self._logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self._logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self._logger.critical(message)
