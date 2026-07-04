from pathlib import Path
from typing import Generator

import pytest
from pydantic_core import PydanticUndefined
from typer.testing import CliRunner

from treebuild.cli.entrypoint import app
from treebuild.core.settings import (
    GLOBAL_SETTINGS_PATH,
    GLOBAL_TREEBUILD_DIR,
    STORE_FILE_NAME,
    TreeBuildSettings,
    load_settings,
    write_settings,
)


@pytest.fixture
def without_global_settings() -> Generator[None, None, None]:
    """
    ensure any already existing global file is temporally renamed, such that state is as if there is no existing global settings.yaml
    Using the pytest `yield instead of a return fixture` mechanism to safely perform cleanup.
    """

    # setup: rename the original file
    temp_displaced: Path | None = None
    if GLOBAL_SETTINGS_PATH.exists():
        temp_displaced = GLOBAL_SETTINGS_PATH.rename(
            GLOBAL_SETTINGS_PATH.with_name(f"{str(GLOBAL_SETTINGS_PATH.name)}_")
        )

    # hand-over control to the test
    yield

    # cleanup: rename back to original name
    if (temp_displaced is not None) and temp_displaced.exists():
        temp_displaced.rename(GLOBAL_SETTINGS_PATH)


@pytest.fixture
def without_global_dir() -> Generator[None, None, None]:
    """Temporally move ~/.config/treebuild to ~/.config/treebuild_ during tests. Afterwards set it back."""
    temp_displaced: Path | None = None
    if GLOBAL_TREEBUILD_DIR.exists():
        temp_displaced = GLOBAL_TREEBUILD_DIR.rename(
            GLOBAL_TREEBUILD_DIR.with_name(f"{str(GLOBAL_TREEBUILD_DIR.name)}_")
        )

    yield
    if (temp_displaced is not None) and temp_displaced.exists():
        temp_displaced.rename(GLOBAL_TREEBUILD_DIR)


@pytest.fixture
def with_global_settings(
    without_global_settings: Generator[None, None, None],
) -> Generator[None, None, None]:
    """
    Ensure there is a global settings file.
    """
    # setup: Create the settings file
    GLOBAL_SETTINGS_PATH.touch()
    yield
    # teardown: Remove file
    GLOBAL_SETTINGS_PATH.unlink(missing_ok=True)


@pytest.fixture
def with_global_dir(
    without_global_dir: Generator[None, None, None],
) -> Generator[None, None, None]:
    """Ensure there is a ~/config/.treebuild/"""
    GLOBAL_TREEBUILD_DIR.mkdir()
    yield
    if GLOBAL_TREEBUILD_DIR.exists():
        GLOBAL_TREEBUILD_DIR.rmdir()


@pytest.fixture
def with_local_settings(tmp_path: Path) -> tuple[Path, Path]:
    local_dir = tmp_path / ".treebuild/"
    local_file = local_dir / "settings.yaml"
    local_dir.mkdir()
    local_file.touch()
    return local_file, tmp_path


@pytest.fixture
def with_local_dir(tmp_path: Path) -> tuple[Path, Path]:
    """Only create the directory, not the settings file."""
    local_dir = tmp_path / ".treebuild/"
    local_dir.mkdir()
    return local_dir, tmp_path


@pytest.fixture
def with_default_global_settings(
    with_global_settings: Generator[None, None, None],
) -> dict[str, str]:
    """Set values for the global settings"""
    defaults = {
        key: str(value.default)
        for key, value in TreeBuildSettings.model_fields.items()
        if value.default is not PydanticUndefined
    }
    write_settings(defaults, GLOBAL_SETTINGS_PATH)
    return defaults


@pytest.fixture
def with_default_local_settings(
    with_local_settings: tuple[Path, Path],
) -> tuple[dict[str, str], Path, Path]:
    local_file, tmp_path = with_local_settings
    defaults = {
        key: str(value.default)
        for key, value in TreeBuildSettings.model_fields.items()
        if value.default is not PydanticUndefined
    }
    write_settings(defaults, local_file)
    return defaults, local_file, tmp_path


