"""Implementation of primary command group"""

import logging
from typing import Optional

from treebuild.cli.helpers import load_message
from treebuild.core.exceptions import SessionAlreadyExistsError
from treebuild.core.settings import get_settings
from treebuild.storage.session import SessionStore

# TODO figure out what to do with this message --> basically want to do either a "no file at all" or "file found, but no paths/root"
# TODO Status command for sure needs them individually, let's see ..
NO_SESSION_MSG = load_message("status_no_tree.md")


def plant_impl(root: Optional[str] = None) -> None:
    """Start defining a new tree"""

    settings = get_settings()
    session_file = settings.session_file
    if session_file.exists():
        raise SessionAlreadyExistsError(
            "Another tree is already in progress.\n"
            "Check out it's status using `treebuild status`\n"
            "Start over? `treebuild replant`"
        )

    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.touch()
    logging.info(f"Created new file to store paths added to your tree: {session_file}")
    session = SessionStore(session_file)
    if root:
        session = SessionStore(session_file)
        session.write_root(root)
        logging.info(f"Written tree root: {root}")
