from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


PathLike = Union[str, Path]


@dataclass
class FS:
    """
    FS = abstraction minimale du système de fichiers.
    Méthodes: create, list, read, delete.
    """
    base_dir: Path

    def __post_init__(self) -> None:
        self.base_dir = Path(self.base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _full_path(self, p: PathLike) -> Path:
        p = Path(p)
        return p if p.is_absolute() else (self.base_dir / p)

    def create(self, path: PathLike, data: Optional[bytes] = None, is_dir: bool = False) -> Path:
        full = self._full_path(path)
        if is_dir:
            full.mkdir(parents=True, exist_ok=True)
            return full

        if data is None:
            raise ValueError("FS.create(...): data must be provided when is_dir=False")

        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)
        return full

    def list(self, path: PathLike = ".") -> List[Path]:
        full = self._full_path(path)
        if not full.exists():
            return []
        if full.is_file():
            return [full]
        return sorted([p for p in full.iterdir()])

    def read(self, path: PathLike) -> bytes:
        full = self._full_path(path)
        return full.read_bytes()

    def delete(self, path: PathLike) -> None:
        full = self._full_path(path)
        if not full.exists():
            return
        if full.is_dir():
            # suppression dir uniquement si vide
            full.rmdir()
        else:
            full.unlink()
