"""Integration tests for src/treebuild/cli/entrypoint.py"""

import logging

from typer.testing import CliRunner

from treebuild.cli.entrypoint import app
from typer import Context
from typer.main import get_command


@app.command()
def mock_cmd() -> None:
    """Simple logging messages. Used to test verbosity level"""
    logging.debug("debug message")
    logging.info("info message")
    logging.warning("warning message")
    logging.error("error message")


def test_default_logging() -> None:
    """Call without additional flags: Shows everything from info and lower."""
    runner = CliRunner()
    result = runner.invoke(app, ["mock-cmd"])
    assert "debug message" not in result.stdout
    assert "info message" in result.stdout
    assert "warning message" in result.stdout
    assert "error message" in result.stdout


def test_verbose_mode() -> None:
    """Verbose mode should also show debug messages"""
    runner = CliRunner()
    result = runner.invoke(app, ["--verbose", "mock-cmd"])
    assert "info message" in result.stdout
    assert "warning message" in result.stdout
    assert "debug message" in result.stdout
    assert "error message" in result.stdout


def test_quiet_mode() -> None:
    """Quiet mode should only show actual errors"""
    runner = CliRunner()
    result = runner.invoke(app, ["--quiet", "mock-cmd"])
    assert "info message" not in result.stdout
    assert "warning message" not in result.stdout
    assert "debug message" not in result.stdout
    assert "error message" in result.stdout


def test_no_command_show_help() -> None:
    """Running without any command should be equivalent to using the --help command on the tool name."""
    runner = CliRunner()
    result = runner.invoke(app, [])
    assert result.exit_code == 0

    with Context(get_command(app)) as ctx:
        help_msg = ctx.get_help()
    assert help_msg in result.stdout
