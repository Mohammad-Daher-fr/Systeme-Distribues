from __future__ import annotations
from src.mem_storage import Mem


def main() -> None:
    mem = Mem(host="localhost", port=11211, lru_capacity=2)

    v1 = b"DATA_1"
    v2 = b"DATA_2"
    v3 = b"DATA_3"

    # Insert K1, K2
    mem.create("K1", v1)
    mem.create("K2", v2)

    print("After K1,K2:", mem.lru.keys_mru_to_lru() if mem.lru else None)

    # Access K1 => K1 devient MRU, K2 devient LRU
    _ = mem.read("K1")
    print("After read(K1):", mem.lru.keys_mru_to_lru() if mem.lru else None)

    # Insert K3 => capacité=2 => éviction du LRU (K2)
    mem.create("K3", v3)
    print("After K3:", mem.lru.keys_mru_to_lru() if mem.lru else None)

    # Vérification côté memcached
    k1 = mem.read("K1")
    k2 = mem.read("K2")
    k3 = mem.read("K3")

    print("K1 exists:", k1 is not None)
    print("K2 exists:", k2 is not None)
    print("K3 exists:", k3 is not None)


if __name__ == "__main__":
    main()
