"""Let Pydantic-settings take care of loading settings from ~/.config/treebuild/config.toml"""

from pathlib import Path
from typing import ClassVar

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from treebuild.harvest.render_factory import RenderMethod

# DEFAULTS TO FALL BACK TO:
ENV_PREFIX = "TREEBUILD_"
GLOBAL_TREEBUILD_DIR = Path().home() / ".config" / "treebuild"
LOCAL_TREEBUILD_DIR = Path(".treebuild/")
DEFAULT_SESSION_FILE = "session_tree.txt"
DEFAULT_SETTINGS_FILE = "settings.toml"


class TreeBuildSettings(BaseSettings):
    """Default settings"""

    model_config = SettingsConfigDict(
        toml_file=Path().home() / ".config" / "treebuild" / "config.toml",
        env_prefix=ENV_PREFIX,
    )
    session_file: Path = GLOBAL_TREEBUILD_DIR / DEFAULT_SESSION_FILE
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

        LOCAL_SETTINGS_PATH = LOCAL_TREEBUILD_DIR / DEFAULT_SETTINGS_FILE
        GLOBAL_SETTINGS_PATH: Path = GLOBAL_TREEBUILD_DIR / DEFAULT_SETTINGS_FILE
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
    return TreeBuildSettings()
