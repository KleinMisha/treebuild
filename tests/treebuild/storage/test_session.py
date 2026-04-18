"""Unit tests for src/treebuild/storage/session.py"""

from pathlib import Path

import pytest

from treebuild.core.exceptions import DuplicatePathError
from treebuild.storage.session import SessionStore


def test_read_and_write_paths(session_file: Path) -> None:
    """Write to a temporary file twice"""
    storage = SessionStore(session_file)
    storage.write_path("/path/to/file")
    storage.write_path("/path/to/another/file")
    written_paths = storage.read_paths()
    expected_paths = [
        str(Path(fn)) for fn in ["/path/to/file", "/path/to/another/file"]
    ]

    assert set(written_paths) == set(expected_paths)


def test_deleting_file(session_file: Path) -> None:
    """Removing the session's stored data."""
    storage = SessionStore(session_file)
    storage.delete_file()
    assert not session_file.exists()


def test_removing_last_path(session_file: Path) -> None:
    """Remove last entered path."""
    storage = SessionStore(session_file)
    storage.write_path("/first/path/")
    storage.write_path("/second/path/")
    storage.write_path("/third/path/")
    storage.remove_path()
    expected_paths = [str(Path(fn)) for fn in ["/first/path/", "/second/path/"]]
    stored_paths = storage.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_removing_middle_entry(session_file: Path) -> None:
    "Remove second of three paths entered"
    storage = SessionStore(session_file)
    storage.write_path("/first/path/")
    storage.write_path("/second/path/")
    storage.write_path("/third/path/")
    storage.remove_path(entry="/second/path/")
    expected_paths = [str(Path(fn)) for fn in ["/first/path/", "/third/path/"]]
    stored_paths = storage.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_cannot_write_duplicate(session_file: Path) -> None:
    """Attempting to write a duplicate path should raise an exception."""
    storage = SessionStore(session_file)
    storage.write_path("/first/path/")
    with pytest.raises(DuplicatePathError):
        storage.write_path("/first/path/")


def test_duplicate_first_normalizes_entry(session_file: Path) -> None:
    """Attempt to write the same path, but the second time you omit the trailing slash."""
    storage = SessionStore(session_file)
    storage.write_path("/first/path/")
    with pytest.raises(DuplicatePathError):
        storage.write_path("/first/path")


@pytest.mark.parametrize(
    "root_name",
    [
        "root",  # simple string
        "path/to/root/dir",  # use slashes in name
    ],
)
def test_read_and_write_root(session_file: Path, root_name: str) -> None:
    """Write root name to file and retrieve it."""
    storage = SessionStore(session_file)
    storage.write_root(root_name)
    assert storage.read_root() == root_name


def test_write_and_clear(session_file: Path) -> None:
    """Write to file and clear contents"""
    storage = SessionStore(session_file)
    storage.write_path("/path/to/file")
    storage.write_path("/path/to/another/file")
    storage.clear_file()
    assert set(storage.read_paths()) == set()
