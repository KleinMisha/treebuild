"""Primary commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from typing import Annotated, Optional

from typer import Abort, Argument, Exit, Option, Typer, echo

from treebuild.cli.commands.treebuild import (
    chop_impl,
    grow_impl,
    plant_impl,
    prune_impl,
    replant_impl,
    seed_impl,
    status_impl,
    uproot_impl,
)
from treebuild.cli.walkthrough import interactive_demo, interrupt_demo, quickstart_impl
from treebuild.core.exceptions import (
    EmptySessionError,
    NoRootSetError,
    RootAlreadySetError,
    SessionAlreadyExistsError,
    TreeBuildError,
)

app = Typer()


@app.command()
def hello() -> None:
    """Confirm treebuild-cli is installed properly."""
    echo("Hello from treebuild!")


@app.command()
def demo() -> None:
    """Demonstrates (basic) treebuild workflow"""
    try:
        interactive_demo()
        raise Exit(code=0)
    except Abort:
        interrupt_demo()
        raise Exit(code=0)
    except TreeBuildError as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


@app.command()
def quickstart() -> None:
    """Interactive walkthrough, no need to know any of the commands."""
    try:
        quickstart_impl()
        raise Exit(code=0)
    except Abort:
        echo("\n Interrupting the quickstart setup. Your session is saved.")
        raise Exit(code=0)
    except TreeBuildError as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


@app.command()
def status() -> None:
    """Display current paths stored in session."""
    status_impl()
    raise Exit(code=0)


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
    try:
        chop_impl()
        raise Exit(code=0)
    except EmptySessionError as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)
