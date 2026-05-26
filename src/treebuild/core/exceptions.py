"""Custom exception hierarchy"""


class TreeBuildError(Exception):
    """Base for all treebuild related errors."""


class DuplicatePathError(TreeBuildError): ...


class EmptyTreeError(TreeBuildError): ...


class TreeAlreadyExistsError(TreeBuildError): ...


class NoRootSetError(TreeBuildError): ...


class RootAlreadySetError(TreeBuildError): ...


class RootDirNotFoundError(TreeBuildError): ...


class ConfigError(TreeBuildError): ...
