"""Implementation of secondary commands, which will be called as 'treebuild config <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from shutil import rmtree
from typing import Any

from pydantic_core import PydanticUndefined

from treebuild.core.exceptions import ConfigError
from treebuild.storage.settings import (
    SettingsLevel,
    TreeBuildSettings,
    get_settings,
    load_settings,
    resolve_settings_file,
    resolve_tree_file,
    resolve_treebuild_dir,
    write_settings,
)


def show_impl(
    location: Path,
    incl_active: bool = True,
    incl_local: bool = True,
    incl_global: bool = True,
) -> None:
    """log / print to screen to inform the user."""
    #  ? Use combination of template markdown string & rich builtin prettyprint to display the values nicely?
    # TODO use rich Console print
    if incl_active:
        resolved_settings = get_settings().model_dump()
        print("==== ACTIVE SETTINGS ====")
        print(resolved_settings)
        print("\n")
    if incl_local:
        _display_settings_by_level(SettingsLevel.LOCAL, location)
    if incl_global:
        _display_settings_by_level(SettingsLevel.GLOBAL, location)


def _display_settings_by_level(level: SettingsLevel, location: Path) -> None:
    """Helper to nicely format printing in `show` command"""
    file = resolve_settings_file(level, location)
    if not file.exists():
        logging.warning(
            f"{level.name.capitalize()} settings file ({str(file)}) does not exist. Cannot display"
        )
    settings = load_settings(file) if file.exists() else {}
    print(f"==== {level.name.upper()} SETTINGS ====")
    print(settings)
    print("\n")


def create_impl(level: SettingsLevel, location: Path) -> None:
    """
    Create the .treebuild/settings.yaml
    ---

    Sets the value for the tree file's location (.treebuild/settings.yaml)
    Other values will equal the global settings.

    ---
    Use `treebuild config show` to view all available configurable options.
    """
    # guard clause comes first:

    settings_file = resolve_settings_file(level, location)
    if settings_file.exists():
        raise ConfigError(
            f"A {level.name.lower()} settings file already exists: {str(settings_file)}"
        )

    # happy path: Check if directory needs to be created first.
    if not settings_file.parent.exists():
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created ./treebuild directory: {str(settings_file.parent)}")

    # create new file
    new_values = (
        {"tree_file": str(resolve_tree_file(level, location))}
        if level == SettingsLevel.LOCAL
        else {}
    )
    write_settings(new_values, settings_file)
    logging.info(f"Created new file: {settings_file}")


def delete_settings_impl(
    level: SettingsLevel, location: Path, dry_run: bool = False
) -> None:
    """Delete the settings.yaml"""

    directory = resolve_treebuild_dir(level, location)
    if not directory.exists():
        raise ConfigError(f"{directory} does not exist.")
    file = resolve_settings_file(level, location)
    if not file.exists():
        raise ConfigError(f"{level.name.capitalize()} settings {file} does not exist.")

    if dry_run:
        logging.info(f"[DRY-RUN] Would remove: {str(file)}")
        return

    file.unlink()
    logging.info(f"Removed: {str(file)}")


def set_impl(key: str, value: Any, level: SettingsLevel, location: Path) -> None:
    """Sets (updates if already set previously) local/global value for the given key"""

    if key not in TreeBuildSettings.model_fields:
        raise ConfigError(f"No valid setting named {key}")

    settings_file = resolve_settings_file(level, location)
    if not settings_file.exists():
        raise ConfigError(
            f"{level.name.capitalize()} settings file ({str(settings_file)}) does not exist."
        )

    settings = load_settings(settings_file)
    settings[key] = value
    write_settings(settings, settings_file)
    logging.info(f"{level.name.capitalize()} settings updated: {str(settings_file)}")
    logging.info(f"Updated setting: {key} --> {value}")


def unset_impl(key: str, level: SettingsLevel, location: Path) -> None:
    """Unset / remove setting from local (or global) config."""
    settings_file = resolve_settings_file(level, location)
    if not settings_file.exists():
        raise ConfigError(
            f"{level.name.capitalize()} settings file ({str(settings_file)}) does not exist."
        )

    settings = load_settings(settings_file)
    if key not in settings:
        raise ConfigError(f"No value set for {key} at {level.name.lower()} level.")
    settings.pop(key)
    write_settings(settings, settings_file)
    logging.info(f"{level.name.capitalize()} settings updated: {str(settings_file)}")
    logging.info(f"Removed setting: {key}")


def restore_impl(level: SettingsLevel, location: Path) -> None:
    """Restore values in specified file (by level) to default values"""
    settings_file = resolve_settings_file(level, location or Path.cwd())
    if not settings_file.exists():
        raise ConfigError(
            f"{level.name.capitalize()} settings file ({str(settings_file)}) does not exist."
        )

    defaults = {
        key: str(value.default)
        for key, value in TreeBuildSettings.model_fields.items()
        if value.default is not PydanticUndefined
    }
    write_settings(defaults, settings_file)
    logging.info(f"{level.name.capitalize()} settings updated: {str(settings_file)}")
    for key, value in defaults.items():
        logging.info(f"Restored to default setting: {key} --> {value}")


def restore_specific_impl(key: str, level: SettingsLevel, location: Path) -> None:
    """Restore specific field back to default value."""
    if key not in TreeBuildSettings.model_fields:
        raise ConfigError(f"No default value for known for: {key}")

    settings_file = resolve_settings_file(level, location or Path.cwd())
    if not settings_file.exists():
        raise ConfigError(
            f"{level.name.capitalize()} settings file ({str(settings_file)}) does not exist."
        )

    settings = load_settings(settings_file)
    default = str(TreeBuildSettings.model_fields[key].default)
    settings[key] = default
    write_settings(settings, settings_file)
    logging.info(f"{level.name.capitalize()} settings updated: {str(settings_file)}")
    logging.info(f"Restored to default setting: {key} --> {default}")


def create_dir_impl(level: SettingsLevel, location: Path) -> None:
    """Create ~/.config/treebuild/ or a local .treebuild/ directory."""

    directory = resolve_treebuild_dir(level, location)
    if directory.exists():
        raise ConfigError(f"{directory} already exists.")
    directory.mkdir(parents=True, exist_ok=True)
    logging.info(f"Created: {str(directory)}")


def delete_dir_impl(level: SettingsLevel, location: Path) -> None:
    """Delete ~/.config/treebuild/ or a local .treebuild/ directory."""
    directory = resolve_treebuild_dir(level, location)
    if not directory.exists():
        raise ConfigError(f"{directory} does not exist.")
    rmtree(directory)
    logging.info(f"Removed: {str(directory)}")
