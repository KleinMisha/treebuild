"""(Abstract) Base Class for a tree renderer"""

from abc import ABC, abstractmethod
from enum import Enum, auto

from treebuild.tree.branches import Branch, Tree


class Connector(Enum):
    EMPTY = auto()
    CONTINUATION = auto()
    MIDDLE_CHILD = auto()
    FINAL_CHILD = auto()


class Renderer(ABC):
    """Rendering tree structure as strings."""

    @property
    @abstractmethod
    def _connectors(self) -> dict[Connector, str]: ...

    def render_tree(self, tree: Tree, include_root: bool = False) -> str:
        """Render the directory tree structure."""

        # add root name:
        first_line = tree.root.name if include_root else "."
        # Start recursion, from empty set of flags.
        lines = self._render_branch(tree.root, [])
        return "\n".join([first_line] + lines)

    def _render_branch(self, branch: Branch, ancestor_is_last: list[bool]) -> list[str]:
        """
        Recursive workhorse: Generate partial tree structure (with given branch as starting point)
        ----
        branch: Starting point
        ancestor_is_last: list of boolean flags indicating wether we need a blanc indentation or a continuation connection.
        """
        lines: list[str] = []

        # Place directories above files in rendering --> Recursive call
        for dir_num, child_dir in enumerate(branch.branches):
            is_last = (dir_num == (len(branch.branches) - 1)) and (
                len(branch.leaves) == 0
            )
            last_ancestor_reached = ancestor_is_last + [is_last]
            # place the directory itself in the tree
            new_line = self._format_line(child_dir.name, last_ancestor_reached)
            lines.append(new_line)

            # Recurse into the subdirectory and place it's children in the tree
            lines.extend(self._render_branch(child_dir, last_ancestor_reached))

        # Place files below directories
        for file_num, filename in enumerate(branch.leaves):
            is_last = file_num == (len(branch.leaves) - 1)
            last_ancestor_reached = ancestor_is_last + [is_last]
            new_line = self._format_line(filename, last_ancestor_reached)
            lines.append(new_line)
        return lines

    @abstractmethod
    def _format_line(self, name: str, ancestor_is_last: list[bool]) -> str:
        """Rendering a single line is implementation dependent"""
        ...
