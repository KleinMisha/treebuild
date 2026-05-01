"""Let Pydantic-settings take care of loading settings from ~/.config/treebuild/config.toml"""

from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from treebuild.harvest.render_factory import RenderMethod

# DEFAULTS TO FALL BACK TO:
DEFAULT_SESSION_FILE = Path().home() / ".config" / "treebuild" / "session_tree.txt"
ENV_PREFIX = "TREEBUILD_"


class TreeBuildSettings(BaseSettings):
    """Default settings"""

    model_config = SettingsConfigDict(
        toml_file=Path().home() / ".config" / "treebuild" / "config.toml",
        env_prefix=ENV_PREFIX,
    )
    session_file: Path = DEFAULT_SESSION_FILE
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
        2. Environment variables (so you can 'env export variables' in terminal or `.zshrc`-like file)
        3. config TOML file (~/.config/treebuild/config.toml)

        ---
        NOTE: Setting environment variables is optional, hence excluding some manual overwrite during instantiation,
        values will be parsed from the TOML file.
        """

        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def get_settings() -> TreeBuildSettings:
    return TreeBuildSettings()
