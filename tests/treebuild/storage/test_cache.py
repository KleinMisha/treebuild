"""Unit tests for src/treebuild/storage/cache.py"""

from pathlib import Path

from treebuild.storage.cache import CacheStore


def test_read_and_write_tree_name(cache_file: Path) -> None:
    store = CacheStore(cache_file)
    store.write_current_tree("project-name")
    assert store.read_current_tree() == "project-name"


def test_read_and_write_root_dir_location(cache_file: Path) -> None:
    store = CacheStore(cache_file)
    store.write_root_location(Path("path/to/project"))
    assert store.read_root_location() == Path("path/to/project")


def test_read_and_write_local_treebuild_dir_parent(cache_file: Path) -> None:
    store = CacheStore(cache_file)
    store.write_local_dir_parent(Path(".treebuild/parent"))
    assert store.read_local_dir_parent() == Path(".treebuild/parent")


def test_read_and_write_multiple(cache_file: Path) -> None:
    """To assure different values are not overwritten"""
    store = CacheStore(cache_file)
    store.write_current_tree("project-name")
    store.write_root_location(Path("path/to/project"))
    assert store.read_current_tree() == "project-name"
    assert store.read_root_location() == Path("path/to/project")


def test_clear_file(cache_file: Path) -> None:
    store = CacheStore(cache_file)
    store.write_current_tree("project-name")
    store.write_root_location(Path("path/to/project"))
    store.write_local_dir_parent(Path(".treebuild/parent"))
    store.clear_file()
    assert store.read_current_tree() is None
    assert store.read_root_location() is None
    assert store.read_local_dir_parent() is None


def test_delete_file(cache_file: Path) -> None:
    store = CacheStore(cache_file)
    store.delete_file()
    assert not cache_file.exists()
