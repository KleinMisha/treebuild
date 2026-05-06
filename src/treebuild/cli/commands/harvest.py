"""Implementation of secondary commands, which will be called as 'treebuild harvest <COMMAND> <ARGS> <OPTIONS>'"""

from pathlib import Path
from typing import Optional

from treebuild.cli.helpers import NO_SESSION_MSG, load_message
from treebuild.core.exceptions import (
    EmptySessionError,
    NoRootSetError,
    RootDirNotFoundError,
)
from treebuild.core.settings import get_settings
from treebuild.harvest.materializer import Materializer
from treebuild.harvest.render_factory import RenderMethod, get_renderer
from treebuild.storage.session import SessionStore
from treebuild.tree.builder import TreeBuilder


def render_txt_impl(
    method: Optional[RenderMethod] = None,
    show_root: bool = False,
) -> str:
    """
    Use tree to get output: Render tree to TXT
    """

    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    # Retrieve current tree's nodes
    session = SessionStore(session_file)
    if not (session.has_paths() or session.has_root()):
        msg = load_message("status_empty_tree.md")
        raise EmptySessionError(msg)

    # read root from Session
    root_name = (
        session.read_root()
        if show_root
        else "Do not use the root in rendering, so do not care if it was set. "
    )
    if not root_name:
        raise NoRootSetError(
            "Set the name of the root directory and try again \n."
            "`treebuild seed <ROOT_NAME>` \n"
            "or render the tree without inclusion of the root's name (displays '.')\n"
            "`treebuild harvest text`"
        )

    # Build the tree
    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
    tree = builder.assemble_tree()

    # Render to text
    rendering_method = method if method else settings.renderer
    renderer = get_renderer(rendering_method)
    rendering = renderer.render_tree(tree, include_root=show_root)
    return rendering


def scaffold_impl(
    location: Optional[Path] = None,
    gitkeep: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Create the files and directories.
    """
    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)

    session = SessionStore(session_file)

    # check name of root directory is set:
    root_name = session.read_root()
    if not root_name:
        msg = load_message("harvest_scaffold_no_root_set.md")
        raise NoRootSetError(msg)

    # Build the tree
    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
    tree = builder.assemble_tree()

    # materialize the tree
    # TODO: use settings here to get base path as fallback.
    base_path = location or Path.cwd()
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path, gitkeep, dry_run)


def teardown_impl(location: Optional[Path] = None, dry_run: bool = False) -> None:
    """
    Remove the files and directories.
    (undoes `treebuild harvest scaffold`)
    """
    # Check if file for session exists:
    settings = get_settings()
    session_file = settings.session_file
    if not session_file.exists():
        raise EmptySessionError(NO_SESSION_MSG)
    session = SessionStore(session_file)

    # Build the tree
    root_name = session.read_root()
    if not root_name:
        msg = load_message("harvest_teardown_no_root_set.md")
        raise NoRootSetError(msg)

    builder = TreeBuilder(root_name=root_name, paths=session.read_paths())
    tree = builder.assemble_tree()

    # check if root directory exists
    base_path = location or Path.cwd()
    if not (base_path / tree.root.name).exists():
        msg = load_message("harvest_teardown_root_dir_does_not_exist.md")
        raise RootDirNotFoundError(msg.format(root_dir=str(base_path / tree.root.name)))

    # de-materialize the tree
    materializer = Materializer()
    materializer.dematerialize_tree(tree, base_path, dry_run)
