"""unit tests for src/treebuild/harvest/settings.py"""

from pathlib import Path

from treebuild.core.settings import (
    GLOBAL_TREEBUILD_DIR,
    LOCAL_TREEBUILD_DIR,
    SettingsLevel,
    resolve_treebuild_dir,
)


def test_resolve_path_to_global_treebuild_dir() -> None:
    assert (
        resolve_treebuild_dir(SettingsLevel.GLOBAL, Path("does/not/matter"))
        == GLOBAL_TREEBUILD_DIR
    )


def test_local_dir_at_present_location(tmp_path: Path) -> None:
    """Place .treebuild/ directly at the start of the search"""
    expected_dir = tmp_path / ".treebuild/"
    expected_dir.mkdir(exist_ok=True)
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, tmp_path) == expected_dir


def test_local_dir_in_parent(tmp_path: Path) -> None:
    """Place .treebuild/ in the parent compared to where we start the search from"""
    expected_dir = tmp_path / ".treebuild"
    expected_dir.mkdir(exist_ok=True)

    start_search = tmp_path / "subdir/"
    start_search.mkdir(exist_ok=True)
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, start_search) == expected_dir


def test_default_local_dir_if_non_existing(tmp_path: Path) -> None:
    """If no local .treebuild/ directory exists --> should return a default local path"""
    expected_dir = tmp_path / LOCAL_TREEBUILD_DIR
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, tmp_path) == expected_dir


def test_resolve_local_dir_from_multiple(tmp_path: Path) -> None:
    """
    Place .treebuild/ both in tmp_path as well as in tmp_path/second_lvl/third_lvl/.treebuild/.
    Should find the directory closest to the start of the search + only search upwards
    (So searching from middle level should find the one in the top level)
    """
    # Setup filesystem
    first_level = tmp_path
    second_level = tmp_path / "second_level/"
    third_level = tmp_path / "third_level/"
    local_in_first = first_level / ".treebuild/"
    local_in_third = third_level / ".treebuild/"
    second_level.mkdir(exist_ok=True)
    third_level.mkdir(exist_ok=True)
    local_in_first.mkdir(exist_ok=True)
    local_in_third.mkdir(exist_ok=True)

    # check searching from different levels retrieves the expected directories
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, first_level) == local_in_first
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, second_level) == local_in_first
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, third_level) == local_in_third


def test_resolve_if_local_dir_only_in_children(tmp_path: Path) -> None:
    """
    Search should always go upwards. Hence, starting to search from a parent to any of the .treebuild/
    directories should return a path to a (non-existing) parent/.treebuild
    """
    parent = tmp_path
    child = tmp_path / "child/"
    local_dir = child / ".treebuild/"
    child.mkdir(exist_ok=True)
    local_dir.mkdir(exist_ok=True)
    expected_dir = parent / LOCAL_TREEBUILD_DIR
    assert resolve_treebuild_dir(SettingsLevel.LOCAL, parent) == expected_dir
