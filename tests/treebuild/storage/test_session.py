"""Unit tests for src/treebuild/session/session.py"""

from pathlib import Path

import pytest

from treebuild.core.exceptions import DuplicatePathError
from treebuild.storage.session import SessionStore, normalize


def test_read_and_write_paths(session_file: Path) -> None:
    """Write to a temporary file twice"""
    session = SessionStore(session_file)
    session.write_path("/path/to/file")
    session.write_path("/path/to/another/file")
    written_paths = session.read_paths()
    expected_paths = [
        normalize(fn) for fn in ["/path/to/file", "/path/to/another/file"]
    ]

    assert set(written_paths) == set(expected_paths)


def test_deleting_file(session_file: Path) -> None:
    """Removing the session's stored data."""
    session = SessionStore(session_file)
    session.delete_file()
    assert not session_file.exists()


def test_removing_last_path(session_file: Path) -> None:
    """Remove last entered path."""
    session = SessionStore(session_file)
    session.write_path("/first/path/")
    session.write_path("/second/path/")
    session.write_path("/third/path/")
    session.remove_path()
    expected_paths = [normalize(fn) for fn in ["/first/path/", "/second/path/"]]
    stored_paths = session.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_removing_middle_entry(session_file: Path) -> None:
    "Remove second of three paths entered"
    session = SessionStore(session_file)
    session.write_path("/first/path/")
    session.write_path("/second/path/")
    session.write_path("/third/path/")
    session.remove_path(entry="/second/path/")
    expected_paths = [normalize(fn) for fn in ["/first/path/", "/third/path/"]]
    stored_paths = session.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_removing_all_paths(session_file: Path) -> None:
    """Removing all paths"""
    session = SessionStore(session_file)
    session.write_path("/first/path/")
    session.write_path("/second/path/")
    session.write_path("/third/path/")
    session.remove_all_paths()
    assert session.read_paths() == []


@pytest.mark.parametrize(
    "duplicate",
    [
        "/first/path",  # exact duplicate
        "./first/path",  # relative to cwd
        "/first/path ",  # trailing spaces (normalization removes them)
    ],
)
def test_cannot_write_duplicate(session_file: Path, duplicate: str) -> None:
    """Attempting to write a duplicate path should raise an exception."""
    session = SessionStore(session_file)
    session.write_path("/first/path")
    with pytest.raises(DuplicatePathError):
        session.write_path(duplicate)


def test_duplicate_first_normalizes_entry(session_file: Path) -> None:
    """Attempt to write the same path, but the second time you omit the trailing slash."""
    session = SessionStore(session_file)
    session.write_path("/first/path")
    with pytest.raises(DuplicatePathError):
        session.write_path("/first/path")


@pytest.mark.parametrize(
    "root_name",
    [
        "root",  # simple string
        "path/to/root/dir",  # use slashes in name
    ],
)
def test_read_and_write_root(session_file: Path, root_name: str) -> None:
    """Write root name to file and retrieve it."""
    session = SessionStore(session_file)
    session.write_root(root_name)
    assert session.read_root() == root_name


def test_has_a_root(session_file: Path) -> None:
    """Set the root, should return True"""
    session = SessionStore(session_file)
    session.write_root("root")
    assert session.has_root()


def test_has_no_root(session_file: Path) -> None:
    """Only write paths, or add root, then remove, should not have a root in the file"""
    session = SessionStore(session_file)
    session.write_path("path/to/file")
    session.write_path("/path/to/another/file")
    assert not session.has_root()


def test_remove_root(session_file: Path) -> None:
    """Write, remove, then read (the now non-existing) root name."""
    session = SessionStore(session_file)
    session.write_root("root")
    session.remove_root()
    assert session.read_root() is None
    assert not session.has_root()


def test_has_paths(session_file: Path) -> None:
    """Should return True if at least one path is set."""
    session = SessionStore(session_file)
    session.write_path("a/valid/path")
    assert session.has_paths()


def test_has_no_paths(session_file: Path) -> None:
    """
    1. Only write a root to the file, should have no paths
    2. Write path(s), then remove them, should have no paths
    """
    # 1. Set a root, should not influence check for paths in file
    session = SessionStore(session_file)
    session.write_root("root")
    assert not session.has_paths()

    # 2. Removing all paths after adding some, should result in check failing
    session.write_path("a/valid/path")
    session.write_path("another_valid.path")
    session.remove_all_paths()
    assert not session.has_paths()


def test_remove_all_paths_preserves_root(session_file: Path) -> None:
    """Correctly get back root name after removing all other leaves and branches."""
    session = SessionStore(session_file)
    session.write_root("root")
    session.write_path("a/valid/path")
    session.write_path("another_valid.path")
    session.remove_all_paths()
    assert session.read_root() == "root"


def test_remove_root_preserves_paths(session_file: Path) -> None:
    """Correctly get back all other leaves and branches (paths) after removing the root name."""
    session = SessionStore(session_file)
    session.write_root("root")
    session.write_path("a/valid/path")
    session.write_path("another_valid.path")
    session.remove_root()
    assert set(session.read_paths()) == set(["a/valid/path", "another_valid.path"])


def test_read_and_write(session_file: Path) -> None:
    """Write both paths and root name"""
    root_name = "root"
    paths = ["/path/to/file", "/path/to/another/file"]
    session = SessionStore(session_file)
    session.write_root(root_name)
    for p in paths:
        session.write_path(p)

    assert set(session.read_paths()) == set([normalize(p) for p in paths])
    assert session.read_root() == root_name


def test_write_and_clear(session_file: Path) -> None:
    """Write to file and clear contents"""
    session = SessionStore(session_file)
    session.write_path("/path/to/file")
    session.write_path("/path/to/another/file")
    session.write_root("root")
    session.clear_file()
    assert (not session.has_paths()) and (not session.has_root())


def test_normalization_preserves_trailing_slash(session_file: Path) -> None:
    """Entering a path as `folder/` should be interpreted as a directory, so session should preserve this trailing slash."""
    session = SessionStore(session_file)
    session.write_path("/path/to/dir/")
    assert "path/to/dir/" in session.read_paths()


def test_trailing_slash_not_counted_as_duplicate(session_file: Path) -> None:
    """some/path/ and some/path should be treated differently"""
    session = SessionStore(session_file)
    session.write_path("/some/path/")
    session.write_path("/some/path")
    assert len(session.read_paths()) == 2
