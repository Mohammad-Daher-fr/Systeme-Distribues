from __future__ import annotations

import hashlib
import time
from pathlib import Path

from src.fs_storage import FS
from src.utils_image import open_file, save_image_from_bytes


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "data"/ "image.png"
    work_dir = repo_root / "work"
    preview_dir = work_dir / "previews"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Image d'entrée introuvable: {input_path}\n"
        )

    fs = FS(base_dir=work_dir)

    # 1) Crée R
    fs.create("R", is_dir=True)

    # 2) Liste contenu (work/)
    print("Contenu work/:")
    for p in fs.list("."):
        print(" -", p.name)

    # 3) Lit I -> T
    t = input_path.read_bytes()
    print("SHA256(T) =", sha256(t))

    # Preview T
    p_t = save_image_from_bytes(t, preview_dir / "T.png")

    # 4) Écrit T -> F (dans work/R/)
    out_file = Path("R") / f"F{input_path.suffix}"

    t0 = time.perf_counter_ns()
    fs.create(out_file, data=t, is_dir=False)
    t1 = time.perf_counter_ns()
    print(f"Ecriture F: {(t1 - t0)/1e6:.3f} ms -> {work_dir/out_file}")

    # 5) Lit F -> T2
    t0 = time.perf_counter_ns()
    t2 = fs.read(out_file)
    t1 = time.perf_counter_ns()
    print(f"Lecture F: {(t1 - t0)/1e6:.3f} ms")
    print("SHA256(T2) =", sha256(t2))

    # Preview T2
    p_t2 = save_image_from_bytes(t2, preview_dir / "T2.png")

    # Vérif non-corruption
    if t != t2:
        raise RuntimeError("Données corrompues: T != T2")
    print("Pas de corruption)")

    # Ouvre les previews (WSL -> explorer.exe, sinon xdg-open)
    print("Previews générés :")
    print(" -", p_t)
    print(" -", p_t2)
    open_file(p_t)
    open_file(p_t2)


if __name__ == "__main__":
    main()
