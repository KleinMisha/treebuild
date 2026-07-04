"""Unit tests for src/treebuild/storage/tree_store.py"""

from pathlib import Path

import pytest

from treebuild.core.exceptions import DuplicatePathError
from treebuild.storage.tree_store import TreeStore, normalize


def test_read_and_write_paths(store_file: Path) -> None:
    """Write to a temporary file twice"""
    store = TreeStore(store_file)
    store.write_path("/path/to/file")
    store.write_path("/path/to/another/file")
    written_paths = store.read_paths()
    expected_paths = [
        normalize(fn) for fn in ["/path/to/file", "/path/to/another/file"]
    ]

    assert set(written_paths) == set(expected_paths)


def test_deleting_file(store_file: Path) -> None:
    """Removing the store's stored data."""
    store = TreeStore(store_file)
    store.delete_file()
    assert not store_file.exists()


def test_removing_last_path(store_file: Path) -> None:
    """Remove last entered path."""
    store = TreeStore(store_file)
    store.write_path("/first/path/")
    store.write_path("/second/path/")
    store.write_path("/third/path/")
    store.remove_path()
    expected_paths = [normalize(fn) for fn in ["/first/path/", "/second/path/"]]
    stored_paths = store.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_removing_middle_entry(store_file: Path) -> None:
    "Remove second of three paths entered"
    store = TreeStore(store_file)
    store.write_path("/first/path/")
    store.write_path("/second/path/")
    store.write_path("/third/path/")
    store.remove_path(entry="/second/path/")
    expected_paths = [normalize(fn) for fn in ["/first/path/", "/third/path/"]]
    stored_paths = store.read_paths()
    assert set(stored_paths) == set(expected_paths)


def test_removing_all_paths(store_file: Path) -> None:
    """Removing all paths"""
    store = TreeStore(store_file)
    store.write_path("/first/path/")
    store.write_path("/second/path/")
    store.write_path("/third/path/")
    store.remove_all_paths()
    assert store.read_paths() == []


@pytest.mark.parametrize(
    "duplicate",
    [
        "/first/path",  # exact duplicate
        "./first/path",  # relative to cwd
        "/first/path ",  # trailing spaces (normalization removes them)
    ],
)
def test_cannot_write_duplicate(store_file: Path, duplicate: str) -> None:
    """Attempting to write a duplicate path should raise an exception."""
    store = TreeStore(store_file)
    store.write_path("/first/path")
    with pytest.raises(DuplicatePathError):
        store.write_path(duplicate)


def test_duplicate_first_normalizes_entry(store_file: Path) -> None:
    """Attempt to write the same path, but the second time you omit the trailing slash."""
    store = TreeStore(store_file)
    store.write_path("/first/path")
    with pytest.raises(DuplicatePathError):
        store.write_path("/first/path")


@pytest.mark.parametrize(
    "root_name",
    [
        "root",  # simple string
        "path/to/root/dir",  # use slashes in name
    ],
)
def test_read_and_write_root(store_file: Path, root_name: str) -> None:
    """Write root name to file and retrieve it."""
    store = TreeStore(store_file)
    store.write_root(root_name)
    assert store.read_root() == root_name


def test_has_a_root(store_file: Path) -> None:
    """Set the root, should return True"""
    store = TreeStore(store_file)
    store.write_root("root")
    assert store.has_root()


def test_has_no_root(store_file: Path) -> None:
    """Only write paths, or add root, then remove, should not have a root in the file"""
    store = TreeStore(store_file)
    store.write_path("path/to/file")
    store.write_path("/path/to/another/file")
    assert not store.has_root()


def test_remove_root(store_file: Path) -> None:
    """Write, remove, then read (the now non-existing) root name."""
    store = TreeStore(store_file)
    store.write_root("root")
    store.remove_root()
    assert store.read_root() is None
    assert not store.has_root()


def test_has_paths(store_file: Path) -> None:
    """Should return True if at least one path is set."""
    store = TreeStore(store_file)
    store.write_path("a/valid/path")
    assert store.has_paths()


def test_has_no_paths(store_file: Path) -> None:
    """
    1. Only write a root to the file, should have no paths
    2. Write path(s), then remove them, should have no paths
    """
    # 1. Set a root, should not influence check for paths in file
    store = TreeStore(store_file)
    store.write_root("root")
    assert not store.has_paths()

    # 2. Removing all paths after adding some, should result in check failing
    store.write_path("a/valid/path")
    store.write_path("another_valid.path")
    store.remove_all_paths()
    assert not store.has_paths()


