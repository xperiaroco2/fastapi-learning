import sys

from loguru import logger


def setup_logging(is_production: bool = False):
    logger.remove()

    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=format_string,
        level="DEBUG",
        colorize=True,
    )

    return logger
