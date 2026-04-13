"""Unit tests for src/treebuild/storage/session.py"""

from pathlib import Path

import pytest

from treebuild.core.exceptions import DuplicatePathError
from treebuild.storage.session import SessionStore


def test_file_is_created_at_instantiation(tmp_path: Path) -> None:
    """Check that file exists after instantiation of the SessionStore"""

    temp_file = tmp_path / "session.txt"
    _ = SessionStore(temp_file)
    assert temp_file.exists()


def test_read_and_write(tmp_path: Path) -> None:
    """Write to a temporary file twice"""
    # write twice
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/path/to/file")
    storage.write_path("/path/to/another/file")
    written_paths = storage.load()
    expected_paths = [
        str(Path(fn)) for fn in ["/path/to/file", "/path/to/another/file"]
    ]

    assert set(written_paths) == set(expected_paths)


def test_write_and_clear(tmp_path: Path) -> None:
    """Write to file and clear contents"""
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/path/to/file")
    storage.write_path("/path/to/another/file")
    storage.clear_file()
    assert set(storage.load()) == set()


def test_deleting_file(tmp_path: Path) -> None:
    """Removing the session's stored data."""
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.delete_file()
    assert not temp_file.exists()


def test_removing_last_path(tmp_path: Path) -> None:
    """Remove last entered path."""
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/first/path/")
    storage.write_path("/second/path/")
    storage.write_path("/third/path/")
    storage.remove_path()
    expected_paths = [str(Path(fn)) for fn in ["/first/path/", "/second/path/"]]
    stored_paths = storage.load()
    assert set(stored_paths) == set(expected_paths)


def test_removing_middle_entry(tmp_path: Path) -> None:
    "Remove second of three paths entered"
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/first/path/")
    storage.write_path("/second/path/")
    storage.write_path("/third/path/")
    storage.remove_path(entry="/second/path/")
    expected_paths = [str(Path(fn)) for fn in ["/first/path/", "/third/path/"]]
    stored_paths = storage.load()
    assert set(stored_paths) == set(expected_paths)


def test_cannot_write_duplicate(tmp_path: Path) -> None:
    """Attempting to write a duplicate path should raise an exception."""
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/first/path/")
    with pytest.raises(DuplicatePathError):
        storage.write_path("/first/path/")


def test_duplicate_first_normalizes_entry(tmp_path: Path) -> None:
    """Attempt to write the same path, but the second time you omit the trailing slash."""
    temp_file = tmp_path / "session.txt"
    storage = SessionStore(temp_file)
    storage.write_path("/first/path/")
    with pytest.raises(DuplicatePathError):
        storage.write_path("/first/path")
