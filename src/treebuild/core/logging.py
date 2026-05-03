"""Logging config.

NOTE for a CLI the logger is setup much more basic (no time stamps / log levels / paper trails etc.)
"""

import logging
import sys


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Basic logging setup for a CLI.
    ---

    NOTE use the verbose level for all commands ran as a dry-run.
    """

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.ERROR if quiet else logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
