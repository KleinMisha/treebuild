"""Implementation of primary commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from typing import Optional

from treebuild.cli.helpers import NO_TREE_MSG, load_message
from treebuild.core.exceptions import (
    DuplicatePathError,
    EmptyTreeError,
    NoRootSetError,
    RootAlreadySetError,
    TreeAlreadyExistsError,
)
from treebuild.storage.settings import get_settings
from treebuild.storage.tree_store import TreeStore, normalize


def plant_impl(root: Optional[str] = None) -> None:
    """Start defining a new tree"""

    settings = get_settings()
    tree_file = settings.tree_file
    # Error path: File already exists / tell user to double check.
    if tree_file.exists():
        raise TreeAlreadyExistsError(
            "Another tree is already in progress.\n"
            "Check out it's status using `treebuild status`\n"
            "Start over? `treebuild replant` \n"
            "Delete the file? `treebuild chop`"
        )

    tree_file.parent.mkdir(parents=True, exist_ok=True)
    tree_file.touch()
    logging.info(f"Created new file to store paths added to your tree: {tree_file}")
    store = TreeStore(tree_file)
    if root:
        store = TreeStore(tree_file)
        store.write_root(root)
        logging.info(f"Written tree root: {root}")


def status_impl() -> None:
    """Display current paths stored in store."""

    settings = get_settings()
    tree_file = settings.tree_file

    if not tree_file.exists():
        message = load_message("status_no_tree.md")
        logging.info(message)
        return

    store = TreeStore(tree_file)
    if not (store.has_paths() or store.has_root()):
        message = load_message("status_empty_tree.md")
        logging.info(message)
        return

    if not store.has_paths():
        message_1 = load_message("status_show_root.md")
        message_2 = load_message("status_no_nodes.md")
        logging.info(message_1.format(root=store.read_root()))
        logging.info(message_2)
        return

    if not store.has_root():
        message_1 = load_message("status_no_root.md")
        message_2 = load_message("status_show_nodes.md")
        logging.info(message_1)
        logging.info(message_2.format(paths="\n".join(store.read_paths())))
        return

    # at this point, we are certain you have both a root and at least one leaf/branch added.
    message_1 = load_message("status_show_root.md")
    message_2 = load_message("status_show_nodes.md")
    logging.info(message_1.format(root=store.read_root()))
    logging.info(message_2.format(paths="\n".join(store.read_paths())))


def grow_impl(paths: list[str]) -> None:
    """Add (a) path(s) to the current store's tree."""

    settings = get_settings()
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)

    # Happy path: write into file
    store = TreeStore(file_path=tree_file)
    for p in paths:
        try:
            store.write_path(p)
            logging.info(f"Path added: {p}")
        except DuplicatePathError as e:
            logging.warning(str(e))


def prune_impl(
    paths: Optional[list[str]] = None,
    remove_all: bool = False,
) -> None:
    """Remove (a) path(s) to the current store's tree."""

    settings = get_settings()
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)

    # Happy path: Remove paths from the file
    store = TreeStore(file_path=tree_file)

    if not store.has_paths():
        raise EmptyTreeError("No paths to remove.")

    if remove_all:
        _paths = store.read_paths()
        store.remove_all_paths()
        logging.info(f"Removed all paths: {_paths}")
        return

    _paths = paths or []
    for p in _paths:
        if normalize(p) in store.read_paths():
            store.remove_path(p)
            logging.info(f"Path removed: {p}")
        else:
            logging.warning(f"Skipping, path not found: {p}")


def seed_impl(root_name: str, force: bool) -> None:
    """Set root of the tree."""
    settings = get_settings()
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)

    store = TreeStore(file_path=tree_file)
    if store.has_root() and not force:
        raise RootAlreadySetError(
            f"Your tree already has a root directory name set: {store.read_root()} \n"
            f"To overwrite: `treebuild seed -f {root_name}"
        )
    store.write_root(root_name)
    logging.info(f"Root set: {root_name}")


def uproot_impl() -> None:
    """Unset root name of tree."""
    settings = get_settings()
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)

    store = TreeStore(tree_file)
    if not store.has_root():
        raise NoRootSetError("No root to remove")

    root_name = store.read_root()
    store.remove_root()
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
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)
    store = TreeStore(file_path=tree_file)
    store.clear_file()
    logging.info(f"Reset file: {tree_file}")


def chop_impl() -> None:
    """Delete the tree (including the file with store's data)."""
    settings = get_settings()
    tree_file = settings.tree_file
    if not tree_file.exists():
        raise EmptyTreeError(NO_TREE_MSG)
    store = TreeStore(file_path=tree_file)
    store.delete_file()
    logging.info(f"Deleted file: {tree_file}")
