"""Unit tests for src/treebuild/core/helpers.py"""

from pathlib import Path

import pytest

from treebuild.core.helpers import read_paths_from_file

MOCK_PATHS = [
    "zeroth.md",
    "first/first/mock.txt",
    "second/second/mock.md",
    "third/",
    "first/first/fourth/mock.py",
]


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    """Create a temporary file"""
    file = tmp_path / "my_paths.txt"
    file.touch()
    return file


def test_read_paths_from_file(tmp_file: Path) -> None:
    """basic file with only paths in it. Check method returns all the paths as expected."""

    with tmp_file.open("w") as f:
        f.writelines("\n".join(MOCK_PATHS))

    paths = read_paths_from_file(tmp_file)
    assert set(paths) == set(MOCK_PATHS)


def test_ignore_empty_lines(tmp_file: Path) -> None:
    """Empty lines should get ignored when constructing the list of paths."""
    incl_empty_line = [
        "zeroth.md",
        "first/first/mock.txt",
        "",  # empty line inserted
        "second/second/mock.md",
        "third/",
        "first/first/fourth/mock.py",
    ]

    with tmp_file.open("w") as f:
        f.writelines("\n".join(incl_empty_line))

    paths = read_paths_from_file(tmp_file)
    assert set(paths) == set(MOCK_PATHS)


def test_ignore_comment_line(tmp_file: Path) -> None:
    """Lines starting with a comment should get ignored when constructing the list of paths."""
    incl_comment = [
        "# ROOT: project-root",  # metadata also starts with pound sign
        "zeroth.md",
        "first/first/mock.txt",
        "# a very useful comment",  # comment
        "second/second/mock.md",
        "third/",
        "first/first/fourth/mock.py",
    ]
    with tmp_file.open("w") as f:
        f.writelines("\n".join(incl_comment))

    paths = read_paths_from_file(tmp_file)
    print(paths)
    assert set(paths) == set(MOCK_PATHS)


def test_whitespaces_get_stripped(tmp_file: Path) -> None:
    """Leading/Trailing whitespaces should get removed to get the proper (candidate) path."""
    incl_whitespaces = [
        " zeroth.md ",  # leading and trailing space
        " first/first/mock.txt",  # only leading
        "second/second/mock.md",
        "third/",
        "first/first/fourth/mock.py ",  # only trailing
    ]
    with tmp_file.open("w") as f:
        f.writelines("\n".join(incl_whitespaces))

    paths = read_paths_from_file(tmp_file)
    assert set(paths) == set(MOCK_PATHS)
