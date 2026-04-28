"""CLI entrypoint & routing."""

from typer import Typer

from treebuild.cli.harvest import harvest_app
from treebuild.cli.treebuild import app as main_app

# Tool will call this `app()` instance
app = Typer()
app.add_typer(main_app)
app.add_typer(harvest_app, name="harvest")

if __name__ == "__main__":
    app()
