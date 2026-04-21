"""
Adjusting (default) configuration settings

Subcommand 'config' --> `treebuild config <COMMAND> <OPTIONS> <ARGS>

"""

from typing import Annotated

from typer import Argument, Typer

app = Typer()


@app.command()
def show() -> None:
    """Display's settings (by default from ~/.config/treebuild/config.toml)"""


@app.command()
def create() -> None:
    """Create a configuration file at ~/.config/treebuild/config.toml"""


@app.command()
def restore() -> None:
    """Restores all configuration values to default."""


@app.command()
def set(
    key: Annotated[str, Argument(help="Config key to set.")],
    value: Annotated[str, Argument(help="Value to set it to.")],
) -> None:
    """
    Adjust configuration setting belonging to the key to the supplied value.
    """
    print("hint: use `treebuild config show` to inspect all available fields.")
