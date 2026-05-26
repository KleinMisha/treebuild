"""Cache values such that user does not need to provide them every time between command calls."""

from pathlib import Path
from typing import Any

import yaml

from treebuild.storage.settings import GLOBAL_TREEBUILD_DIR

CACHE_FILE = GLOBAL_TREEBUILD_DIR / "cache.yaml"

Cache = dict[str, Any]


class CacheStore:
    def __init__(self, file_path: Path = CACHE_FILE) -> None:
        self.file = file_path

    # readers:
    def read_current_tree(self) -> str | None:
        cache = self._load()
        return cache.get("current_tree", None)

    def read_root_location(self) -> Path | None:
        cache = self._load()
        root_location = cache.get("root_location")
        return Path(root_location) if root_location else None

    def read_local_dir_parent(self) -> Path | None:
        cache = self._load()
        local_dir_parent = cache.get("local_dir_parent")
        return Path(local_dir_parent) if local_dir_parent else None

    # writers:
    def write_current_tree(self, name: str) -> None:
        new_cache = self._load()
        new_cache["current_tree"] = name
        self._save(new_cache)

    def write_root_location(self, location: Path) -> None:
        new_cache = self._load()
        new_cache["root_location"] = str(location)
        self._save(new_cache)

    def write_local_dir_parent(self, path: Path) -> None:
        new_cache = self._load()
        new_cache["local_dir_parent"] = str(path)
        self._save(new_cache)

    # lifecycle:
    def clear_file(self) -> None:
        with self.file.open("w") as _:
            pass

    def delete_file(self) -> None:
        self.file.unlink(missing_ok=True)

    # internal:
    def _load(self) -> Cache:
        with self.file.open("r") as f:
            cache = yaml.safe_load(f)
        return cache or {}

    def _save(self, cache: Cache) -> None:
        with self.file.open("w") as f:
            yaml.dump(cache, f)
