"""
A Directory tree consists of:
- Leaves <--> files (no further children)
- Branches <--> subdirectories (may be nested)
"""

from dataclasses import dataclass, field

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
    branches: list[Branch] = field(default_factory=list["Branch"])

    def add_leaf(self, filename: str) -> None:
        self.leaves.append(filename)

    def add_child_branch(self, branch: Branch) -> None:
        self.branches.append(branch)


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
