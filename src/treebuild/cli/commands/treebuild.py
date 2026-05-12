"""Implementation of primary commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from typing import Optional

from treebuild.cli.helpers import NO_SESSION_MSG, load_message
from treebuild.core.exceptions import (
    DuplicatePathError,
    EmptySessionError,
    NoRootSetError,
    RootAlreadySetError,
    SessionAlreadyExistsError,
)
from treebuild.core.settings import get_settings
from treebuild.storage.session import SessionStore, normalize


def plant_impl(root: Optional[str] = None) -> None:
    """Start defining a new tree"""

    settings = get_settings()
    session_file = settings.session_file
    # Error path: File already exists / tell user to double check.
    if session_file.exists():
        raise SessionAlreadyExistsError(
            "Another tree is already in progress.\n"
            "Check out it's status using `treebuild status`\n"
            "Start over? `treebuild replant` \n"
            "Delete the file? `treebuild chop`"
        )

    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.touch()
    logging.info(f"Created new file to store paths added to your tree: {session_file}")
    session = SessionStore(session_file)
    if root:
        session = SessionStore(session_file)
        session.write_root(root)
        logging.info(f"Written tree root: {root}")


def status_impl() -> None:
    """Display current paths stored in session."""

    settings = get_settings()
    session_file = settings.session_file

    if not session_file.exists():
        message = load_message("status_no_tree.md")
        logging.info(message)
        return

    session = SessionStore(session_file)
    if not (session.has_paths() or session.has_root()):
        message = load_message("status_empty_tree.md")
        logging.info(message)
        return

    if not session.has_paths():
        message_1 = load_message("status_show_root.md")
        message_2 = load_message("status_no_nodes.md")
        logging.info(message_1.format(root=session.read_root()))
        logging.info(message_2)
        return

    if not session.has_root():
        message_1 = load_message("status_no_root.md")
        message_2 = load_message("status_show_nodes.md")
        logging.info(message_1)
        logging.info(message_2.format(paths="\n".join(session.read_paths())))
        return

    # at this point, we are certain you have both a root and at least one leaf/branch added.
    message_1 = load_message("status_show_root.md")
    message_2 = load_message("status_show_nodes.md")
    logging.info(message_1.format(root=session.read_root()))
    logging.info(message_2.format(paths="\n".join(session.read_paths())))


def grow_impl(paths: list[str]) -> None:
    """Add (a) path(s) to the current session's tree."""

    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    # Happy path: write into file
    session = SessionStore(file_path=session_file)
    for p in paths:
        try:
            session.write_path(p)
            logging.info(f"Path added: {p}")
        except DuplicatePathError as e:
            logging.warning(str(e))


def prune_impl(
    paths: Optional[list[str]] = None,
    remove_all: bool = False,
) -> None:
    """Remove (a) path(s) to the current session's tree."""

    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    # Happy path: Remove paths from the file
    session = SessionStore(file_path=session_file)

    if not session.has_paths():
        raise EmptySessionError("No paths to remove.")

    if remove_all:
        _paths = session.read_paths()
        session.remove_all_paths()
        logging.info(f"Removed all paths: {_paths}")
        return

    _paths = paths or []
    for p in _paths:
        if normalize(p) in session.read_paths():
            session.remove_path(p)
            logging.info(f"Path removed: {p}")
        else:
            logging.warning(f"Skipping, path not found: {p}")


def seed_impl(root_name: str, force: bool) -> None:
    """Set root of the tree."""
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    session = SessionStore(file_path=session_file)
    if session.has_root() and not force:
        raise RootAlreadySetError(
            f"Your tree already has a root directory name set: {session.read_root()} \n"
            f"To overwrite: `treebuild seed -f {root_name}"
        )
    session.write_root(root_name)
    logging.info(f"Root set: {root_name}")


def uproot_impl() -> None:
    """Unset root name of tree."""
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    session = SessionStore(session_file)
    if not session.has_root():
        raise NoRootSetError("No root to remove")

    root_name = session.read_root()
    session.remove_root()
    logging.info(f"Removed root: {root_name}")


def replant_impl() -> None:
    """
    Keep the tree, but start from scratch with an empty file.

    ---
    Equivalent to (assuming you are using the same target file.)
    1. `chop_impl`
    followed by
    2. `plant_impl`
    """
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)
    session = SessionStore(file_path=session_file)
    session.clear_file()
    logging.info(f"Reset file: {session_file}")


def chop_impl() -> None:
    """Delete the tree (including the file with session's data)."""
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)
    session = SessionStore(file_path=session_file)
    session.delete_file()
    logging.info(f"Deleted file: {session_file}")
