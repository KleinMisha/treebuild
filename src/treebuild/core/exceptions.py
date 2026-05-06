"""Custom exception hierarchy"""

import functools
from typing import Any, Callable


class TreeBuildError(Exception):
    """Base for all treebuild related errors."""


class DuplicatePathError(TreeBuildError): ...


class EmptySessionError(TreeBuildError): ...


class SessionAlreadyExistsError(TreeBuildError): ...


class TreeAssemblyError(TreeBuildError): ...


CliCommand = Callable[..., None]
ErrorHandler = Callable[[TreeBuildError], None]


def with_error_handling(
    handlers: dict[type[TreeBuildError], ErrorHandler],
) -> Callable[[CliCommand], CliCommand]:
    """
    Handle exceptions using a custom handler function for a given exception type.
    -----

    Supply a mapping from exception (types) --> handler function
    NOTE if some other exception occurs, other than the ones explicitly defined in the mapping,
        intentionally letting the programme crash as this indicates a programming error.
    """

    def decorator(command: CliCommand) -> CliCommand:
        @functools.wraps(command)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            try:
                command(*args, **kwargs)
            except TreeBuildError as e:
                try:
                    handlers[type(e)](e)
                except KeyError:
                    raise KeyError(
                        f"No handler defined for exception {type(e).__name__} on method {command.__name__}"
                    )

        return wrapper

    return decorator
