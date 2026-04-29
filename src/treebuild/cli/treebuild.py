"""Primary commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from typing import Annotated, Optional

from typer import Argument, Exit, Option, Typer, echo

from treebuild.cli.helpers import ensure_session_exists, load_message
from treebuild.core.exceptions import DuplicatePathError
from treebuild.core.settings import get_settings
from treebuild.rendering.factory import RenderMethod, get_renderer
from treebuild.storage.session import SessionStore, normalize
from treebuild.tree.builder import TreeBuilder

app = Typer()


@app.command()
def hello() -> None:
    """Confirm treebuild-cli is installed properly."""
    echo("Hello from treebuild!")


@app.command()
def demo() -> None:
    """Demonstrates (basic) treebuild workflow"""

    echo(load_message("demo.md"))
    # -- FOLLOW DEMO ---

    # plant a tree:
    temp_session_file = Path().home() / ".config" / "treebuild" / "demo.txt"
    root_name = "myproject"
    session = SessionStore(temp_session_file)
    session.write_root(root_name)

    # grow the tree:
    path_names = [
        "myproject/first_folder/file.py",
        "myproject/second_folder/another_file.json",
        "/second_folder/yet_another.file",
        "empty_folder/",
        ".dotfile",
        "README.md",
    ]
    for path in path_names:
        session.write_path(path)

    # harvest:
    paths = [Path(entry) for entry in session.read_paths()]
    builder = TreeBuilder(root_name=root_name, paths=paths)
    tree = builder.assemble_tree()
    renderer = get_renderer(RenderMethod.PLAIN)
    rendering = renderer.render_tree(tree, include_root=True)
    echo(rendering)

    # remove temporary file
    session.delete_file()


@app.command()
def status() -> None:
    """Display current paths stored in session."""

    settings = get_settings()
    session_file = settings.session_file

    if not session_file.exists():
        message = load_message("status_no_tree.md")
        echo(message)
        raise Exit(code=0)

    session = SessionStore(session_file)
    if not (session.has_paths() or session.has_root()):
        message = load_message("status_empty_tree.md")
        echo(message)
        raise Exit(code=0)

    if not session.has_paths():
        message_1 = load_message("status_show_root.md")
        message_2 = load_message("status_no_nodes.md")
        echo(message_1.format(root=session.read_root()))
        echo(message_2)
        raise Exit(0)

    if not session.has_root():
        message_1 = load_message("status_no_root.md")
        message_2 = load_message("status_show_nodes.md")
        echo(message_1)
        echo(message_2.format(paths="\n".join(session.read_paths())))
        raise Exit(0)

    # at this point, we are certain you have both a root and at least one leaf/branch added.
    message_1 = load_message("status_show_root.md")
    message_2 = load_message("status_show_nodes.md")
    echo(message_1.format(root=session.read_root()))
    echo(message_2.format(paths="\n".join(session.read_paths())))


@app.command()
def plant(
    root: Annotated[
        str | None, Option(help="Name of root directory for your tree.")
    ] = None,
) -> None:
    """Start defining a new tree"""

    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.touch()
        logging.info(
            f"Created new file to store paths added to your tree: {session_file}"
        )

    session = SessionStore(session_file)
    if session.has_paths() or session.has_root():
        logging.error(
            "Another tree is already in progress.\n"
            "Check out it's status using `treebuild status`\n"
            "Start over? `treebuild replant`"
        )
        raise Exit(1)

    if root:
        session = SessionStore(session_file)
        session.write_root(root)
        logging.info(f"Written tree root: {root}")


@app.command()
def grow(
    paths: list[str] = Argument(help="Paths to be added as nodes to the tree."),
) -> None:
    """Add (a) path(s) to the current session's tree."""

    settings = get_settings()
    session_file = settings.session_file

    # Error path: Redirect user to command to call first
    ensure_session_exists(session_file)

    # Happy path: write into file
    session = SessionStore(file_path=session_file)
    for p in paths:
        try:
            session.write_path(p)
            logging.info(f"Path added: {p}")
        except DuplicatePathError:
            logging.warning(f"Skipping duplicate path: {p}")


@app.command()
def prune(
    paths: Annotated[
        Optional[list[str]],
        Argument(help="Path(s) to remove from current session's tree."),
    ] = None,
    remove_all: Annotated[
        bool, Option("--all", "-a", help="remove all paths from current session.")
    ] = False,
) -> None:
    """Remove (a) path(s) to the current session's tree."""

    if not (paths or remove_all):
        logging.error(
            "Please enter paths to remove or use the `--all` flag to indicate all paths should be removed.\n"
            "Try it again!"
        )
        raise Exit(1)

    settings = get_settings()
    session_file = settings.session_file

    # Error path: Redirect user to command to call first
    ensure_session_exists(session_file)

    # Happy path: Remove paths from the file
    session = SessionStore(file_path=session_file)

    if not session.has_paths():
        logging.error("No paths to remove.")
        raise Exit(1)

    if remove_all:
        _paths = session.read_paths()
        session.remove_all_paths()
        logging.info(f"Removed all paths: {_paths}")
        raise Exit(0)

    _paths = paths or []
    for p in _paths:
        if normalize(p) in session.read_paths():
            session.remove_path(p)
            logging.info(f"Path removed: {p}")
        else:
            logging.warning(f"Skipping, path not found: {p}")


@app.command()
def seed(
    root_name: Annotated[str, Argument(help="Name of the root directory.")],
) -> None:
    """Set root of the tree."""
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(file_path=session_file)
    session.write_root(root_name)
    logging.info(f"Root set: {root_name}")


@app.command()
def uproot() -> None:
    """Unset root name of tree."""
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(session_file)

    if not session.has_root():
        logging.error("No root to remove")
        raise Exit(1)

    root_name = session.read_root()
    session.remove_root()
    logging.info(f"Removed root: {root_name}")


@app.command()
def replant() -> None:
    """
    Keep the tree, but start from scratch with an empty file.

    ---
    Equivalent to (assuming you are using the same target file.)
    1. `treebuild chop`
    followed by
    2. `treebuild plant`
    """
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(file_path=session_file)
    session.clear_file()
    logging.info(f"Reset file: {session_file}")


@app.command()
def chop() -> None:
    """Delete the tree (including the file with session's data)."""
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(file_path=session_file)
    session.delete_file()
    logging.info(f"Deleted file: {session_file}")
