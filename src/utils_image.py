from __future__ import annotations
import io
import os
import subprocess
from pathlib import Path
from PIL import Image


def _is_wsl() -> bool:
    if os.environ.get("WSL_INTEROP"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        return False


def save_image_from_bytes(image_data: bytes, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(io.BytesIO(image_data))
    img.save(out_path)
    return out_path


def open_file(path: Path) -> None:
    """
    Ouvre un fichier avec l'outil système.
    - WSL: explorer.exe
    - Linux: xdg-open
    """
    try:
        if _is_wsl():
            win_path = subprocess.check_output(["wslpath", "-w", str(path)]).decode().strip()
            subprocess.Popen(["explorer.exe", win_path])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        print(f"Impossible d'ouvrir automatiquement: {path}")
