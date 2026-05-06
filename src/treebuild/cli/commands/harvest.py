"""Implementation of secondary commands, which will be called as 'treebuild harvest <COMMAND> <ARGS> <OPTIONS>'"""

from typing import Optional

from treebuild.cli.helpers import load_message
from treebuild.core.exceptions import EmptySessionError, NoRootSetError
from treebuild.core.settings import get_settings
from treebuild.harvest.render_factory import RenderMethod, get_renderer
from treebuild.storage.session import SessionStore
from treebuild.tree.builder import TreeBuilder

NO_SESSION_MSG = load_message("status_no_tree.md")


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
