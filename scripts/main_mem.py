from __future__ import annotations
import hashlib
import time
from pathlib import Path
from src.mem_storage import Mem
from src.utils_image import open_file, save_image_from_bytes


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "data" / "image.png"
    work_dir = repo_root / "work"
    preview_dir = work_dir / "previews_mem"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Image d'entrée introuvable: {input_path}\n"
        )

    # 1) Lit I -> T
    t = input_path.read_bytes()
    print("T: size =", len(t), "bytes")
    print("SHA256(T) =", sha256(t))

    # Preview T
    p_t = save_image_from_bytes(t, preview_dir / "T.png")

    # 2) Connexion memcached
    mem = Mem(host="localhost", port=11211)

    # 3) Ecrit T sous une clé K
    key = "K"

    t0 = time.perf_counter_ns()
    mem.create(key, t)
    t1 = time.perf_counter_ns()
    print(f"Ecriture memcached: {(t1 - t0)/1e6:.3f} ms (key={key})")

    # 4) Lit K -> T2
    t0 = time.perf_counter_ns()
    t2 = mem.read(key)
    t1 = time.perf_counter_ns()
    print(f"Lecture memcached: {(t1 - t0)/1e6:.3f} ms (key={key})")

    if t2 is None:
        raise RuntimeError("Memcached a retourné None (clé absente ou échec set/get)")

    print("T2: size =", len(t2), "bytes")
    print("SHA256(T2) =", sha256(t2))

    # Preview T2
    p_t2 = save_image_from_bytes(t2, preview_dir / "T2.png")

    # Vérif non-corruption
    if t != t2:
        raise RuntimeError("Données corrompues: T != T2")
    print("Pas de corruption")

    # Affiche infos previews
    print("Previews générés :")
    print(" -", p_t)
    print(" -", p_t2)
    open_file(p_t)
    open_file(p_t2)

    # Option: nettoyage
    # mem.delete(key)


if __name__ == "__main__":
    main()