def test_remove_path_preserves_root(store_file: Path) -> None:
    """Correctly get back root name after removing a specific leaf or branch."""
    store = TreeStore(store_file)
    store.write_root("root")
    store.write_path("a/valid/path")
    store.write_path("another_valid.path")
    store.remove_path("another_valid.path")
    assert store.read_root() == "root"


def test_remove_all_paths_preserves_root(store_file: Path) -> None:
    """Correctly get back root name after removing all other leaves and branches."""
    store = TreeStore(store_file)
    store.write_root("root")
    store.write_path("a/valid/path")
    store.write_path("another_valid.path")
    store.remove_all_paths()
    assert store.read_root() == "root"


def test_remove_root_preserves_paths(store_file: Path) -> None:
    """Correctly get back all other leaves and branches (paths) after removing the root name."""
    store = TreeStore(store_file)
    store.write_root("root")
    store.write_path("a/valid/path")
    store.write_path("another_valid.path")
    store.remove_root()
    assert set(store.read_paths()) == set(["a/valid/path", "another_valid.path"])


def test_read_and_write(store_file: Path) -> None:
    """Write both paths and root name"""
    root_name = "root"
    paths = ["/path/to/file", "/path/to/another/file"]
    store = TreeStore(store_file)
    store.write_root(root_name)
    for p in paths:
        store.write_path(p)

    assert set(store.read_paths()) == set([normalize(p) for p in paths])
    assert store.read_root() == root_name


def test_write_and_clear(store_file: Path) -> None:
    """Write to file and clear contents"""
    store = TreeStore(store_file)
    store.write_path("/path/to/file")
    store.write_path("/path/to/another/file")
    store.write_root("root")
    store.clear_file()
    assert (not store.has_paths()) and (not store.has_root())


def test_normalization_preserves_trailing_slash(store_file: Path) -> None:
    """Entering a path as `folder/` should be interpreted as a directory, so store should preserve this trailing slash."""
    store = TreeStore(store_file)
    store.write_path("/path/to/dir/")
    assert "path/to/dir/" in store.read_paths()


def test_trailing_slash_not_counted_as_duplicate(store_file: Path) -> None:
    """some/path/ and some/path should be treated differently"""
    store = TreeStore(store_file)
    store.write_path("/some/path/")
    store.write_path("/some/path")
    assert len(store.read_paths()) == 2


def test_adding_items_to_empty_dir(store_file: Path) -> None:
    """Adding a file to an initially empty directory should remove the now redundant path to the empty directory."""
    store = TreeStore(store_file)
    store.write_path("/empty_dir/")
    store.write_path("empty_dir/no_longer.txt")
    assert store.read_paths() == ["empty_dir/no_longer.txt"]


def test_adding_items_to_grandchild_makes_existing_dir_redundant(
    store_file: Path,
) -> None:
    """Adding path/, then add path/to/some/file.py, should eliminate the first entry as it has now become redundant."""
    store = TreeStore(store_file)
    store.write_path("path/")
    store.write_path("path/to/some/file.py")
    assert store.read_paths() == ["path/to/some/file.py"]


def test_adding_a_file_removes_multiple_redundant_ancestors(store_file: Path) -> None:
    """If grandchild is added, then child and parent cannot be an empty directory anymore."""
    store = TreeStore(store_file)
    store.write_path("path/")
    store.write_path("path/to/")
    store.write_path("path/to/file.md")
    assert store.read_paths() == ["path/to/file.md"]


def test_rejecting_redundant_dirname(store_file: Path) -> None:
    """Adding a parent directory to an already added path should reject the new entry."""
    store = TreeStore(store_file)
    store.write_path("path/to/file.txt")
    # test with parent
    with pytest.raises(DuplicatePathError):
        store.write_path("path/to/")
    # test with grandparent
    with pytest.raises(DuplicatePathError):
        store.write_path("path/")


def test_adding_file_to_empty_dir_keeps_siblings(store_file: Path) -> None:
    """Check sibling directories are not removed by accident"""
    store = TreeStore(store_file)
    store.write_path("parent/child/")
    store.write_path("parent/sibling/")
    store.write_path("parent/child/file.bla")
    assert set(store.read_paths()) == set(["parent/child/file.bla", "parent/sibling/"])
