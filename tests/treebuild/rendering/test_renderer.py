"""Unit tests for src/treebuild/rendering/renderer.py"""

from unittest.mock import Mock

import pytest

from treebuild.rendering.renderer import Branch, Connector, Renderer, Tree


class MockRenderer(Renderer):
    """Simplified version for easy testing of shared logic in the ABC."""

    @property
    def _connectors(self) -> dict[Connector, str]:
        return {
            Connector.EMPTY: "E",
            Connector.MIDDLE_CHILD: "M",
            Connector.FINAL_CHILD: "F",
            Connector.CONTINUATION: "C",
        }

    def _format_line(self, name: str, ancestor_is_last: list[bool]) -> str:
        prefix = (
            self._connectors[Connector.FINAL_CHILD]
            if ancestor_is_last[-1]
            else self._connectors[Connector.MIDDLE_CHILD]
        )
        return f"LINE:{prefix}\t{name}"


@pytest.fixture()
def renderer() -> MockRenderer:
    return MockRenderer()


@pytest.fixture()
def tree() -> Tree:
    return Tree(Branch("root"))


def test_render_tree_returns_string(tree: Tree, renderer: MockRenderer) -> None:
    """Output should be a single string (no longer a list of strings)"""
    output = renderer.render_tree(tree)
    assert isinstance(output, str)


def test_render_only_root(tree: Tree, renderer: MockRenderer) -> None:
    """A tree with just a root"""
    output = renderer.render_tree(tree, include_root=True)
    assert output == tree.root.name


def test_render_do_not_show_root(tree: Tree, renderer: MockRenderer) -> None:
    """A tree with just a root, do not show root's name"""
    output = renderer.render_tree(tree, include_root=False)
    assert output == "."


def test_render_tree_joins_by_new_line(tree: Tree, renderer: MockRenderer) -> None:
    """A tree with only files directly under the root"""
    num_files = 5
    files = [f"file_{n + 1}.bla" for n in range(num_files)]
    for file in files:
        tree.add_leaf(file)
    output = renderer.render_tree(tree)
    assert len(str(output).splitlines()) == num_files + 1


@pytest.mark.parametrize("N, M", [(n, m) for n in range(6) for m in range(6)])
def test_render_tree_calls_format_line_for_every_leaf_or_branch(
    tree: Tree, renderer: MockRenderer, N: int, M: int
) -> None:
    """Check recursion happens correctly
    directory: ./file{1...N} and ./dir/subdir_file{1...M},
    should have a total of (N + M + 1) calls to the formatting method.
    (number of files + number of directories below the root to be printed)
    """
    # build tree
    files_in_root = [f"file_{n + 1}.x" for n in range(N)]
    files_in_dir = [f"file_{m + 1}.y" for m in range(M)]

    for file in files_in_root:
        tree.add_leaf(file)

    directory = Branch("directory")
    for file in files_in_dir:
        directory.add_leaf(file)
    tree.add_branch(directory)

    # mock the format-line calls
    renderer._format_line = Mock(return_value="")  # pyright: ignore[reportPrivateUsage]
    renderer.render_tree(tree)
    assert renderer._format_line.call_count == (N + M + 1)  # pyright: ignore[reportPrivateUsage]
