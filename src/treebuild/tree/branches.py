"""
A Directory tree consists of:
- Leaves <--> files (no further children)
- Branches <--> subdirectories (may be nested)
"""

from dataclasses import dataclass, field
from pathlib import Path

# A filename represents a Leaf in the tree.
type Leaf = str


@dataclass
class Branch:
    """
    A branch node in the tree
    ------
    * Top directory name
    * files are leaves
    * subdirectories are nested branches
    """

    name: str
    leaves: list[str] = field(default_factory=list[str])
    branches: list["Branch"] = field(default_factory=list["Branch"])

    @property
    def is_empty(self) -> bool:
        """An empty directory has no child directories or files inside it."""
        return not (self.leaves or self.branches)

    def add_leaf(self, filename: str) -> None:
        self.leaves.append(filename)

    def add_child_branch(self, branch: "Branch") -> None:
        self.branches.append(branch)

    def all_paths(self, current_path: Path) -> list[Path]:
        """All the paths in this (child) directory."""
        paths = [current_path]
        paths.extend([current_path / leaf for leaf in self.leaves])

        # traversal / recursion:
        for branch in self.branches:
            paths.extend(branch.all_paths(current_path / branch.name))
        return paths


@dataclass
class Tree:
    """
    A directory tree defines the root Branch from which the tree starts.
    ----

    NOTE technically a Tree is just a Branch. Using this thin wrapper makes future definitions more expressive.
    """

    root: Branch

    def add_leaf(self, filename: str) -> None:
        """Wrapper for convenience"""
        self.root.add_leaf(filename)

    def add_branch(self, branch: Branch) -> None:
        """Wrapper for convenience"""
        self.root.add_child_branch(branch)

    @property
    def is_empty(self) -> bool:
        "Wrapper for convenience"
        return self.root.is_empty

    @property
    def paths(self) -> list[str]:
        """Paths (at deepest level) as strings"""
        all_paths = [Path(self.root.name)]
        all_paths.extend(self.root.all_paths(Path(self.root.name)))

        # Only keep root/dir/some.file , and remove root and root/dir in this case
        deepest_paths = [
            str(path)
            for path in all_paths
            if not any(
                other_path != path and path in other_path.parents
                for other_path in all_paths
            )
        ]

        return deepest_paths
