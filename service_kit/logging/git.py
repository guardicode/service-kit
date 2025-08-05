import shutil
import subprocess
from pathlib import Path

import yaml

from . import logger

GIT = shutil.which("git")


def log_git_status(git_status_yaml_path: Path | None = None):
    """
    Log the status of the current git repository

    Logs the commit ID, repository status (clean or dirty), and any tags associated with the current
    HEAD at the INFO level. Optionally, this function accepts a path to a YAML file. If, and only
    if, the current directory is not a git repository, or the `git` command is not available, the
    status can be read from the YAML file instead. Note, however, that this function cannot
    guarantee the accuracy of the information in the YAML file.

    Example YAML file:
        commit: "3db2b4fbc9db2635b4ae6411496132f6d985426e"
        status: "clean"
        tags:
        - test-tag

    :param git_status_yaml_path: Optional path to a YAML file containing git status information.
    """
    if GIT is None:
        logger.warning("Command `git` not found")
        commit_id, status, tags = _read_yaml_file(git_status_yaml_path)
    elif not _pwd_in_git_repository():
        logger.warning("Failed to identify a git repository")
        commit_id, status, tags = _read_yaml_file(git_status_yaml_path)
    else:
        commit_id = _get_commit_id()
        status = _get_repository_status()
        tags = _get_tags()

    logger.info("Identified the currently running code", commit=commit_id, status=status, tags=tags)


def _read_yaml_file(git_status_yaml_path: Path | None) -> tuple[str, str, list[str]]:
    unknown_git_status: tuple[str, str, list[str]] = ("UNKNOWN", "UNKNOWN", [])

    if git_status_yaml_path is None:
        logger.info("No git status YAML file provided")
        return unknown_git_status
    else:
        logger.info("Attempting to retrieve the git status from a file")

    try:
        with open(git_status_yaml_path, "r") as f:
            git_status = yaml.safe_load(f)

        return (git_status["commit"], git_status["status"], git_status["tags"])
    except FileNotFoundError:
        logger.warning(
            "The provided git status YAML file does not exist.", path=git_status_yaml_path
        )
        return unknown_git_status
    except KeyError as err:
        logger.warning(
            "The provided git status YAML file is missing a required field.",
            path=git_status_yaml_path,
            field=str(err),
        )
        return unknown_git_status
    except Exception as err:
        logger.warning(
            "Failed to read git status from YAML file",
            path=git_status_yaml_path,
            error=str(err),
        )
        return unknown_git_status


def _pwd_in_git_repository() -> bool:
    try:
        subprocess.run(
            [GIT, "rev-parse", "--is-inside-work-tree"],  # type: ignore[list-item]
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return True
    except subprocess.CalledProcessError:
        return False


def _get_commit_id():
    process = subprocess.run(
        [GIT, "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE, text=True  # type: ignore[list-item]  # noqa: E501
    )
    return process.stdout.strip()


def _get_repository_status():
    try:
        subprocess.run(
            [GIT, "diff-index", "--quiet", "HEAD"],  # type: ignore[list-item]
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return "clean"
    except subprocess.CalledProcessError:
        return "dirty"


def _get_tags():
    process = subprocess.run(
        [GIT, "tag", "--points-at", "HEAD"], check=True, stdout=subprocess.PIPE, text=True  # type: ignore[list-item]  # noqa: E501
    )
    tags = process.stdout.strip().split("\n")

    return [tag for tag in tags if tag]
