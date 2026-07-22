"""
utils/logger.py
---------------
Centralised logging setup for the entire application.
Import `logger` from this module in any file that needs logging.
"""

import logging
import sys


def get_logger(name: str = "skill_assessment") -> logging.Logger:
    """
    Create and return a configured logger.

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Session started")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger


# Default module-level logger
logger = get_logger()