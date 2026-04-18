"""Custom exception hierarchy"""


class TreeBuildError(Exception):
    """Base for all treebuild related errors."""


class DuplicatePathError(TreeBuildError): ...


class EmptySessionError(TreeBuildError): ...


class TreeAssemblyError(TreeBuildError): ...