# ==== treebuild config show ====
def test_show_defaults_showing_settings(with_local_settings: tuple[Path, Path]) -> None:
    """Invoke treebuild config show"""
    _, tmp_path = with_local_settings
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show", "--local-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "==== ACTIVE SETTINGS ====" in result.stdout
    assert "==== LOCAL SETTINGS ====" in result.stdout
    assert "==== GLOBAL SETTINGS ====" in result.stdout


def test_show_handles_missing_files(with_local_dir: tuple[Path, Path]) -> None:
    """
    Call with default settings without creating a file. Should simply log the file is missing without traceback.

    NOTE: Since this test passes --> Can do without creating the file in the following tests!
    """
    local_dir, tmp_path = with_local_dir
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show", "--local-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert (
        f"Local settings file ({str(local_dir / 'settings.yaml')}) does not exist."
        in result.stdout
    )
    assert "==== ACTIVE SETTINGS ====" in result.stdout
    assert "==== LOCAL SETTINGS ====" in result.stdout
    assert "==== GLOBAL SETTINGS ====" in result.stdout


def test_show_active_settings_only() -> None:
    """Invoke treebuild config show --active/-a"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show", "--active"])
    assert result.exit_code == 0
    assert "==== ACTIVE SETTINGS ====" in result.stdout
    assert "==== LOCAL SETTINGS ====" not in result.stdout
    assert "==== GLOBAL SETTINGS ====" not in result.stdout


def test_show_local_settings_only() -> None:
    """Invoke treebuild config show --local/-l"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show", "--local"])
    assert result.exit_code == 0
    assert "==== ACTIVE SETTINGS ====" not in result.stdout
    assert "==== LOCAL SETTINGS ====" in result.stdout
    assert "==== GLOBAL SETTINGS ====" not in result.stdout


def test_show_global_settings_only() -> None:
    """Invoke treebuild config show --global/-g"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show", "--global"])
    assert result.exit_code == 0
    assert "==== ACTIVE SETTINGS ====" not in result.stdout
    assert "==== LOCAL SETTINGS ====" not in result.stdout
    assert "==== GLOBAL SETTINGS ====" in result.stdout


@pytest.mark.parametrize(
    "flags",
    [
        ("--active", "--local"),
        ("--active", "--global"),
        ("--local", "--global"),
        ("--active", "--local", "--global"),
    ],
)
def test_show_raises_if_multiple_flags(flags: tuple[str, ...]) -> None:
    """Use more than one flag --> should raise Exit code 1."""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "show"] + [f for f in flags])
    assert result.exit_code == 1
    assert "Error:" in result.stdout


# # ==== treebuild config create ====
def test_create_global(
    without_global_settings: Generator[None, None, None],
) -> None:
    """Invoke treebuild config create --level/-l global"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "create", "--level", "global"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert GLOBAL_SETTINGS_PATH.exists()

    global_settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert global_settings == {}


def test_create_local(with_local_dir: tuple[Path, Path]) -> None:
    """
    Invoke treebuild config create --level/-l local --local-dr <PATH>
    (create local dir manually beforehand)
    """
    local_dir, tmp_path = with_local_dir
    local_file = local_dir / "settings.yaml"
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "create", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.stdout != ""
    assert local_file.exists()

    local_settings = load_settings(local_file)
    assert local_settings["session_file"] == str(local_file.parent / STORE_FILE_NAME)


def test_create_local_incl_new_dir(tmp_path: Path) -> None:
    """
    Invoke treebuild config create --level/-l local --local-dir <PATH>
    (do NOT create local dir manually beforehand)
    """
    local_dir = tmp_path / ".treebuild/"
    local_file = local_dir / "settings.yaml"
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "create", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.stdout != ""
    assert local_dir.exists()
    assert local_file.exists()


def test_create_raises_if_file_exists_global(
    with_global_settings: Generator[None, None, None],
) -> None:
    """Cannot create a new file if ~/.config/treebuild/settings.yaml already exists."""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "create", "--level", "global"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_create_raises_if_file_exists_local(
    with_local_settings: tuple[Path, Path],
) -> None:
    """Cannot create new file if local .treebuild/settings.yaml already exists."""
    _, tmp_path = with_local_settings
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "create", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


