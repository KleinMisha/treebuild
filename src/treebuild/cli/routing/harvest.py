"""Secondary group of commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from typing import Annotated

from typer import Exit, Option, Typer, echo

from treebuild.cli.commands.harvest import render_txt_impl, scaffold_impl, teardown_impl
from treebuild.core.exceptions import (
    EmptySessionError,
    NoRootSetError,
    RootDirNotFoundError,
)
from treebuild.core.settings import get_settings
from treebuild.harvest.render_factory import RenderMethod
from treebuild.storage.session import SessionStore

harvest_app = Typer(invoke_without_command=True, name="harvest")


@harvest_app.command()
def text(
    method: Annotated[
        RenderMethod | None, Option("--renderer", "-r", help="Rendering method.")
    ] = None,
    show_root: Annotated[
        bool,
        Option(
            "--show-root",
            help="If used will display the root name as the top node. NOTE: Requires a root name to be set for the current tree.",
        ),
    ] = False,
    to_file: Annotated[
        Path | None,
        Option(
            "--file",
            "-f",
            "--output",
            "-o",
            help="File to write rendered tree into.",
        ),
    ] = None,
) -> None:
    """
    Use tree to get output: Render tree to TXT
    """
    try:
        rendering = render_txt_impl(method, show_root)
        echo(rendering)
        if to_file:
            to_file.write_text(rendering)
            echo(f"Written into file: {str(to_file)}")
        raise Exit(code=0)
    except (EmptySessionError, NoRootSetError) as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


@harvest_app.command()
def scaffold(
    location: Annotated[
        Path | None,
        Option("--location", "-l", help="Where to place the root directory."),
    ] = None,
    gitkeep: Annotated[
        bool,
        Option(
            "--gitkeep",
            help="Adds dummy `.gitkeep` files into empty directories, such that git includes them.",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        Option(
            "--dry-run", help="Only print which files and directories would be created."
        ),
    ] = False,
) -> None:
    """
    Create the files and directories.
    """
    try:
        scaffold_impl(location, gitkeep, dry_run)
        if not dry_run:
            base_path = location or Path.cwd()
            settings = get_settings()
            session_file = settings.session_file
            session = SessionStore(session_file)
            root_name = session.read_root()
            # just to satisfy type-checker. Logically, this is condition guaranteed to be met as we did not raise NoRootSetError
            assert root_name is not None
            echo(f"Created: {base_path / root_name}")
        raise Exit(code=0)
    except (EmptySessionError, NoRootSetError) as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)


@harvest_app.command()
def teardown(
    location: Annotated[
        Path | None,
        Option("--location", "-l", help="Where to find the root directory."),
    ] = None,
    dry_run: Annotated[
        bool,
        Option(
            "--dry-run", help="Only print which files and directories would be removed."
        ),
    ] = False,
) -> None:
    """
    Remove the files and directories.
    (undoes `treebuild harvest scaffold`)
    """
    try:
        teardown_impl(location, dry_run)
        if not dry_run:
            base_path = location or Path.cwd()
            settings = get_settings()
            session_file = settings.session_file
            session = SessionStore(session_file)
            root_name = session.read_root()
            # just to satisfy type-checker. Logically, this is condition guaranteed to be met as we did not raise NoRootSetError
            assert root_name is not None
            echo(f"Removed: {base_path / root_name}")
        raise Exit(code=0)
    except (EmptySessionError, NoRootSetError, RootDirNotFoundError) as e:
        logging.error(f"{type(e).__name__}:{str(e)}")
        raise Exit(code=1)
