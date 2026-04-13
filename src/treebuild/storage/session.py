"""Storage of paths between calls to the CLI (to assure persistence of data across multiple sessions)."""

from pathlib import Path
from typing import Optional

from treebuild.core.exceptions import DuplicatePathError

# todo: Move this into a config file later
DEFAULT_FILE_LOCATION = Path.home() / ".config" / "treebuild" / "session.txt"


class SessionStore:
    """
    To save the paths in between CLI calls, so one does not need to write all paths in one go.
    -----

    A simple TXT-file to save paths added / removed from the collection.
    """

    def __init__(self, file_path: Path = DEFAULT_FILE_LOCATION) -> None:
        self.file = file_path
        # create the file if not yet existing (as well as any directories if needed)
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.touch(exist_ok=True)

    def load(self) -> list[str]:
        """Load the list of paths already entered previously"""
        with self.file.open(mode="r") as f:
            lines = f.readlines()
        return [line.strip() for line in lines]

    def write_path(self, entry: str) -> None:
        """
        Write a path (input as str) to storage.
        -----
        Duplicate entries (after normalization, removal of trailing '/' ) are rejected.
        """

        current_paths = self.load()
        normalized = self._normalize(entry)
        if normalized in current_paths:
            raise DuplicatePathError(
                f"{normalized} already included in current session ({self.file})"
            )
        with self.file.open(mode="a") as f:
            f.write(normalized + "\n")

    def clear_file(self) -> None:
        """Clear all contents"""
        with self.file.open(mode="w") as _:
            pass

    def delete_file(self) -> None:
        self.file.unlink(missing_ok=True)

    def remove_path(self, entry: Optional[str] = None) -> None:
        """
        Remove a specific path str from the list (no actual tree-based operations done here)
        -----
        If no value for entry is given, the last entered path in the file will be removed.
        """
        current_paths = self.load()
        path_to_delete = self._normalize(entry) if entry else current_paths[-1]
        paths_to_keep = [p for p in current_paths if p != path_to_delete]
        with self.file.open("w") as f:
            for path in paths_to_keep:
                f.write(str(path))
                f.write("\n")

    def _normalize(self, entry: str) -> str:
        return str(Path(entry))
