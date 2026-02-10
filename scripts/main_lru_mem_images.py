from __future__ import annotations
import hashlib
import time
from pathlib import Path
from src.mem_storage import Mem
from src.utils_image import open_file, save_image_from_bytes


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_bytes(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    return path.read_bytes()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    work_dir = repo_root / "work"
    preview_dir = work_dir / "previews_lru_mem"

    
    img1 = repo_root / "data" / "image.png"
    img2 = repo_root / "data" / "image.png"
    img3 = repo_root / "data" / "image.png"


    t1 = load_bytes(img1)
    t2 = load_bytes(img2)
    t3 = load_bytes(img3)

    print("Sizes:", len(t1), len(t2), len(t3))
    print("SHA256(T1) =", sha256(t1))
    print("SHA256(T2) =", sha256(t2))
    print("SHA256(T3) =", sha256(t3))

    # Previews sources
    p_src1 = save_image_from_bytes(t1, preview_dir / "SRC1.png")
    p_src2 = save_image_from_bytes(t2, preview_dir / "SRC2.png")
    p_src3 = save_image_from_bytes(t3, preview_dir / "SRC3.png")

    # Mem + LRU (capacité 2 => une eviction à l'insertion de la 3e clé)
    mem = Mem(host="localhost", port=11211, lru_capacity=2)

    def put(key: str, data: bytes) -> None:
        t0 = time.perf_counter_ns()
        mem.create(key, data)
        t1n = time.perf_counter_ns()
        print(f"PUT {key}: {(t1n - t0)/1e6:.3f} ms | LRU={mem.lru.keys_mru_to_lru() if mem.lru else None}")

    def get(key: str) -> bytes | None:
        t0 = time.perf_counter_ns()
        out = mem.read(key)
        t1n = time.perf_counter_ns()
        print(f"GET {key}: {(t1n - t0)/1e6:.3f} ms | hit={out is not None} | LRU={mem.lru.keys_mru_to_lru() if mem.lru else None}")
        return out

    # 1) Insert K1, K2
    put("K1", t1)
    put("K2", t2)

    # 2) Access K1 (K1 devient MRU)
    _ = get("K1")

    # 3) Insert K3 => eviction de K2 (car K2 est LRU)
    put("K3", t3)

    # 4) Vérif côté memcached + previews des hits
    out_k1 = get("K1")
    out_k2 = get("K2")
    out_k3 = get("K3")

    if out_k1 is None or out_k3 is None:
        raise RuntimeError("Erreur: K1 ou K3 devrait exister après eviction.")
    if out_k2 is not None:
        raise RuntimeError("Erreur: K2 devrait être expulsée (LRU capacity=2).")

    print("Eviction OK: K2 absente, K1 et K3 présentes")

    # Previews des résultats
    p_k1 = save_image_from_bytes(out_k1, preview_dir / "K1.png")
    p_k3 = save_image_from_bytes(out_k3, preview_dir / "K3.png")

    print("Previews générés :")
    for p in [p_src1, p_src2, p_src3, p_k1, p_k3]:
        print(" -", p)

    # Ouvrir (WSL -> explorer.exe)
    open_file(p_src1)
    open_file(p_src2)
    open_file(p_src3)
    open_file(p_k1)
    open_file(p_k3)


if __name__ == "__main__":
    main()
