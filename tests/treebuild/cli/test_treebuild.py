"""Integration tests for commands directly under the tool name (treebuild ...): src/treebuild/cli/treebuild.py"""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from treebuild.cli.entrypoint import app
from treebuild.cli.helpers import load_message
from treebuild.cli.walkthrough import CORRECT_DEMO_INPUTS
from treebuild.storage.session import SessionStore, normalize


def static_part(message: str) -> str:
    """Get the part of the message before the first {placeholder}"""
    return message.split("{")[0].strip()


DEMO_NO_QUICKSTART = CORRECT_DEMO_INPUTS + ["n"]
DEMO_YES_QUICKSTART = CORRECT_DEMO_INPUTS + ["y"]


# --- treebuild hello: health check ---
def test_hello() -> None:
    """Display simple message to screen."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello"])

    # make sure at least something has been printed to screen
    assert result.exit_code == 0
    assert result.stdout != ""


# --- treebuild demo ---
def test_demo_run_until_completion(empty_session: tuple[Path, dict[str, str]]) -> None:
    """Go through the full demo, make sure your state (the session file etc.) no longer exist afterwards."""
    file, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["demo"], input="\n".join(DEMO_NO_QUICKSTART))
    assert result.exit_code == 0
    assert not file.exists()
    assert not Path("./demo-project/").exists()


def test_demo_enters_quickstart(empty_session: tuple[Path, dict[str, str]]) -> None:
    """Test entering the quickstart implementation if user chooses to do such."""
    with patch("treebuild.cli.walkthrough.quickstart_impl") as mock_quickstart:
        file, environment = empty_session
        runner = CliRunner(env=environment)
        result = runner.invoke(app, ["demo"], input="\n".join(DEMO_YES_QUICKSTART))
        assert result.exit_code == 0
        mock_quickstart.assert_called_once()
        assert not file.exists()
        assert not Path("demo-project/").exists()


@pytest.mark.parametrize(
    "steps_completed", [n for n in range(1, len(DEMO_NO_QUICKSTART) + 1)]
)
def test_demo_keyboard_interrupt_triggers_cleanup(
    empty_session: tuple[Path, dict[str, str]], steps_completed: int
) -> None:
    """Interrupt the demo midway --> ensure cleanup still happens properly."""

    partial_inputs = DEMO_NO_QUICKSTART[:steps_completed]
    file, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["demo"], input="\n".join(partial_inputs + ["\x03"]))
    assert result.exit_code == 0
    assert not file.exists()
    assert not Path("demo-project/").exists()


# --- treebuild quickstart ---


# --- treebuild status ---
def test_status_before_tree_planted(empty_session: tuple[Path, dict[str, str]]) -> None:
    """no session store created."""
    _, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["status"])
    expected_message = load_message("status_no_tree.md")
    assert result.exit_code == 0
    assert static_part(expected_message) in result.stdout


def test_status_empty_tree(active_session: tuple[Path, dict[str, str]]) -> None:
    """session store created, but no root or node set."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["status"])
    expected_message = load_message("status_empty_tree.md")
    assert result.exit_code == 0
    assert static_part(expected_message) in result.stdout


def test_status_only_root(active_session: tuple[Path, dict[str, str]]) -> None:
    """A tree with only a root name set."""
    root_name = "my-project"
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["seed", root_name])
    result = runner.invoke(app, ["status"])
    msg1 = load_message("status_show_root.md")
    msg2 = load_message("status_no_nodes.md")
    assert result.exit_code == 0
    assert static_part(msg1) in result.stdout
    assert static_part(msg2) in result.stdout
    assert root_name in result.stdout


def test_status_no_nodes(active_session: tuple[Path, dict[str, str]]) -> None:
    """A tree with leaves/branches, but without a root name set."""
    leaves_and_branches = ["a.leaf", "branch/another.leaf"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + leaves_and_branches)
    result = runner.invoke(app, ["status"])
    msg1 = load_message("status_no_root.md")
    msg2 = load_message("status_show_nodes.md")
    assert result.exit_code == 0
    assert static_part(msg1) in result.stdout
    assert static_part(msg2) in result.stdout
    assert all(normalize(l_or_b) in result.stdout for l_or_b in leaves_and_branches)


def test_status_both_nodes_and_root(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """A tree with it's root name set & containing leaves/ branches."""
    root = "project-root"
    leaves_and_branches = ["a.leaf", "branch/another.leaf"]
    _, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["seed", root])
    runner.invoke(app, ["grow"] + leaves_and_branches)
    result = runner.invoke(app, ["status"])
    msg1 = load_message("status_show_root.md")
    msg2 = load_message("status_show_nodes.md")
    assert result.exit_code == 0
    assert static_part(msg1) in result.stdout
    assert static_part(msg2) in result.stdout
    assert root in result.stdout
    assert all(normalize(l_or_b) in result.stdout for l_or_b in leaves_and_branches)


