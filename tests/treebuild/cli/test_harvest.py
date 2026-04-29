"""Integration tests for src/treebuild/cli/harvest.py"""

from pathlib import Path

from typer.testing import CliRunner

from treebuild.cli.entrypoint import app
from treebuild.cli.helpers import load_message
from treebuild.rendering.plain_text_renderer import PlainTextRenderer
from treebuild.tree.builder import TreeBuilder


## --- treebuild harvest text---
def test_harvest_plain_text_renderer(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """Render to plain text."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", "some.file", "a/folder/with/some/file.inside"])
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(app, ["harvest", "text", "--renderer", "plain"])
    assert result.exit_code == 0
    assert result.stdout != ""

    # Manually create rendering and check if contents is send to stdout
    paths = [Path(p) for p in ["some.file", "a/folder/with/some/file.inside"]]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    renderer = PlainTextRenderer()
    rendering = renderer.render_tree(tree)
    assert rendering in result.stdout


def test_harvest_render_and_write_to_file(
    active_session: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    """write contents to a file."""

    tmp_file = tmp_path / "rendering.md"
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", "some.file", "a/folder/with/some/file.inside"])
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(
        app, ["harvest", "text", "--renderer", "plain", "--output", str(tmp_file)]
    )
    assert result.exit_code == 0
    assert str(tmp_file) in result.stdout

    # Manually create rendering and check if contents is written to file.
    paths = [Path(p) for p in ["some.file", "a/folder/with/some/file.inside"]]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    renderer = PlainTextRenderer()
    rendering = renderer.render_tree(tree)
    assert rendering == tmp_file.read_text()


def test_harvest_exits_if_tree_is_empty(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """No leaves/branches or a root? Nothing to render."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["harvest", "text", "--renderer", "plain"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_harvest_show_root_ignored_if_no_root_name(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """The --show-root flag should only have an affect if a root name is set for the given tree."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", "some.file", "a/folder/with/some/file.inside"])

    result = runner.invoke(
        app, ["harvest", "text", "--renderer", "plain", "--show-root"]
    )
    output_with_flag = result.stdout

    result = runner.invoke(app, ["harvest", "text", "--renderer", "plain"])
    output_no_flag = result.stdout

    # check additional message is shown:
    expected_msg = load_message("harvest_show_root_no_name.md").strip()
    assert expected_msg in output_with_flag

    # check only the 'tree' part
    assert output_no_flag.strip() == output_with_flag.replace(expected_msg, "").strip()


def test_harvest_needs_active_session(
    empty_session: tuple[Path, dict[str, str]],
) -> None:
    """Cannot harvest without starting a tree."""
    _, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["harvest", "text", "--renderer", "plain"])
    assert result.exit_code == 1
    assert result.stdout != ""
