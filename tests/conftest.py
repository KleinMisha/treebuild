"""Shared fixtures and mocks"""

import pytest

from treebuild.tree.branches import Branch, Tree


@pytest.fixture()
def tree() -> Tree:
    """Empty tree with just a root directory"""
    return Tree(Branch("root"))
