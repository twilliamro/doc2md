"""Conversão de documentos para Markdown (markitdown + LibreOffice p/ legados)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import VIA_LIBREOFFICE
from .images import extract_base64_images
from .normalize import normalize_markdown

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

_md_instance = None  # reutiliza uma única instância (economia de tempo/memória)


def markitdown_available() -> bool:
    return MarkItDown is not None


def _get_md() -> "MarkItDown":
    global _md_instance
    if _md_instance is None:
        _md_instance = MarkItDown(enable_plugins=False)
    return _md_instance


def find_soffice() -> str | None:
    """Localiza o LibreOffice no macOS ou no PATH."""
    for c in ("/Applications/LibreOffice.app/Contents/MacOS/soffice",
              shutil.which("soffice"), shutil.which("libreoffice")):
        if c and Path(c).exists():
            return c
    return None


def convert_legacy(path: Path, tmpdir: Path) -> Path:
    """Converte .doc/.ppt para .docx/.pptx usando LibreOffice headless."""
    soffice = find_soffice()
    if not soffice:
        raise RuntimeError(
            "formato legado requer LibreOffice (brew install --cask libreoffice)")
    target = "docx" if path.suffix.lower() == ".doc" else "pptx"
    subprocess.run([soffice, "--headless", "--convert-to", target,
                    "--outdir", str(tmpdir), str(path)],
                   check=True, capture_output=True, timeout=300)
    converted = tmpdir / f"{path.stem}.{target}"
    if not converted.exists():
        raise RuntimeError("LibreOffice não gerou o arquivo convertido")
    return converted


def convert_file(src: Path, out_dir: Path) -> tuple[Path | None, str]:
    """Converte um arquivo. Retorna (destino, detalhe) ou (None, erro)."""
    suffix = src.suffix.lower()
    try:
        if suffix == ".md":
            dest = out_dir / src.name
            shutil.copy2(src, dest)
            return dest, "copiado"

        if suffix == ".txt":
            dest = out_dir / f"{src.stem}.md"
            dest.write_text(src.read_text(encoding="utf-8", errors="replace"),
                            encoding="utf-8")
            return dest, "texto puro"

        tmp, work = None, src
        if suffix in VIA_LIBREOFFICE:
            tmp = Path(tempfile.mkdtemp(prefix="doc2md_"))
            work = convert_legacy(src, tmp)

        result = _get_md().convert(str(work))
        text = result.text_content or ""
        if not text.strip():
            raise RuntimeError("conversão resultou em conteúdo vazio "
                               "(PDF escaneado? seria preciso OCR)")

        text, n_imgs = extract_base64_images(text, out_dir / "assets" / src.stem,
                                             src.stem)
        text, detalhe_norm = normalize_markdown(text)
        dest = out_dir / f"{src.stem}.md"
        dest.write_text(text, encoding="utf-8")

        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

        detail = f"{len(text):,} caracteres" + (f", {detalhe_norm}"
                                                if detalhe_norm else "")
        if n_imgs:
            detail += f", {n_imgs} imagem(ns) .png"
        return dest, detail

    except subprocess.TimeoutExpired:
        return None, "timeout no LibreOffice (>5 min)"
    except subprocess.CalledProcessError:
        return None, "falha na conversão via LibreOffice"
    except PermissionError:
        return None, "sem permissão de leitura"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"