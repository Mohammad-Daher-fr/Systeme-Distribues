from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class _Node:
    key: bytes
    prev: Optional["_Node"] = None
    next: Optional["_Node"] = None


class LRU:
    """
    - head = plus récent
    - tail = moins récent
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("LRU capacity must be > 0")
        self.capacity = capacity
        self._map: Dict[bytes, _Node] = {}
        self.head: Optional[_Node] = None
        self.tail: Optional[_Node] = None

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key: bytes) -> bool:
        return key in self._map

    def _detach(self, node: _Node) -> None:
        # Retire node de la liste
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None

    def _attach_front(self, node: _Node) -> None:
        # Ajoute node en tête (MRU)
        node.prev = None
        node.next = self.head
        if self.head:
            self.head.prev = node
        self.head = node
        if self.tail is None:
            self.tail = node

    def touch(self, key: bytes) -> None:
        """
        Marque la clé comme récemment utilisée (si elle existe).
        """
        node = self._map.get(key)
        if node is None:
            return
        self._detach(node)
        self._attach_front(node)

    def create(self, key: bytes) -> List[bytes]:
        """
        Déclare/insère la clé dans le LRU (MRU).
        Retourne la liste des clés expulsées si dépassement de capacité.
        """
        evicted: List[bytes] = []

        # Si déjà présente -> juste la remonter
        node = self._map.get(key)
        if node is not None:
            self._detach(node)
            self._attach_front(node)
            return evicted

        # Nouvelle clé -> insertion en tête
        node = _Node(key=key)
        self._map[key] = node
        self._attach_front(node)

        # Eviction si overflow
        while len(self._map) > self.capacity:
            assert self.tail is not None
            lru_node = self.tail
            self._detach(lru_node)
            del self._map[lru_node.key]
            evicted.append(lru_node.key)

        return evicted

    def delete(self, key: bytes) -> None:
        node = self._map.get(key)
        if node is None:
            return
        self._detach(node)
        del self._map[key]

    def keys_mru_to_lru(self) -> List[bytes]:
        """
        Debug: clés du plus récent au moins récent.
        """
        out: List[bytes] = []
        cur = self.head
        while cur is not None:
            out.append(cur.key)
            cur = cur.next
        return out
