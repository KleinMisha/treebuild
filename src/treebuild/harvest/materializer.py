"""Create files and directories based on built tree structure."""

import logging
import shutil
from pathlib import Path
from typing import Optional

from treebuild.tree.branches import Branch, Tree


class Materializer:
    """
    Writes / Deletes files (+ directories) in the file system.

    #TODO include option to automatically add ".gitkeep" files in otherwise empty directories.
    """

    def materialize_tree(self, tree: Tree, base_path: Optional[Path] = None) -> None:
        """Build all files/directories based on the given Tree."""

        # Create root directory
        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name
        root_path.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Created root directory: {root_path}")

        # start recursion
        self._materialize_branch(tree.root, root_path)

    def _materialize_branch(self, branch: Branch, current_path: Path) -> None:
        """
        Recursive workhorse: Create child directories (and files within them)
        """

        # create directories
        for child_dir in branch.branches:
            # create the new directory
            child_path = current_path / child_dir.name
            child_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Created child directory: {child_path}")

            # traverse into the child directory to check for additional children
            self._materialize_branch(child_dir, child_path)

        # Create files inside the current directory
        for filename in branch.leaves:
            file_path = current_path / filename
            file_path.touch(exist_ok=True)
            logging.debug(f"Created file: {file_path}")

    def dematerialize_tree(self, tree: Tree, base_path: Optional[Path] = None) -> None:
        """Delete all files/directory of the given Tree"""

        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name

        for path in tree.paths:
            logging.debug(f"Removing: {path}")

        if root_path.exists():
            shutil.rmtree(root_path)
