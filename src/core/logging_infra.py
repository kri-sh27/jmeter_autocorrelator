"""
Logging Infrastructure Framework.
Thread-safe, enterprise-grade logger configured for high-throughput diagnostics.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

class LoggingInfrastructure:
    """Configures and registers the centralized logging layout."""
    
    _initialized: bool = False

    @classmethod
    def setup(cls, config: Dict[str, Any]) -> logging.Logger:
        """
        Initializes root loggers with standard streaming and asynchronous-ready rotation.
        """
        logger = logging.getLogger("JMeterAutoCorrelator")
        if cls._initialized:
            return logger

        log_level_str = config.get("level", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(threadName)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Appender
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Appender
        if config.get("log_to_file", False):
            file_path = config.get("file_path", "./logs/autocorrelator.log")
            log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=file_path,
                maxBytes=config.get("max_bytes", 10485760),
                backupCount=config.get("backup_count", 5),
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._initialized = True
        logger.info("Logging infrastructure successfully operational.")
        return logger