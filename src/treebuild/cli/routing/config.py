"""Secondary group of commands, which will be called as 'treebuild config <COMMAND> <ARGS> <OPTIONS>'"""

import logging
from pathlib import Path
from typing import Annotated

from typer import Argument, Exit, Option, Typer

from treebuild.cli.commands.config import (
    create_dir_impl,
    create_impl,
    delete_dir_impl,
    delete_settings_impl,
    restore_impl,
    restore_specific_impl,
    set_impl,
    show_impl,
    unset_impl,
)
from treebuild.core.exceptions import ConfigError
from treebuild.core.settings import SettingsLevel

config_app = Typer()


@config_app.command()
def show(
    active: Annotated[
        bool, Option("--active", "-a", help="Only show active/resolved settings.")
    ] = False,
    local: Annotated[
        bool, Option("--local", "-l", help="Only show local settings.")
    ] = False,
    global_: Annotated[
        bool, Option("--global", "-g", help="Only show global settings.")
    ] = False,
    loc: Annotated[
        Path | None,
        Option(
            "--local-dir", help="Path to where local .treebuild/ can be discovered."
        ),
    ] = None,
) -> None:
    """Display active configuration settings as well as local/global values."""

    if (active + local + global_) > 1:
        logging.error(
            "Error: use only one of --active, --local, --global."
            "To display all settings call treebuild config show without any flags."
        )
        raise Exit(code=1)
    # NOTE: This route is not expected to raise any ConfigError (or another TreeBuildError), so if it does, let things crash.
    loc_dir = loc or Path.cwd()
    if active:
        show_impl(
            incl_active=True, incl_local=False, incl_global=False, location=loc_dir
        )
    elif local:
        show_impl(
            incl_active=False, incl_local=True, incl_global=False, location=loc_dir
        )
    elif global_:
        show_impl(
            incl_active=False, incl_local=False, incl_global=True, location=loc_dir
        )
    else:
        show_impl(incl_active=True, incl_local=True, incl_global=True, location=loc_dir)
    raise Exit(code=0)


@config_app.command()
def create(
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
) -> None:
    """Create a new settings.yaml file."""
    try:
        loc_dir = loc or Path.cwd()
        create_impl(level, loc_dir)
        raise Exit(code=0)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)


@config_app.command()
def delete(
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
    dry_run: Annotated[
        bool,
        Option("--dry-run", help="Only print which file would be deleted."),
    ] = False,
) -> None:
    try:
        loc_dir = loc or Path.cwd()
        delete_settings_impl(level, loc_dir, dry_run)
        raise Exit(code=0)
    except ConfigError as e:
        logging.error(f"{type(e).__name__} : {str(e)}")
        raise Exit(code=1)


@config_app.command()
def set(
    key: Annotated[str, Argument(help="Config key to set.")],
    value: Annotated[str, Argument(help="Value to set it to.")],
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
) -> None:
    """
    Update configuration setting.
    """
    # print("hint: use `treebuild config show` to inspect all available fields.")
    try:
        loc_dir = loc or Path.cwd()
        set_impl(key, value, level, loc_dir)
        raise Exit(code=0)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)


@config_app.command()
def unset(
    key: Annotated[str, Argument(help="Config key to unset.")],
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
) -> None:
    """
    Remove configuration setting.
    """
    try:
        loc_dir = loc or Path.cwd()
        unset_impl(key, level, loc_dir)
        raise Exit(code=0)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)


@config_app.command()
def restore(
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
    key: Annotated[str | None, Option("--key", help="Config key to reset.")] = None,
    all_: Annotated[bool, Option("--all", "-a", help="Reset all settings.")] = False,
) -> None:
    """Restores configuration setting(s) to default."""
    if (not all_) and (key is None):
        logging.error(
            "Error: Use one of --key or --all."
            "To restore a specific field's value: treebuild config restore --key <KEY>"
            "To restore all fields to their default values: treebuild config restore --all"
        )
        raise Exit(code=1)

    if all_ and (key is not None):
        logging.error(
            "Error: Use only one of --key or --all."
            "To restore a specific field's value: treebuild config restore --key <KEY>"
            "To restore all fields to their default values: treebuild config restore --all"
        )
        raise Exit(code=1)

    try:
        loc_dir = loc or Path.cwd()
        if all_:
            restore_impl(level, loc_dir)
        if key is not None:
            restore_specific_impl(key, level, loc_dir)
        raise Exit(code=0)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)


@config_app.command()
def create_dir(
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
) -> None:
    """Creates directory for treebuild related files (configuration, session store, etc.)"""
    try:
        loc_dir = loc or Path.cwd()
        create_dir_impl(level, loc_dir)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)


@config_app.command()
def delete_dir(
    level: Annotated[
        SettingsLevel,
        Option("--level", "-l", help="Select local/global settings."),
    ] = SettingsLevel.LOCAL,
    loc: Annotated[
        Path | None,
        Option("--local-dir", help="Path to where .treebuild/ can be discovered."),
    ] = None,
    dry_run: Annotated[
        bool, Option("--dry-run", help="Only print which directory would be deleted.")
    ] = False,
) -> None:
    """Deletes directory for treebuild related files (configuration, session store, etc.)"""
    try:
        loc_dir = loc or Path.cwd()
        delete_dir_impl(level, loc_dir, dry_run)
    except ConfigError as e:
        logging.error(f"{type(e).__name__}: {str(e)}")
        raise Exit(code=1)
