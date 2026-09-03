import sys

from loguru import logger as loguru_logger


def setup_logging():
    loguru_logger.remove()

    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    loguru_logger.add(
        sys.stdout,
        format=format_string,
        level="DEBUG",
        colorize=True,
    )


logger = loguru_logger
