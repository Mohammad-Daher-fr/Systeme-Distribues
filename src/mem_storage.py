from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union
from pymemcache.client.base import Client
from src.lru import LRU

Key = Union[str, bytes]


def _key_bytes(k: Key) -> bytes:
    return k if isinstance(k, (bytes, bytearray)) else k.encode("utf-8")


@dataclass
class Mem:
    host: str = "localhost"
    port: int = 11211
    lru_capacity: Optional[int] = None  

    def __post_init__(self) -> None:
        self.client = Client((self.host, self.port))
        self.lru: Optional[LRU] = LRU(self.lru_capacity) if self.lru_capacity else None

    def create(self, key: Key, data: bytes) -> None:
        k = _key_bytes(key)

        # écrire en memcached et vérifier que ça a bien été stocké
        ok = self.client.set(k, data, noreply=False)
        if not ok:
            raise RuntimeError("Echec memcached set(): objet trop gros ? memcached down ?")

        # mise à jour LRU + évictions
        if self.lru is not None:
            evicted = self.lru.create(k)
            for ek in evicted:
                self.client.delete(ek)

    def read(self, key: Key) -> Optional[bytes]:
        k = _key_bytes(key)
        val = self.client.get(k)

        # Si hit : on marque comme MRU
        if val is not None and self.lru is not None:
            self.lru.touch(k)

        return val

    def delete(self, key: Key) -> None:
        k = _key_bytes(key)
        self.client.delete(k)
        if self.lru is not None:
            self.lru.delete(k)
