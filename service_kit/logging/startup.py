import sys

from . import logger


def log_python_version():
    logger.info("Python version", version=sys.version)
