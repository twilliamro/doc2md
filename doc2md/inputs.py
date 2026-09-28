"""Resolução das entradas: arquivos, diretórios, globs e URLs."""

import tempfile
from pathlib import Path

from .config import SUPPORTED, VIA_LIBREOFFICE
from .net import download_url


def clean_path(raw: str) -> str:
    """Limpa texto colado/arrastado no terminal (aspas, espaços escapados)."""
    raw = raw.strip().strip("'\"")
    return raw.replace("\\ ", " ")


def is_url(text: str) -> bool:
    return text.lower().startswith(("http://", "https://"))


def collect_inputs(inputs: list[str]) -> tuple[list[Path], list[str], list[Path]]:
    """Resolve arquivos, diretórios, globs e URLs.
    Retorna (válidos, avisos, diretórios-temporários-para-limpar)."""
    files, warnings, tmpdirs = [], [], []
    for item in inputs:
        item = clean_path(item)
        if is_url(item):
            try:
                tmp = Path(tempfile.mkdtemp(prefix="doc2md_dl_"))
                files.append(download_url(item, tmp))
                tmpdirs.append(tmp)
            except Exception as e:
                warnings.append(f"falha no download: {e}")
            continue
        p = Path(item).expanduser()
        if any(ch in item for ch in "*?["):
            files.extend(Path().glob(item))
        elif p.is_dir():
            files.extend(f for f in sorted(p.rglob("*")) if f.is_file())
        elif p.is_file():
            files.append(p)
        else:
            warnings.append(f"não encontrado: {item}")

    valid, seen = [], set()
    for f in files:
        rp = f.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        if f.suffix.lower() in SUPPORTED | VIA_LIBREOFFICE:
            valid.append(f)
        else:
            warnings.append(f"tipo não suportado (ignorado): {f.name}")
    return valid, warnings, tmpdirs
