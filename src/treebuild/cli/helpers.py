"""Functions shared across CLI endpoints"""

from pathlib import Path

from typer import Exit, echo

# Where messages are stored.
MESSAGES_DIR = Path(__file__).parent / "messages"


def ensure_session_exists(session_file: Path) -> None:
    """Helper to raise exit code 1 if no session file is detected."""
    if not session_file.exists():
        echo(
            f"No file for current session found: {session_file} \n"
            "Use `treebuild new` to start growing your new tree. "
        )
        raise Exit(code=1)


def load_message(filename: str) -> str:
    file = MESSAGES_DIR / filename
    return file.read_text()
