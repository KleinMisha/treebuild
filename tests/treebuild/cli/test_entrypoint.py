"""Integration tests for src/treebuild/cli/entrypoint.py"""

import logging

from typer.testing import CliRunner

from treebuild.cli.entrypoint import app


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
