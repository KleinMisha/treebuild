"""Primary commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from typing import Annotated, Optional

from typer import Argument, Exit, Option, Typer, echo

from treebuild.cli.commands.treebuild import (
    grow_impl,
    plant_impl,
    prune_impl,
    replant_impl,
    seed_impl,
    uproot_impl,
)
from treebuild.cli.helpers import ensure_session_exists, load_message
from treebuild.core.exceptions import (
    EmptySessionError,
    NoRootSetError,
    RootAlreadySetError,
    SessionAlreadyExistsError,
)
from treebuild.core.settings import get_settings
from treebuild.harvest.render_factory import RenderMethod, get_renderer
from treebuild.storage.session import SessionStore
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

    # harvest text:
    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
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
    try:
        plant_impl(root)
        raise Exit(code=0)
    except SessionAlreadyExistsError as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


@app.command()
def grow(
    paths: list[str] = Argument(help="Paths to be added as nodes to the tree."),
) -> None:
    """Add (a) path(s) to the current session's tree."""
    try:
        grow_impl(paths)
        raise Exit(code=0)
    except EmptySessionError as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


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

    # Improper call to the command.
    if not (paths or remove_all):
        logging.error(
            "Please enter paths to remove or use the `--all` flag to indicate all paths should be removed.\n"
            "Try it again!"
        )
        raise Exit(code=1)

    try:
        prune_impl(paths, remove_all)
        raise Exit(code=0)
    except EmptySessionError as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)


@app.command()
def seed(
    root_name: Annotated[str, Argument(help="Name of the root directory.")],
    force: Annotated[
        bool, Option("--force", "-f", help="Overwrite existing root (if existing). ")
    ] = False,
) -> None:
    """Set root of the tree."""
    try:
        seed_impl(root_name, force)
        raise Exit(code=0)
    except (EmptySessionError, RootAlreadySetError) as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)


@app.command()
def uproot() -> None:
    """Unset root name of tree."""
    try:
        uproot_impl()
        raise Exit(code=0)
    except (EmptySessionError, NoRootSetError) as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)


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
    try:
        replant_impl()
        raise Exit(code=0)
    except EmptySessionError as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)


@app.command()
def chop() -> None:
    """Delete the tree (including the file with session's data)."""
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(file_path=session_file)
    session.delete_file()
    logging.info(f"Deleted file: {session_file}")
