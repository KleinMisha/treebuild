"""Custom exception hierarchy"""


class TreeBuildError(Exception):
    """Base for all treebuild related errors."""


class DuplicatePathError(TreeBuildError): ...


class NoRootSetError(TreeBuildError): ...


class EmptySessionError(TreeBuildError): ...


class TreeAssemblyError(TreeBuildError): ...
