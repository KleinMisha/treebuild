"""Storage of paths between calls to the CLI (to assure persistence of data across multiple sessions)."""

from pathlib import Path
from typing import Optional

from treebuild.core.exceptions import DuplicatePathError

ROOT_NAME_PREFIX = "# ROOT:"


def normalize(entry: str) -> str:
    # Allow user to enter directory names as "folder/", i.e. with a trailing slash.
    stripped = entry.strip().lstrip("/")
    is_dir = stripped.endswith("/")
    normalized = str(Path(stripped))
    return normalized + "/" if is_dir else normalized


class SessionStore:
    """
    To save the paths in between CLI calls, so one does not need to write all paths in one go.
    -----

    A simple TXT-file to save paths added / removed from the collection.

    At the top of the file, the (optional) name of the root will be stored as: "# ROOT: <name>"
    """

    def __init__(self, file_path: Path) -> None:
        self.file = file_path
        # create the file if not yet existing (as well as any directories if needed)
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.touch(exist_ok=True)

    def read_paths(self) -> list[str]:
        """Load the list of paths already entered previously"""
        with self.file.open(mode="r") as f:
            lines = f.readlines()
        return [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith(ROOT_NAME_PREFIX)
        ]

    def write_path(self, entry: str) -> None:
        """
        Write a path (input as str) to storage.
        -----
        Duplicate entries (after normalization, removal of trailing '/' ) are rejected.
        """

        current_paths = self.read_paths()
        normalized = normalize(entry)
        if normalized in current_paths:
            raise DuplicatePathError(
                f"{normalized} already included in current session ({self.file})"
            )
        with self.file.open(mode="a") as f:
            f.write(normalized + "\n")

    def remove_path(self, entry: Optional[str] = None) -> None:
        """
        Remove a specific path str from the list (no actual tree-based operations done here)
        -----
        If no value for entry is given, the last entered path in the file will be removed.
        """
        root_name = self.read_root()
        current_paths = self.read_paths()
        path_to_delete = normalize(entry) if entry else current_paths[-1]
        paths_to_keep = [p for p in current_paths if p != path_to_delete]
        with self.file.open("w") as f:
            if root_name:
                f.write(f"{ROOT_NAME_PREFIX} {root_name}\n")

            for path in paths_to_keep:
                f.write(str(path))
                f.write("\n")

    def remove_all_paths(self) -> None:
        """Convenience method to remove all paths and just keep the root (if any)"""
        root_name = self.read_root()
        with self.file.open("w") as f:
            if root_name:
                f.write(f"{ROOT_NAME_PREFIX} {root_name}\n")

    def has_paths(self) -> bool:
        return len(self.read_paths()) > 0

    def read_root(self) -> str | None:
        """Read the root from the file (if present)"""
        with self.file.open(mode="r") as f:
            for line in f.readlines():
                if line.strip().startswith(ROOT_NAME_PREFIX):
                    return line.removeprefix(ROOT_NAME_PREFIX).strip()
        return None

    def write_root(self, root_name: str) -> None:
        """
        At the top of the file, the name of the root will be stored as: "# ROOT: <name>

        Will overwrite any root name stored previously.
        """
        new_root = f"{ROOT_NAME_PREFIX} {root_name}\n"
        lines = [f"{p}\n" for p in self.read_paths()]
        with self.file.open(mode="w") as f:
            lines.insert(0, new_root)
            f.writelines(lines)

    def remove_root(self) -> None:
        """Remove / Unset root"""
        paths = self.read_paths()
        with self.file.open("w") as f:
            for path in paths:
                f.write(str(path))
                f.write("\n")

    def has_root(self) -> bool:
        return self.read_root() is not None

    def clear_file(self) -> None:
        """Clear all contents"""
        with self.file.open(mode="w") as _:
            pass

    def delete_file(self) -> None:
        self.file.unlink(missing_ok=True)
