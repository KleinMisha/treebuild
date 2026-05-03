"""Integration tests for src/treebuild/cli/harvest.py"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from treebuild.cli.entrypoint import app
from treebuild.cli.helpers import load_message
from treebuild.harvest.plain_text_renderer import PlainTextRenderer
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


def test_harvest_text_exits_if_tree_is_empty(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """No leaves/branches or a root? Nothing to render."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["harvest", "text", "--renderer", "plain"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_harvest_text_show_root_ignored_if_no_root_name(
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


# --- treebuild harvest scaffold ---
def test_scaffold_defaults(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Calling `treebuild harvest scaffold` without any additional options/flags."""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(app, ["harvest", "scaffold", "--location", str(tmp_path)])
    assert result.exit_code == 0
    assert result.stdout != ""

    # manually build tree and check behavior
    paths = [Path(p) for p in path_strs]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    assert all((tmp_path / path).exists() for path in tree.paths)


@pytest.mark.xfail(
    reason="Trailing slashes not yet interpreted as indicating the path is a directory. See issue #1"
)
def test_scaffold_w_gitkeep(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Calling `treebuild harvest scaffold --gitkeep`"""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(
        app, ["harvest", "scaffold", "--location", str(tmp_path), "--gitkeep"]
    )
    assert result.exit_code == 0
    assert result.stdout != ""

    # manually build tree and check behavior
    paths = [Path(p) for p in path_strs]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    assert all((tmp_path / path).exists() for path in tree.paths)
    assert (tmp_path / "second-folder" / ".gitkeep").exists()


def test_scaffold_exists_if_no_root(
    active_session: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    """Cannot materialize anything, if root directory name is not set."""
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    result = runner.invoke(app, ["harvest", "scaffold", "--location", str(tmp_path)])
    assert result.exit_code == 1

    expected_msg = load_message("harvest_scaffold_no_root_set.md")
    assert expected_msg in result.stdout


def test_scaffold_dry_run(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Calling `treebuild harvest scaffold --dry-run"""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(
        app, ["harvest", "scaffold", "--location", str(tmp_path), "--dry-run"]
    )
    assert result.exit_code == 0

    # manually build tree and check behavior
    paths = [Path(p) for p in path_strs]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    assert not (tmp_path / tree.root.name).exists()
    assert all(str(tmp_path / path) in result.stdout for path in tree.paths)


# --- treebuild harvest teardown ---
def test_teardown_defaults(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Call `treebuild harvest teardown` (perform roundtrip by creating directories first)"""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    runner.invoke(app, ["harvest", "scaffold", "--location", str(tmp_path)])
    result = runner.invoke(app, ["harvest", "teardown", "--location", str(tmp_path)])
    assert result.exit_code == 0
    assert result.stdout != ""

    # manually build tree and check behavior
    paths = [Path(p) for p in path_strs]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    assert not any((tmp_path / path).exists() for path in tree.paths)


def test_teardown_dry_run(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Call `treebuild harvest teardown --dry-run"""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    runner.invoke(app, ["harvest", "scaffold", "--location", str(tmp_path)])
    result = runner.invoke(
        app, ["harvest", "teardown", "--location", str(tmp_path), "--dry-run"]
    )
    assert result.exit_code == 0

    # manually build tree and check behavior
    paths = [Path(p) for p in path_strs]
    builder = TreeBuilder("project-name", paths)
    tree = builder.assemble_tree()
    assert (tmp_path / tree.root.name).exists()
    assert all(str(tmp_path / path) in result.stdout for path in tree.paths)


def test_teardown_exists_if_no_root(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Cannot dematerialize anything if root name unknown."""
    # invoke CLI
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    runner.invoke(app, ["harvest", "scaffold", "--location", str(tmp_path)])
    runner.invoke(app, ["uproot"])
    result = runner.invoke(app, ["harvest", "teardown", "--location", str(tmp_path)])
    assert result.exit_code == 1
    expected_msg = load_message("harvest_teardown_no_root_set.md")
    assert expected_msg in result.stdout


def test_teardown_exists_if_root_does_not_exist(
    active_session: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Cannot dematerialize / remove anything if root directory is not found."""
    path_strs = ["some.file", "first-folder/file", "second-folder/"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + path_strs)
    runner.invoke(app, ["seed", "project-name"])
    result = runner.invoke(app, ["harvest", "teardown", "--location", str(tmp_path)])
    assert result.exit_code == 1
    expected_msg = load_message("harvest_teardown_root_dir_does_not_exist.md")
    assert expected_msg in result.stdout


# --- ensure there is an active session (for else there is no tree to do anything with) ---
@pytest.mark.parametrize(
    "command,arguments",
    [
        ("text", ["--renderer", "plain"]),
        ("scaffold", []),
        ("teardown", []),
    ],
)
def test_harvest_group_needs_active_session(
    empty_session: tuple[Path, dict[str, str]], command: str, arguments: list[str]
) -> None:
    """Cannot harvest without starting a tree."""
    _, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["harvest"] + [command] + arguments)
    assert result.exit_code == 1
    assert result.stdout != ""
