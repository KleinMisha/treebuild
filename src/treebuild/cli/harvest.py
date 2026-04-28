"""Harvest the tree: Render to text / scaffold <--> create all files and directories."""

from pathlib import Path
from typing import Annotated

from typer import Exit, Option, Typer, echo

from treebuild.cli.helpers import ensure_session_exists, load_message
from treebuild.core.settings import get_settings
from treebuild.rendering.factory import RenderMethod, get_renderer
from treebuild.storage.session import SessionStore
from treebuild.tree.builder import TreeBuilder

harvest_app = Typer(invoke_without_command=True, name="harvest")


@harvest_app.callback()
def harvest(
    method: Annotated[
        RenderMethod | None, Option("--renderer", help="Rendering method.")
    ] = None,
    show_root: Annotated[
        bool,
        Option(
            "--show-root", help="If used will display the root name as the top node."
        ),
    ] = False,
    root: Annotated[
        str,
        Option(
            help="Name of root directory. Will only be used if --show-root flag is used."
        ),
    ] = ".",
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

    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    ensure_session_exists(session_file)

    # Retrieve current tree's nodes
    session = SessionStore(session_file)
    if not (session.has_paths() or session.has_root()):
        msg = load_message("status_empty_tree.md")
        echo(msg)
        raise Exit(1)

    # Build the tree
    paths = [Path(entry) for entry in session.read_paths()]
    builder = TreeBuilder(root_name=root, paths=paths)
    tree = builder.assemble_tree()

    # Render to TXT
    rendering_method = method if method else settings.renderer
    renderer = get_renderer(rendering_method)

    _show_root = show_root
    if show_root and not session.has_root():
        msg = load_message("harvest_show_root_no_name.md")
        echo(msg)
        _show_root = False

    rendering = renderer.render_tree(tree, include_root=_show_root)
    echo(rendering)

    if to_file:
        to_file.write_text(rendering)
        echo(f"Written into file: {str(to_file)}")