# --- treebuild plant ---
def test_plant_creates_new_session_file(
    empty_session: tuple[Path, dict[str, str]],
) -> None:
    """Call it when session (file) does not exist yet."""
    file, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["plant"])
    assert result.exit_code == 0
    assert file.exists()
    assert str(file) in result.stdout


def test_plant_set_root(empty_session: tuple[Path, dict[str, str]]) -> None:
    """Call plan with the `--root` flag"""
    root_name = "my-root-dir"
    file, environment = empty_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["plant", "--root", root_name])
    assert result.exit_code == 0

    session = SessionStore(file)
    assert session.read_root() == root_name
    assert result.stdout != ""


def test_plant_fails_if_root_already_set(
    empty_session: tuple[Path, dict[str, str]],
) -> None:
    """Cannot plant tree if session already contains data (here: a root name)"""
    root_name = "my-root-dir"
    file, environment = empty_session
    # already add the root
    session = SessionStore(file)
    session.write_root(root_name)

    # An invocation of treebuild plant should fail
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["plant"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_plant_fails_if_nodes_already_added(
    empty_session: tuple[Path, dict[str, str]],
) -> None:
    """Cannot plant tree if session already contains data (here: a leaf is added)"""
    leaf_name = "some.file"
    file, environment = empty_session
    # already add the file
    session = SessionStore(file)
    session.write_path(leaf_name)

    # An invocation of treebuild plant should fail
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["plant"])
    assert result.exit_code == 1
    assert result.stdout != ""


# --- treebuild grow ---
@pytest.mark.parametrize(
    "path_name", ["some.file", "some_directory/", "a_file/within_a.dir"]
)
def test_grow_single_path(
    active_session: tuple[Path, dict[str, str]], path_name: str
) -> None:
    """Writing a single bath (leaf or branch) to your current session."""
    file, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["grow", path_name])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert set(session.read_paths()) == set([normalize(path_name)])


def test_grow_multiple_paths(active_session: tuple[Path, dict[str, str]]) -> None:
    """Writing multiple leaves and branches at the same time."""
    paths_to_add = ["some.file", "some_directory/", "a_file/within_a.dir"]
    file, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["grow"] + paths_to_add)
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert set(session.read_paths()) == set([normalize(p) for p in paths_to_add])


def test_grow_skips_duplicates(active_session: tuple[Path, dict[str, str]]) -> None:
    """Duplicate paths (within normalization) should be skipped when writing to file."""
    unique = ["some_directory/some_file.inside", "some.file"]
    duplicates = [
        "some_directory/some_file.inside",
        "some_directory/some_file.inside",
        "./some_directory/some_file.inside",
        "some.file",
        "./some.file",
        "some.file ",
    ]
    file, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["grow"] + duplicates)
    assert result.exit_code == 0
    # check that regardless of skipping it, the user gets updated something happened with their entry
    assert all(name in result.stdout for name in duplicates)

    session = SessionStore(file)
    assert set(session.read_paths()) == set([normalize(p) for p in unique])
    assert all(session.read_paths().count(normalize(name)) == 1 for name in unique)


# --- treebuild prune ---
def test_prune_after_grow(active_session: tuple[Path, dict[str, str]]) -> None:
    """Successfully remove (prune) a path (leaf/branch) from your session (tree)."""
    path = "some.file"
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", path])
    result = runner.invoke(app, ["prune", path])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert session.read_paths() == []


@pytest.mark.parametrize(
    "path_to_remove", ["some.file", "another.file", "yet_another/file"]
)
def test_prune_specific_path(
    active_session: tuple[Path, dict[str, str]], path_to_remove: str
) -> None:
    """Remove just a specific path"""
    paths_added = ["some.file", "another.file", "yet_another/file"]
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + [normalize(p) for p in paths_added])
    result = runner.invoke(app, ["prune", path_to_remove])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert len(session.read_paths()) == len(paths_added) - 1
    assert normalize(path_to_remove) not in session.read_paths()


def test_prune_all(active_session: tuple[Path, dict[str, str]]) -> None:
    """Remove all paths in one go"""
    paths_added = ["some.file", "another.file", "yet_another/file"]
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + paths_added)
    result = runner.invoke(app, ["prune", "--all"])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert session.read_paths() == []


