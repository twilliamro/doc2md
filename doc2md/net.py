"""Download de URLs (Dropbox, Google Drive, links diretos) com trato de SSL."""

import re
import ssl
import urllib.request
from pathlib import Path

from .config import CONTENT_TYPE_MAP, SUPPORTED, VIA_LIBREOFFICE


def log(msg: str) -> None:
    print(msg, flush=True)


def normalize_url(url: str) -> str:
    """Ajusta links de compartilhamento para download direto."""
    if "dropbox.com" in url:
        url = re.sub(r"[?&]dl=0", "", url)  # dl=0 (página) -> dl=1 (download)
        sep = "&" if "?" in url else "?"
        return url + sep + "dl=1"
    if "drive.google.com" in url and "/file/d/" in url:
        file_id = url.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


def _ssl_context() -> ssl.SSLContext:
    """Prefere certificados do certifi; cai no padrão do sistema."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def download_url(url: str, tmpdir: Path) -> Path:
    """Baixa a URL para um arquivo temporário e retorna o caminho local."""
    url = normalize_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    log("    baixando da web ...")

    try:
        resp = urllib.request.urlopen(req, timeout=120, context=_ssl_context())
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            raise
        log("    ⚠ certificado SSL não pôde ser verificado "
            "(rede corporativa/proxy ou certificados do Python ausentes).")
        resp_in = input("    Baixar mesmo assim, sem verificação? [s/N] ").strip().lower()
        if resp_in not in ("s", "sim", "y", "yes"):
            raise RuntimeError("download cancelado (falha de certificado SSL)")
        resp = urllib.request.urlopen(req, timeout=120,
                                      context=ssl._create_unverified_context())

    with resp:
        data = resp.read()
        ctype = resp.headers.get_content_type()

        # nome original: extraído do caminho da URL (ex.: .../Comunicado-001.pdf)
        from urllib.parse import unquote, urlparse
        name = unquote(Path(urlparse(url).path).name)
        stem, ext = Path(name).stem, Path(name).suffix.lower()
        if ext not in SUPPORTED | VIA_LIBREOFFICE:
            ext = CONTENT_TYPE_MAP.get(ctype, "")
            stem = "download"
        if not ext:
            raise RuntimeError(f"não consegui identificar o tipo do arquivo "
                               f"(Content-Type: {ctype})")
        if ext in (".html", ".htm"):
            # página web: usa o nome do site (ex.: g1.globo.com)
            stem = urlparse(url).hostname or stem or "download"
        local = tmpdir / f"{stem}{ext}"  # <-- nome original preservado
        local.write_bytes(data)
    log(f"    baixado: {local.name} ({len(data) / 1024:.0f} KB)")
    return local