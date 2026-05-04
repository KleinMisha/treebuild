"""Functions shared across CLI endpoints"""

from pathlib import Path

from typer import Exit, echo

# Where messages are stored.
MESSAGES_DIR = Path(__file__).parent / "messages"


def load_message(filename: str) -> str:
    file = MESSAGES_DIR / filename
    return file.read_text()


def ensure_session_exists(session_file: Path) -> None:
    """Most commands need share this check: Ensure a session file has been created."""
    if not session_file.exists():
        msg = load_message("status_no_tree.md")
        echo(msg)
        raise Exit(code=1)
