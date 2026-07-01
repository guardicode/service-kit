import sys
from pathlib import Path

from . import log_git_status, logger


def log_startup_information(git_status_yaml_path: Path | None = None):
    log_python_version()
    log_git_status(git_status_yaml_path)


def log_python_version():
    logger.info("Python version", version=sys.version)