def test_cannot_prune_before_grow(active_session: tuple[Path, dict[str, str]]) -> None:
    """Exit when no paths to be removed in the file."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["prune", "a_file_not_yet.added"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_prune_multiple(active_session: tuple[Path, dict[str, str]]) -> None:
    """Manually remove multiple paths"""
    paths_added = ["some.file", "another.file", "yet_another/file"]
    paths_to_remove = paths_added.copy()[1:]
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + paths_added)
    result = runner.invoke(app, ["prune"] + paths_to_remove)
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert set(session.read_paths()) == set([normalize(paths_added[0])])


def test_prune_skips_not_found_paths(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """Simply skip a path not added prior."""
    paths_added = ["some.file", "another.file", "yet_another/file"]
    path_not_added = ["not/yet/added/as/branch/with.leaf"]
    paths_to_remove = [paths_added[0]] + path_not_added
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow"] + paths_added)
    result = runner.invoke(app, ["prune"] + paths_to_remove)
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert set(session.read_paths()) == set([normalize(p) for p in paths_added[1:]])


def test_prune_needs_path_or_all_flag(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """Cannot prune without specifying a path (when '--all' flag is not provided. )"""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["prune"])
    assert result.exit_code == 1
    assert result.stdout != ""


# --- treebuild seed ---
def test_seed(active_session: tuple[Path, dict[str, str]]) -> None:
    """Use seed command to set the root of existing tree."""
    root_name = "my-project-root"
    file, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, ["seed", root_name])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert session.read_root() == root_name


def test_exit_if_root_already_set(active_session: tuple[Path, dict[str, str]]) -> None:
    """If '--force' flag not provided, the seed command will exit and inform the user in stead of silently overwriting."""
    before = "first-name"
    after = "new-name"
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["seed", before])
    result = runner.invoke(app, ["seed", after])
    assert result.exit_code == 1
    assert result.stdout != ""

    session = SessionStore(file)
    assert session.read_root() == before


def test_force_rename_root(active_session: tuple[Path, dict[str, str]]) -> None:
    """Adding the '--force' flag will silently overwrite the already existing root."""
    before = "first-name"
    after = "new-name"
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["seed", before])
    result = runner.invoke(app, ["seed", "-f", after])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert session.read_root() == after


# --- treebuild uproot ---
def test_uproot(active_session: tuple[Path, dict[str, str]]) -> None:
    """Use uproot to unset a previously set root."""
    root_name = "my-project-root"
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["seed", root_name])
    result = runner.invoke(app, ["uproot"])
    assert result.exit_code == 0
    assert result.stdout != ""

    session = SessionStore(file)
    assert not session.has_root()


def test_cannot_uproot_if_not_seeded(
    active_session: tuple[Path, dict[str, str]],
) -> None:
    """Must first set a root, for else cannot unset it."""
    _, environment = active_session
    runner = CliRunner(env=environment)
    result = runner.invoke(app, "uproot")
    assert result.exit_code == 1
    assert result.stdout != ""


# --- treebuild replant ---
def test_replant(active_session: tuple[Path, dict[str, str]]) -> None:
    """Clear all contents of file, but keeps the file."""
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", "path1", "path2"])
    runner.invoke(app, ["seed", "root-name"])
    result = runner.invoke(app, ["replant"])
    assert result.exit_code == 0
    assert result.stdout != ""

    assert file.exists()
    session = SessionStore(file)
    assert not session.has_paths()
    assert not session.has_root()


# --- treebuild chop ---
def test_chop(active_session: tuple[Path, dict[str, str]]) -> None:
    """Delete the file with stored paths / root's entirely."""
    file, environment = active_session
    runner = CliRunner(env=environment)
    runner.invoke(app, ["grow", "path1", "path2"])
    runner.invoke(app, ["seed", "root-name"])
    result = runner.invoke(app, ["chop"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert not file.exists()


# --- ERROR PATH: Commands that require an existing file to write into ---
@pytest.mark.parametrize(
    "command, arguments",
    [
        ("grow", ["path1", "path2"]),
        ("prune", ["path1", "path2"]),
        ("seed", ["root-name"]),
        ("uproot", None),
        ("replant", None),
        ("chop", None),
    ],
)
def test_active_session_required(
    empty_session: tuple[Path, dict[str, str]],
    command: str,
    arguments: list[str] | None,
) -> None:
    """Make sure `ensure_active_session()` is called when invoking any of the tested commands."""
    _, environment = empty_session
    runner = CliRunner(env=environment)
    args = arguments if arguments else []
    result = runner.invoke(app, [command] + args)
    assert result.exit_code == 1
    assert result.stdout != ""
