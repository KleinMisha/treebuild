from dataclasses import dataclass
from pathlib import Path
from treebuild.storage.settings import GLOBAL_TREEBUILD_DIR


@dataclass
class Cache:
    current_tree: str
    root_location: Path
    local_dir_parent: Path

    def __post_init__(self) -> None:
        self.root_location = Path(self.root_location)
        self.local_dir_parent = Path(self.local_dir_parent)


class CacheStore:
    def __init__(self, file: Path) -> None:
        pass
