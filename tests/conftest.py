"""Shared fixtures and mocks"""

from itertools import zip_longest
from pathlib import Path

import pytest

from treebuild.tree.branches import Branch, Tree
from treebuild.core.settings import ENV_PREFIX


@pytest.fixture()
def tree() -> Tree:
    """Empty tree with just a root directory"""
    return Tree(Branch("root"))


@pytest.fixture()
def session_file(tmp_path: Path) -> Path:
    """Temporary file for session's state. For unit tests of SessionStore"""
    file = tmp_path / "session.txt"
    file.touch()
    return file


@pytest.fixture()
def empty_session(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """
    A session using a temporary file (not yet created), for tests of CLI commands.
    """
    session_file = tmp_path / "session.txt"
    env = {f"{ENV_PREFIX}SESSION_FILE": str(session_file)}
    return session_file, env


@pytest.fixture()
def active_session(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """
    A session with session-file created.
    For (unit) tests of CLI commands requiring a file to exist.
    """
    session_file = tmp_path / "session.txt"
    session_file.touch()
    env = {f"{ENV_PREFIX}SESSION_FILE": str(session_file)}
    return session_file, env


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
