"""CLI entrypoint & routing."""

from typing import Annotated

from typer import Option, Typer

from treebuild.cli.harvest import harvest_app
from treebuild.cli.treebuild import app as main_app
from treebuild.core.logging import setup_logging

# Tool will call this `app()` instance
app = Typer()
app.add_typer(main_app)
app.add_typer(harvest_app, name="harvest")


@app.callback()
def main(
    verbose: Annotated[
        bool, Option("--verbose", "-v", help="Show detailed output.")
    ] = False,
    quiet: Annotated[
        bool, Option("--quiet", "-q", help="Suppress all messages except errors.")
    ] = False,
) -> None:

    # setup logging with logging level based on flags
    setup_logging(verbose=verbose, quiet=quiet)


if __name__ == "__main__":
    app()
