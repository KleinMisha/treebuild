"""Let Pydantic-settings take care of loading settings from ~/.config/treebuild/config.toml"""

import tomllib
from enum import Enum, auto
from pathlib import Path
from typing import Any

import tomli_w
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from treebuild.harvest.render_factory import RenderMethod

TOML = dict[str, Any]
ENV_PREFIX = "TREEBUILD_"
GLOBAL_TREEBUILD_DIR = Path().home() / ".config" / "treebuild"
LOCAL_TREEBUILD_DIR = Path(".treebuild/")
SESSION_FILE_NAME = "tree.txt"
SETTINGS_FILE_NAME = "settings.toml"
GLOBAL_SETTINGS_PATH = GLOBAL_TREEBUILD_DIR / SETTINGS_FILE_NAME
LOCAL_SETTINGS_PATH = LOCAL_TREEBUILD_DIR / SETTINGS_FILE_NAME
GLOBAL_SESSION_PATH = GLOBAL_TREEBUILD_DIR / SESSION_FILE_NAME


class SettingsLevel(Enum):
    LOCAL = auto()
    GLOBAL = auto()


# Pydantic model: resolving settings from both local / global config.
class TreeBuildSettings(BaseSettings):
    """Default settings"""

    model_config = SettingsConfigDict(
        toml_file=GLOBAL_SETTINGS_PATH,
        env_prefix=ENV_PREFIX,
    )

    session_file: Path = GLOBAL_SESSION_PATH
    renderer: RenderMethod = RenderMethod.PLAIN

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Priority of loading variables

        1. Constructor (TreeBuildSettings(key=value), aka the __init__() method)
        2. Global config TOML file (~/.config/treebuild/settings.toml)
        3. Local config TOML file (<root>/.config/treebuild/settings.toml)
        4. Environment variables (so you can 'env export variables' in terminal or `.zshrc`-like file)

        ---
        NOTE: ENV variables will only be used for testing purposes. Not intended to be utilized by the user (if they do, it will overwrite any local settings)
        """

        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls, toml_file=GLOBAL_SETTINGS_PATH),
            TomlConfigSettingsSource(
                settings_cls,
                toml_file=LOCAL_SETTINGS_PATH if LOCAL_SETTINGS_PATH else None,
            ),
            env_settings,
        )


def get_settings() -> TreeBuildSettings:
    """Gets the resolved settings based on the priority chain configured in the Pydantic-settings model."""
    return TreeBuildSettings()


# handling TOML files
def write_settings(settings: TOML, file: Path) -> None:
    """Save settings to file."""
    file.write_bytes(tomli_w.dumps(settings).encode())


def load_settings(file: Path) -> TOML:
    """Load settings from given file."""
    return tomllib.loads(file.read_text())


# Resolving file paths
def resolve_settings_file(level: SettingsLevel, start_search: Path) -> Path:
    return _resolve_treebuild_file(level, start_search, filename=SETTINGS_FILE_NAME)


def resolve_session_file(level: SettingsLevel, start_search: Path) -> Path:
    return _resolve_treebuild_file(level, start_search, filename=SESSION_FILE_NAME)


def resolve_treebuild_dir(level: SettingsLevel, start_search: Path) -> Path:
    """Get either the local or global directory with treebuild related files."""
    return (
        _find_local_treebuild_dir(start_search) or start_search / LOCAL_TREEBUILD_DIR
        if level == SettingsLevel.LOCAL
        else GLOBAL_TREEBUILD_DIR
    )


def _resolve_treebuild_file(
    level: SettingsLevel, start_search: Path, filename: str
) -> Path:
    """
    Get path to file inside of the directory.
    """
    dirname = resolve_treebuild_dir(level, start_search)
    return dirname / filename


def _find_local_treebuild_dir(start_search: Path) -> Path | None:
    """
    Search upwards for the .treebuild/ directory from the cwd upwards.
    ---

    Raises if no .treebuild/ directory can be found.
    """
    for directory in [start_search, *start_search.parents]:
        candidate = directory / LOCAL_TREEBUILD_DIR
        if candidate.exists():
            return candidate
    return None
