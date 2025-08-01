import shutil
import subprocess

from . import logger

GIT = shutil.which("git")


def _pwd_is_git_repository() -> bool:
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
    # Filter empty items to avoid empty strings
    return [tag for tag in tags if tag]


def log_git_status():
    """
    Log the status of the current git repository

    Logs the commit ID, repository status (clean or dirty), and any tags
    associated with the current HEAD at the INFO level.
    """
    if not _pwd_is_git_repository():
        logger.warning(
            "The current directory is not a Git repository so the running code cannot be "
            "identified by a tag or commit ID."
        )
        return

    commit_id = _get_commit_id()
    status = _get_repository_status()
    tags = _get_tags()

    logger.info("Identified the currently running code", commit=commit_id, status=status, tags=tags)
