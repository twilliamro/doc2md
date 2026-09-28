"""Extração de imagens embutidas: salva apenas PNGs relevantes em assets/."""

import base64
import re
from pathlib import Path

from .config import MIN_PNG_BYTES


def extract_base64_images(text: str, assets_dir: Path, stem: str) -> tuple[str, int]:
    """Salva PNGs embutidos (>= 10 KB) em assets/ e limpa o resto.
    Retorna (texto atualizado, quantidade de imagens salvas)."""
    pattern = re.compile(r"!\[([^\]]*)\]\(data:image/(\w+);base64,([^)]+)\)")
    counter = 0

    def repl(m: re.Match) -> str:
        nonlocal counter
        alt, fmt, b64 = m.groups()
        try:
            data = base64.b64decode(b64)
        except Exception:
            return ""
        if fmt.lower() == "png" and len(data) >= MIN_PNG_BYTES:
            counter += 1
            assets_dir.mkdir(parents=True, exist_ok=True)
            fname = f"{stem}_{counter:03d}.png"
            (assets_dir / fname).write_bytes(data)
            return f"![{alt}](assets/{stem}/{fname})"
        return ""

    return pattern.sub(repl, text), counter
