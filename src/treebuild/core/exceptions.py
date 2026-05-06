"""Custom exception hierarchy"""


class TreeBuildError(Exception):
    """Base for all treebuild related errors."""


class DuplicatePathError(TreeBuildError): ...


class EmptySessionError(TreeBuildError): ...


class SessionAlreadyExistsError(TreeBuildError): ...


class NoRootSetError(TreeBuildError): ...


class RootAlreadySetError(TreeBuildError): ...


class TreeAssemblyError(TreeBuildError): ...
