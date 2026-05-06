"""Secondary group of commands, which will be called as 'treebuild <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from typing import Annotated

from typer import Exit, Option, Typer, echo

from treebuild.cli.commands.harvest import render_txt_impl
from treebuild.cli.helpers import ensure_session_exists, load_message
from treebuild.core.exceptions import EmptySessionError, NoRootSetError
from treebuild.core.settings import get_settings
from treebuild.harvest.materializer import Materializer
from treebuild.harvest.render_factory import RenderMethod
from treebuild.storage.session import SessionStore
from treebuild.tree.builder import TreeBuilder

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
    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(session_file)

    # check name of root directory is set:
    # NOTE: The 'walrus operator' (:=) will automatically assign the value to `root_name`, which will persist if we exit this clause (and thus did not raise Exit(1))
    if not (root_name := session.read_root()):
        msg = load_message("harvest_scaffold_no_root_set.md")
        echo(msg)
        raise Exit(1)

    # Build the tree
    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
    tree = builder.assemble_tree()

    # materialize the tree
    # TODO: use settings here to get base path as fallback.
    base_path = location or Path.cwd()
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path, gitkeep, dry_run)
    if not dry_run:
        echo(f"Created: {base_path / tree.root.name}")


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
    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)
    session = SessionStore(session_file)

    # Build the tree
    if not (root_name := session.read_root() or None):
        msg = load_message("harvest_teardown_no_root_set.md")
        echo(msg)
        raise Exit(1)
    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
    tree = builder.assemble_tree()

    # check if root directory exists
    base_path = location or Path.cwd()
    if not (base_path / tree.root.name).exists():
        msg = load_message("harvest_teardown_root_dir_does_not_exist.md")
        echo(msg.format(root_dir=str(base_path / tree.root.name)))
        raise Exit(1)

    # de-materialize the tree
    materializer = Materializer()
    materializer.dematerialize_tree(tree, base_path, dry_run)
    echo(f"Removed: {base_path / tree.root.name}")
