"""Create files and directories based on built tree structure."""

import shutil
from pathlib import Path
from typing import Optional

from treebuild.tree.branches import Branch, Tree


class FileCreator:
    """Creates / Deletes files (+ directories) in the file system."""

    def scaffold_tree(self, tree: Tree, base_path: Optional[Path] = None) -> None:
        """Build all files/directories based on the given Tree."""

        # Create root directory
        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name
        root_path.mkdir(parents=True, exist_ok=True)

        # start recursion
        self._scaffold_branch(tree.root, root_path)

    def _scaffold_branch(self, branch: Branch, current_path: Path) -> None:
        """
        Recursive workhorse: Create child directories (and files within them)
        """

        # create directories
        for child_dir in branch.branches:
            # create the new directory
            child_path = current_path / child_dir.name
            child_path.mkdir(parents=True, exist_ok=True)

            # traverse into the child directory to check for additional children
            self._scaffold_branch(child_dir, child_path)

        # Create files inside the current directory
        for filename in branch.leaves:
            file_path = current_path / filename
            file_path.touch(exist_ok=True)

    def teardown_tree(self, tree: Tree, base_path: Optional[Path] = None) -> None:
        """Delete all files/directory of the given Tree"""

        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name
        if root_path.exists():
            shutil.rmtree(root_path)
