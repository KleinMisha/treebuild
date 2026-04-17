"""Let Pydantic-settings take care of loading settings from ~/.config/treebuild/config.toml"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from treebuild.rendering.renderer_types import RendererType

# DEFAULTS TO FALL BACK TO:
DEFAULT_SESSION_FILE = Path().home() / ".config" / "treebuild" / "session_tree.txt"


class TreeBuildSettings(BaseSettings):
    """Default settings"""

    session_file: Path = DEFAULT_SESSION_FILE
    renderer: RendererType = RendererType.PLAIN

    model_config = SettingsConfigDict(
        toml_file=Path().home() / ".config" / "treebuild" / "config.toml"
    )


def get_settings() -> TreeBuildSettings:
    return TreeBuildSettings()
