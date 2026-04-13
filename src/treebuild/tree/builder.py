"""
Assembling the directory tree
"""

from itertools import groupby
from pathlib import Path

from treebuild.tree.branches import Branch, Tree


class TreeBuilder:
    """Creates a Tree (a Branch) given a root and additional file paths."""

    def __init__(self, root_name: str, paths: list[Path]) -> None:
        self.root = root_name
        self._paths: list[Path] = paths

    @property
    def _items_below_root(self) -> list[Path]:
        directly_under_root: list[Path] = []
        for p in self._paths:
            if self._is_leaf(p):
                directly_under_root.append(p)
            else:
                directly_under_root.append(Path("/".join(p.parts[1:])))
        return directly_under_root

    def assemble_tree(self) -> Tree:
        root = self._assemble_branch(self.root, self._items_below_root)
        return Tree(root)

    def _assemble_branch(self, name: str, children: list[Path]) -> Branch:
        """
        Constructs a Branch with specified name and descendants.

        NOTE call this method recursively to build the entire tree.
        """
        # create the new branch
        branch = Branch(name)

        for _, group in groupby(sorted(children), key=self._common_ancestor):
            # Every group is an iterator of paths that start from the same ancestor directory (['foo/bar', 'foo/bli'], vs ['bla/boo', 'bla/bladiboo] in another group)
            children_same_parent = list(group)
            # If we are dealing with a file --> group has a single element (unique name for each file directly under this directory)
            # If we are dealing with a directory --> just perform one iteration per unique branch. Recursive calls already take care of placing all subsequent files in it.
            child = children_same_parent[0]
            if self._is_leaf(child):
                branch.add_leaf(child.name)
            else:
                # recurse: Repeat this procedure given the items below the given child
                descendants = self._find_descendants(child.parts[0], children)
                branch.add_child_branch(
                    self._assemble_branch(child.parts[0], descendants)
                )
        return branch

    def _find_descendants(self, parent: str, paths: list[Path]) -> list[Path]:
        """
        Given a directory name, filter the descendants / further descendants (items of which the directory is a common ancestor / the parent) from its siblings
        (items that share the same parent directory)
        """
        descendants: list[Path] = []
        for path in sorted(paths):
            if self._has_parent(parent, path):
                # add path, stripped from this common root/parent directory
                descendants.append(Path("/".join(path.parts[1:])))
        return descendants

    def _common_ancestor(self, path: Path) -> str:
        """Used in itertools.groupby call to only create a branch once."""
        return path.parts[0]

    def _has_parent(self, parent: str, path: Path) -> bool:
        return path.parts[0] == parent

    def _is_leaf(self, path: Path) -> bool:
        """A leaf is a path with no further descendants"""
        return len(path.parts) == 1
