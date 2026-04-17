"""Shared fixtures and mocks"""

from itertools import zip_longest
from pathlib import Path

import pytest

from treebuild.tree.branches import Branch, Tree


@pytest.fixture()
def tree() -> Tree:
    """Empty tree with just a root directory"""
    return Tree(Branch("root"))


@pytest.fixture()
def session_file(tmp_path: Path) -> Path:
    """Temporary file for session's state."""
    file = tmp_path / "session.txt"
    file.touch()
    return file


def assert_strings_equal(actual: str, expected: str) -> None:
    """
    Test that formatted trees equal on a character-by-character basis.
    If not, produce custom error message that makes debugging easier.
    """
    for idx, (a, b) in enumerate(zip_longest(actual, expected)):
        if a != b:
            raise AssertionError(
                f"Character {idx} differs: {repr(a)} != {repr(b)}\n"
                + f"actual:   {repr(actual)}\n"
                + f"expected: {repr(expected)}"
            )
