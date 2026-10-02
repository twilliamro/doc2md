"""Interface com o usuário: banner, modo interativo e orquestração do fluxo."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .converters import convert_file, markitdown_available
from .inputs import collect_inputs


def log(msg: str) -> None:
    print(msg, flush=True)


def banner() -> None:
    log("=" * 56)
    log("  doc2md — conversor local de documentos para Markdown")
    log("  Suporta: PDF, EPUB, DOCX, PPTX, HTML, DOC, PPT, TXT, CSV")
    log("  Aceita: arquivos, pastas, globs e URLs (Dropbox/Drive)")
    log("=" * 56)


def default_out_dir(src: Path) -> Path:
    """Pasta de saída padrão de um arquivo: ./saida/<origem>/md."""
    return Path("./saida") / src.stem / "md"


def interactive_input() -> tuple[list[str], Path | None]:
    """Modo interativo: pergunta a origem e a pasta de saída (vazio = padrão por origem)."""
    log("\nNenhum argumento informado — vamos configurar juntos.\n")
    log("Arraste um ARQUIVO ou PASTA para esta janela, ou cole uma URL,")
    log("e pressione Enter. (para sair, deixe em branco)\n")
    raw = input("  Origem: ").strip()
    if not raw:
        log("Nada informado. Encerrando.")
        sys.exit(0)

    raw_out = input("  Pasta de saída [./saida/<origem>/md]: ").strip()
    out = Path(raw_out.strip().strip("'\"")).expanduser() if raw_out else None
    return [raw], out


def main() -> int:
    banner()

    parser = argparse.ArgumentParser(
        description="Converte documentos para Markdown "
                    "(sem argumentos, abre o modo interativo).")
    parser.add_argument("inputs", nargs="*",
                        help="arquivo(s), pasta(s), glob(s) ou URL(s)")
    parser.add_argument("-o", "--out", default=None,
                        help="pasta final de saída, sem subpastas "
                             "(padrão: ./saida/<origem>/md, uma pasta por arquivo)")
    args = parser.parse_args()

    if args.inputs:
        inputs = args.inputs
        out_dir = Path(args.out).expanduser() if args.out else None
    else:
        inputs, out_dir = interactive_input()

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    if not markitdown_available():
        log("\nERRO: pacote 'markitdown' não instalado.")
        log("Rode:  pip install 'markitdown[pdf,docx,pptx,epub]'\n")
        return 1

    files, warnings, tmpdirs = collect_inputs(inputs)
    for w in warnings:
        log(f"  ⚠ {w}")

    if not files:
        log("\nNenhum arquivo válido encontrado. Verifique o caminho informado.")
        for tmp in tmpdirs:
            shutil.rmtree(tmp, ignore_errors=True)
        return 1

    dest_label = out_dir.resolve() if out_dir else Path("./saida").resolve() / "<origem>" / "md"
    log(f"\n{len(files)} arquivo(s) → {dest_label}\n")

    ok, failed = [], []
    for i, f in enumerate(files, 1):
        log(f"[{i}/{len(files)}] {f.name}")
        file_out = out_dir if out_dir else default_out_dir(f)
        file_out.mkdir(parents=True, exist_ok=True)
        dest, detail = convert_file(f, file_out)
        if dest:
            log(f"    ✔ ok ({detail})")
            ok.append(dest)
        else:
            log(f"    ✘ FALHOU — {detail}")
            failed.append((f, detail))

    for tmp in tmpdirs:  # limpa downloads temporários
        shutil.rmtree(tmp, ignore_errors=True)

    log("\n" + "-" * 56)
    log(f"Resumo: {len(ok)} convertido(s), {len(failed)} com erro")
    for dest in ok:
        log(f"Saída em: {dest.resolve()}")
    if failed:
        log("\nArquivos com erro:")
        for f, err in failed:
            log(f"  • {f.name}: {err}")
    log("-" * 56)

    if not args.inputs and ok:  # modo interativo: oferece abrir no Finder
        resp = input("\nAbrir a pasta de saída no Finder? [s/N] ").strip().lower()
        if resp in ("s", "sim", "y", "yes"):
            target = out_dir if out_dir else \
                (ok[0].parent if len(ok) == 1 else Path("./saida"))
            subprocess.run(["open", str(target.resolve())], check=False)

    return 0 if not failed else 2