# # === treebuild config delete ===
def test_delete_global_settings_file(
    with_global_settings: Generator[None, None, None],
) -> None:
    """Invoke treebuild config delete --level global"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "delete", "--level", "global"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert not GLOBAL_SETTINGS_PATH.exists()


def test_delete_local_settings_file(with_local_settings: Generator[Path, Path]) -> None:
    """Invoke treebuild config delete --level local"""
    local_file, tmp_path = with_local_settings
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.stdout != ""
    assert not local_file.exists()


def test_delete_dry_run_global(
    with_global_settings: Generator[None, None, None],
) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["config", "delete", "--level", "global", "--dry-run"])
    assert result.exit_code == 0
    assert str(GLOBAL_SETTINGS_PATH) in result.stdout
    assert GLOBAL_SETTINGS_PATH.exists()


def test_delete_dry_run_local(with_local_settings: tuple[Path, Path]) -> None:
    local_file, tmp_path = with_local_settings
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--level",
            "local",
            "--local-dir",
            str(tmp_path),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert str(local_file) in result.stdout
    assert local_file.exists()


def test_delete_raises_if_no_file_exists_global(
    without_global_settings: Generator[None, None, None],
) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["config", "delete", "--level", "global"])
    assert result.exit_code == 1
    assert (
        f"Global settings {str(GLOBAL_SETTINGS_PATH)} does not exist." in result.stdout
    )


def test_delete_raises_if_no_file_exists_local(
    with_local_dir: tuple[Path, Path],
) -> None:
    local_dir, tmp_path = with_local_dir
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert (
        f"Local settings {str(local_dir / 'settings.yaml')} does not exist."
        in result.stdout
    )


def test_delete_raises_if_no_dir_exists(tmp_path: Path) -> None:
    """Do not create the local treebuild directory"""
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert str(tmp_path / ".treebuild/") in result.stdout


# # ==== treebuild config set <KEY> <VALUE> ====
@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "path/to/a/tree.txt"),
        ("renderer", "plain"),
    ],
)
def test_set_global_setting(
    with_global_settings: Generator[None, None, None], key: str, value: str
) -> None:
    """Invoke treebuild config set key value --level global"""
    runner = CliRunner()
    result = runner.invoke(app, ["config", "set", key, value, "--level", "global"])
    assert result.exit_code == 0
    assert all(x in result.stdout for x in [key, value])

    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert settings[key] == value


@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "path/to/a/tree.txt"),
        ("renderer", "plain"),
    ],
)
def test_set_local_setting(
    with_local_settings: tuple[Path, Path], key: str, value: str
) -> None:
    """Invoke treebuild config set key value --level local"""
    local_file, tmp_dir = with_local_settings
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["config", "set", key, value, "--level", "local", "--local-dir", str(tmp_dir)],
    )
    assert result.exit_code == 0
    assert all(x in result.stdout for x in [key, value])

    settings = load_settings(local_file)
    assert settings[key] == value


@pytest.mark.parametrize(
    "key, first_value, second_value",
    [
        ("session_file", "path/to/first/tree.txt", "path/to/second/tree.txt"),
        (
            "renderer",
            "plain",
            "mock",
        ),  # NOTE: Second renderer does not exist, but does not matter for this particular test.
    ],
)
def test_set_overwrites_previous_value(
    with_global_settings: Generator[None, None, None],
    key: str,
    first_value: str,
    second_value: str,
) -> None:
    """Set the value for the same key twice."""
    runner = CliRunner()
    runner.invoke(app, ["config", "set", key, first_value, "--level", "global"])
    result = runner.invoke(
        app, ["config", "set", key, second_value, "--level", "global"]
    )
    assert result.exit_code == 0
    assert all(x in result.stdout for x in [key, second_value])
    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert settings[key] == second_value
    assert first_value not in settings.values()


def test_set_raises_if_no_global_settings_file(
    without_global_settings: Generator[None, None, None],
) -> None:
    """Attempt to set a value before having created a file."""
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "set", "session_file", "will/fail.txt", "--level", "global"]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_set_raises_if_no_local_settings_file(
    with_local_dir: tuple[Path, Path],
) -> None:
    _, tmp_dir = with_local_dir
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "session_file",
            "will/fail.txt",
            "--level",
            "local",
            "--local-dir",
            str(tmp_dir),
        ],
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_raises_if_invalid_key(tmp_path: Path) -> None:
    """Attempt to set some non-existing key"""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "non_existing",
            "value_does_not_matter",
            "--level",
            "global",
        ],
    )
    assert result.exit_code == 1
    assert result.stdout != ""


# # ==== treebuild config unset <KEY> ====
@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "path/to/a/tree.txt"),
        ("renderer", "plain"),
    ],
)
def test_unset_global_setting(
    with_global_settings: Generator[None, None, None], key: str, value: str
) -> None:
    """
    Invoke treebuild config unset key --level global
    set the value first, then unset it and assert it no longer is present in the file.
    """
    runner = CliRunner()
    runner.invoke(app, ["config", "set", key, value, "--level", "global"])
    result = runner.invoke(app, ["config", "unset", key, "--level", "global"])
    assert result.exit_code == 0
    assert key in result.stdout
    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert key not in settings


@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "path/to/a/tree.txt"),
        ("renderer", "plain"),
    ],
)
def test_unset_local_setting(
    with_local_settings: tuple[Path, Path], key: str, value: str
) -> None:
    """
    Invoke treebuild config unset key --level local --local-dir <PATH>
    set the value first, then unset it and assert it no longer is present in the file.
    """
    local_file, tmp_dir = with_local_settings
    runner = CliRunner()
    runner.invoke(
        app,
        ["config", "set", key, value, "--level", "local", "--local-dir", str(tmp_dir)],
    )
    result = runner.invoke(
        app, ["config", "unset", key, "--level", "local", "--local-dir", str(tmp_dir)]
    )
    assert result.exit_code == 0
    assert key in result.stdout
    settings = load_settings(local_file)
    assert key not in settings


def test_unset_keeps_other_values_intact(
    with_global_settings: Generator[None, None, None],
) -> None:
    """Set two values, only unset one."""
    runner = CliRunner()
    runner.invoke(
        app, ["config", "set", "session_file", "path/to/tree.txt", "--level", "global"]
    )
    runner.invoke(app, ["config", "set", "renderer", "plain", "--level", "global"])
    result = runner.invoke(app, ["config", "unset", "renderer", "--level", "global"])
    assert result.exit_code == 0
    assert result.stdout != ""
    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert "renderer" not in settings
    assert "session_file" in settings
    assert settings["session_file"] == "path/to/tree.txt"


def test_unset_raises_if_no_global_settings_file(
    without_global_settings: Generator[None, None, None],
) -> None:
    """Cannot unset a value if the file does not exist at all."""
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "unset", "file_does_not_exist", "--level", "global"]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_unset_raises_if_no_local_settings_file(
    with_local_dir: tuple[Path, Path],
) -> None:
    """Cannot unset a value if the file does not exist at all."""
    _, tmp_dir = with_local_dir
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "config",
            "unset",
            "file_does_not_exist",
            "--level",
            "local",
            "--local-dir",
            str(tmp_dir),
        ],
    )
    assert result.exit_code == 1
    assert result.stdout != ""
    print(result.stdout)


@pytest.mark.parametrize(
    "key",
    [
        ("session_file"),
        ("renderer"),
    ],
)
def test_unset_raises_if_no_value_set_previously(
    with_global_settings: Generator[None, None, None], key: str
) -> None:
    """
    Invoke treebuild config unset key --level global
    set the value first, then unset it and assert it no longer is present in the file.
    """
    runner = CliRunner()
    result = runner.invoke(app, ["config", "unset", key, "--level", "global"])
    assert result.exit_code == 1
    assert key in result.stdout
    print(result.stdout)


# # ==== treebuild config restore ====
@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "new/path.txt"),
        ("renderer", "different_renderer"),
    ],
)
def test_restore_all_global_settings(
    with_default_global_settings: dict[str, str], key: str, value: str
) -> None:
    runner = CliRunner()
    runner.invoke(app, ["config", "set", key, value, "--level", "global"])
    result = runner.invoke(app, ["config", "restore", "--all", "--level", "global"])
    assert result.exit_code == 0
    assert key in result.stdout
    defaults = with_default_global_settings
    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert settings[key] == defaults[key]


@pytest.mark.parametrize(
    "key, value",
    [
        ("session_file", "new/path.txt"),
        ("renderer", "different_renderer"),
    ],
)
def test_restore_all_local_settings(
    with_default_local_settings: tuple[dict[str, str], Path, Path], key: str, value: str
) -> None:
    defaults, local_file, tmp_dir = with_default_local_settings
    runner = CliRunner()
    runner.invoke(
        app,
        ["config", "set", key, value, "--level", "local", "--local-dir", str(tmp_dir)],
    )
    result = runner.invoke(
        app,
        ["config", "restore", "--all", "--level", "local", "--local-dir", str(tmp_dir)],
    )
    assert result.exit_code == 0
    assert key in result.stdout
    settings = load_settings(local_file)
    assert settings[key] == defaults[key]


@pytest.mark.parametrize(
    "key, value, other_key, other_value",
    [
        ("session_file", "new/path.txt", "renderer", "different_renderer"),
        ("renderer", "different_renderer", "session_file", "new/path.txt"),
    ],
)
def test_restore_specific_global_setting(
    with_default_global_settings: dict[str, str],
    key: str,
    value: str,
    other_key: str,
    other_value: str,
) -> None:
    runner = CliRunner()
    runner.invoke(app, ["config", "set", key, value, "--level", "global"])
    runner.invoke(app, ["config", "set", other_key, other_value, "--level", "global"])
    result = runner.invoke(
        app, ["config", "restore", "--key", key, "--level", "global"]
    )
    assert result.exit_code == 0
    assert key in result.stdout
    defaults = with_default_global_settings
    settings = load_settings(GLOBAL_SETTINGS_PATH)
    assert settings[key] == defaults[key]
    assert settings[other_key] != defaults[other_key]
    assert settings[other_key] == other_value


@pytest.mark.parametrize(
    "key, value, other_key, other_value",
    [
        ("session_file", "new/path.txt", "renderer", "different_renderer"),
        ("renderer", "different_renderer", "session_file", "new/path.txt"),
    ],
)
def test_restore_specific_local_setting(
    with_default_local_settings: tuple[dict[str, str], Path, Path],
    key: str,
    value: str,
    other_key: str,
    other_value: str,
) -> None:
    defaults, local_file, tmp_dir = with_default_local_settings
    runner = CliRunner()
    runner.invoke(
        app,
        ["config", "set", key, value, "--level", "local", "--local-dir", str(tmp_dir)],
    )
    runner.invoke(
        app,
        [
            "config",
            "set",
            other_key,
            other_value,
            "--level",
            "local",
            "--local-dir",
            str(tmp_dir),
        ],
    )
    result = runner.invoke(
        app,
        [
            "config",
            "restore",
            "--key",
            key,
            "--level",
            "local",
            "--local-dir",
            str(tmp_dir),
        ],
    )
    assert result.exit_code == 0
    assert key in result.stdout
    settings = load_settings(local_file)
    assert settings[key] == defaults[key]
    assert settings[other_key] != defaults[other_key]
    assert settings[other_key] == other_value


def test_restore_raises_if_no_flag(
    with_global_settings: Generator[None, None, None],
) -> None:
    """Router cannot decide if user does not specify to restore a specific setting or all settings to default(s)."""
    runner = CliRunner()
    runner.invoke(app, ["config", "set", "renderer", "plain", "--level", "global"])
    result = runner.invoke(app, ["config", "restore", "--level", "global"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_restore_raises_if_both_key_and_all_flags(tmp_path: Path) -> None:
    """Specifying a key and saying 'please restore all' is ambiguous. Raise and let user decide which one they want."""
    runner = CliRunner()
    runner.invoke(app, ["config", "set", "renderer", "plain", "--level", "global"])
    result = runner.invoke(
        app, ["config", "restore", "--key", "renderer", "--all", "--level", "global"]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_restore_raises_if_global_file_does_not_exist(
    without_global_settings: Generator[None, None, None],
) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "restore", "--key", "session_file", "--level", "global"]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_restore_raises_if_local_file_does_not_exist(
    with_local_dir: tuple[Path, Path],
) -> None:
    _, tmp_dir = with_local_dir
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["config", "restore", "--all", "--level", "local", "--local-dir", str(tmp_dir)],
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_restore_raises_if_no_default_value_for_key(
    with_global_settings: Generator[None, None, None],
) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "restore", "--key", "bla", "--level", "global"]
    )
    assert result.exit_code == 1
    assert "bla" in result.stdout


# # ==== treebuild config create-dir ====
def test_create_global_treebuild_dir(
    without_global_dir: Generator[None, None, None],
) -> None:
    """Invoke treebuild config create-dir --level global"""
    assert not GLOBAL_TREEBUILD_DIR.exists()
    runner = CliRunner()
    result = runner.invoke(app, ["config", "create-dir", "--level", "global"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert GLOBAL_TREEBUILD_DIR.exists()


def test_create_local_treebuild_dir(tmp_path: Path) -> None:
    local_dir = tmp_path / ".treebuild/"
    assert not local_dir.exists()
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "create-dir", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.stdout != ""
    assert local_dir.exists()


def test_create_dir_raises_if_already_exists_global(
    with_global_dir: Generator[None, None, None],
) -> None:
    assert GLOBAL_TREEBUILD_DIR.exists()
    runner = CliRunner()
    result = runner.invoke(app, ["config", "create-dir", "--level", "global"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_create_dir_raises_if_already_exists_local(
    with_local_dir: tuple[Path, Path],
) -> None:
    local_dir, tmp_path = with_local_dir
    assert local_dir.exists()
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "create-dir", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


# # ==== treebuild config delete-dir ====
def test_delete_global_treebuild_dir(
    with_global_dir: Generator[None, None, None],
) -> None:
    """Invoke treebuild config delete-dir --level global"""
    assert GLOBAL_TREEBUILD_DIR.exists()
    runner = CliRunner()
    result = runner.invoke(app, ["config", "delete-dir", "--level", "global"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert not GLOBAL_TREEBUILD_DIR.exists()


def test_delete_local_treebuild_dir(with_local_dir: tuple[Path, Path]) -> None:
    local_dir, tmp_path = with_local_dir
    assert local_dir.exists()
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete-dir", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.stdout != ""
    assert not local_dir.exists()


def test_delete_dir_raises_if_does_not_exist_global(
    without_global_dir: Generator[None, None, None],
) -> None:
    assert not GLOBAL_TREEBUILD_DIR.exists()
    runner = CliRunner()
    result = runner.invoke(app, ["config", "delete-dir", "--level", "global"])
    assert result.exit_code == 1
    assert result.stdout != ""


def test_delete_dir_raises_if_does_not_exist_local(tmp_path: Path) -> None:
    local_dir = tmp_path / ".treebuild/"
    assert not local_dir.exists()
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete-dir", "--level", "local", "--local-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert result.stdout != ""


def test_delete_dir_dry_run_global(
    with_global_dir: Generator[None, None, None],
) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app, ["config", "delete-dir", "--level", "global", "--dry-run"]
    )
    assert result.exit_code == 0
    assert str(GLOBAL_TREEBUILD_DIR) in result.stdout
    assert GLOBAL_TREEBUILD_DIR.exists()


def test_delete_dir_dry_run_local(with_local_dir: tuple[Path, Path]) -> None:
    local_dir, tmp_path = with_local_dir
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "config",
            "delete-dir",
            "--level",
            "local",
            "--local-dir",
            str(tmp_path),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert str(local_dir) in result.stdout
    assert local_dir.exists()
