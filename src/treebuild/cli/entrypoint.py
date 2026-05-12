"""CLI entrypoint & routing."""

from typing import Annotated

from typer import Context, Option, Typer, echo

from treebuild.cli.routing.harvest import harvest_app
from treebuild.cli.routing.treebuild import app as main_app
from treebuild.core.logging import setup_logging

# Tool will call this `app()` instance
app = Typer()
app.add_typer(main_app)
app.add_typer(
    harvest_app,
    name="harvest",
    help="Use your tree to render text or scaffold on filesystem. ",
)


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    verbose: Annotated[
        bool, Option("--verbose", "-v", help="Show detailed output.")
    ] = False,
    quiet: Annotated[
        bool, Option("--quiet", "-q", help="Suppress all messages except errors.")
    ] = False,
) -> None:
    # if tool name (treebuild) is typed without any command --> show help message
    if ctx.invoked_subcommand is None:
        echo(ctx.get_help())

    # setup logging with logging level based on flags
    setup_logging(verbose=verbose, quiet=quiet)


if __name__ == "__main__":
    app()
