"""
Assembling the directory tree
"""

from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

from treebuild.tree.branches import Branch, Tree


@dataclass
class TreePath:
    path: Path
    is_dir: bool


class TreeBuilder:
    """Creates a Tree (a Branch) given a root and additional file paths."""

    def __init__(self, root_name: str, paths: list[str]) -> None:
        self.root = root_name
        self._paths: list[TreePath] = []
        for p in paths:
            _is_dir = False
            if p.endswith("/"):
                _is_dir = True
            self._paths.append(TreePath(Path(p), _is_dir))

    @property
    def _items_below_root(self) -> list[TreePath]:
        directly_under_root: list[TreePath] = []
        for p in self._paths:
            # If a file is directly placed in the root, do not strip the path first
            if len(p.path.parts) == 1:
                directly_under_root.append(p)
            else:
                # strip nested paths first
                directly_under_root.append(
                    TreePath(Path("/".join(p.path.parts[1:])), p.is_dir)
                )
        return directly_under_root

    def assemble_tree(self) -> Tree:
        root = self._assemble_branch(self.root, self._items_below_root)
        return Tree(root)

    def _assemble_branch(self, name: str, children: list[TreePath]) -> Branch:
        """
        Constructs a Branch with specified name and descendants.

        NOTE call this method recursively to build the entire tree.
        """
        # create the new branch
        branch = Branch(name)

        for _, group in groupby(
            sorted(children, key=self._common_ancestor), key=self._common_ancestor
        ):
            # Every group is an iterator of paths that start from the same ancestor directory (['foo/bar', 'foo/bli'], vs ['bla/boo', 'bla/bladiboo] in another group)
            children_same_parent = list(group)
            # If we are dealing with a file --> group has a single element (unique name for each file directly under this directory)
            # If we are dealing with a directory --> just perform one iteration per unique branch. Recursive calls already take care of placing all subsequent files in it.
            child = children_same_parent[0]
            if self._is_leaf(child):
                branch.add_leaf(child.path.name)
            elif self._is_empty_branch(child):
                branch.add_child_branch(Branch(child.path.name))
            else:
                # recurse: Repeat this procedure given the items below the given child
                descendants = self._find_descendants(child.path.parts[0], children)
                branch.add_child_branch(
                    self._assemble_branch(child.path.parts[0], descendants)
                )
        return branch

    def _find_descendants(self, parent: str, paths: list[TreePath]) -> list[TreePath]:
        """
        Given a directory name, filter the descendants / further descendants (items of which the directory is a common ancestor / the parent) from its siblings
        (items that share the same parent directory)
        """
        descendants: list[TreePath] = []
        for p in sorted(paths, key=self._common_ancestor):
            if self._has_parent(parent, p):
                # add path, stripped from this common root/parent directory
                descendants.append(TreePath(Path("/".join(p.path.parts[1:])), p.is_dir))
        return descendants

    def _common_ancestor(self, p: TreePath) -> str:
        """Used in itertools.groupby call to only create a branch once."""
        return p.path.parts[0] if p.path.parts else ""

    def _has_parent(self, parent: str, p: TreePath) -> bool:
        return p.path.parts[0] == parent

    def _is_leaf(self, p: TreePath) -> bool:
        """Is this a file at the current level? (That is it is not a directory and has no further descendants.)"""
        return not p.is_dir and len(p.path.parts) == 1

    def _is_empty_branch(self, p: TreePath) -> bool:
        """Is this a directory that has no file inside? (It is a single directory, and has no further descendants. )"""
        return p.is_dir and len(p.path.parts) == 1
