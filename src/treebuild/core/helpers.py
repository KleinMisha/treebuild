"""Helper methods used across layers of the app."""

from pathlib import Path

POUND_SIGN = "#"


def read_paths_from_file(file: Path) -> list[str]:
    """
    Load paths from a file.
    assumes
    - one path per line
    - additional metadata (like the root name, or comments) are preceded by a '#'
    """

    with file.open(mode="r") as f:
        lines = f.readlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith(POUND_SIGN)
    ]
