"""Functions shared across CLI endpoints"""

import logging
from pathlib import Path

from typer import Exit, echo

from treebuild.core.exceptions import TreeBuildError

# Where messages are stored.
MESSAGES_DIR = Path(__file__).parent / "messages"


def load_message(filename: str) -> str:
    file = MESSAGES_DIR / filename
    return file.read_text()


# TODO remove this method after refactor / migration is done!
def ensure_session_exists(session_file: Path) -> None:
    """Most commands need share this check: Ensure a session file has been created."""
    if not session_file.exists():
        msg = load_message("status_no_tree.md")
        echo(msg)
        raise Exit(code=1)


# Exception Handlers:
def raise_exit(exc: TreeBuildError) -> None:
    """Handle fatal errors by logging message + exiting with status code 1."""
    logging.error(f"{type(exc).__name__}: {str(exc)}")
    raise Exit(code=1)


def only_warn(exc: TreeBuildError) -> None:
    """Log the error, do not raise Exit status"""
    msg = f"{type(exc).__name__} : {str(exc)}"
    logging.warning(msg)
