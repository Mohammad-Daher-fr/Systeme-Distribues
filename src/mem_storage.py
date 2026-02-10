from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union
from pymemcache.client.base import Client

Key = Union[str, bytes]

def _key_bytes(k: Key) -> bytes:
    return k if isinstance(k, (bytes, bytearray)) else k.encode("utf-8")

@dataclass
class Mem:
    host: str = "localhost"
    port: int = 11211

    def __post_init__(self) -> None:
        self.client = Client((self.host, self.port))

    def create(self, key: Key, data: bytes) -> None:
        self.client.set(_key_bytes(key), data)

    def read(self, key: Key) -> Optional[bytes]:
        return self.client.get(_key_bytes(key))

    def delete(self, key: Key) -> None:
        self.client.delete(_key_bytes(key))
