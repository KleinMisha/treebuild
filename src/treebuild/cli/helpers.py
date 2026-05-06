"""Functions shared across CLI endpoints"""

from pathlib import Path

# Where messages are stored.
MESSAGES_DIR = Path(__file__).parent / "messages"


def load_message(filename: str) -> str:
    file = MESSAGES_DIR / filename
    return file.read_text()


# TODO figure out what to do with this message --> basically want to do either a "no file at all" or "file found, but no paths/root"
# TODO Status command for sure needs them individually, let's see ..
NO_SESSION_MSG = load_message("status_no_tree.md")
