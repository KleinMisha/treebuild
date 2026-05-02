"""Create files and directories based on built tree structure."""

import logging
import shutil
from pathlib import Path
from typing import Optional

from treebuild.tree.branches import Branch, Tree


class Materializer:
    """
    Writes / Deletes files (+ directories) in the file system.
    """

    def materialize_tree(
        self,
        tree: Tree,
        base_path: Optional[Path] = None,
        gitkeep: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Build all files/directories based on the given Tree."""

        # Create root directory
        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name
        self._create_dir(root_path, dry_run)

        # add a `.gitkeep` file in empty repository
        if tree.is_empty and gitkeep:
            self._create_file((root_path / ".gitkeep"), dry_run)

        # start recursion
        self._materialize_branch(tree.root, root_path, gitkeep, dry_run)

    def _materialize_branch(
        self,
        branch: Branch,
        current_path: Path,
        gitkeep: bool = False,
        dry_run: bool = False,
    ) -> None:
        """
        Recursive workhorse: Create child directories (and files within them)
        """

        # create directories
        for child_dir in branch.branches:
            # create the new directory
            child_path = current_path / child_dir.name
            self._create_dir(child_path, dry_run)

            if child_dir.is_empty and gitkeep:
                self._create_file((child_path / ".gitkeep"), dry_run)

            # traverse into the child directory to check for additional children
            self._materialize_branch(child_dir, child_path, gitkeep, dry_run)

        # Create files inside the current directory
        for filename in branch.leaves:
            file_path = current_path / filename
            self._create_file(file_path, dry_run)

    def dematerialize_tree(
        self, tree: Tree, base_path: Optional[Path] = None, dry_run: bool = False
    ) -> None:
        """Delete all files/directory of the given Tree"""
        # TODO: use settings here to get base path as fallback.
        base_path = base_path or Path.cwd()
        root_path = base_path / tree.root.name

        # If no root directory anymore...
        if not root_path.exists():
            logging.info(f"Nothing to remove. Root directory not found: {root_path}")
            return

        # If dry-run (do not do anything besides logging)
        if dry_run:
            for path in tree.paths:
                logging.info(f"Would remove: {base_path / path}")
            return

        # happy case: remove the tree's items from disc.
        shutil.rmtree(root_path)
        for path in tree.paths:
            logging.debug(f"Removed: {base_path / path}")

    def _create_dir(self, directory: Path, dry_run: bool) -> None:
        """Helper to ensure that dry-run is a no-op (only logging)."""
        if dry_run:
            logging.info(f"Would create directory: {directory}")
            return

        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Created directory: {directory}")

    def _create_file(self, file: Path, dry_run: bool) -> None:
        """Helper to ensure that dry-run is a no-op (only logging)."""
        if dry_run:
            logging.info(f"Would create file: {file}")
            return

        file.touch(exist_ok=True)
        logging.debug(f"Created file: {file}")
