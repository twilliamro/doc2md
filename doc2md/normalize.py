"""Normalização pós-conversão de Markdown gerado a partir de EPUB.

O markitdown converte EPUB sem estrutura: o sumário vira links soltos para
arquivos .xhtml internos (que não resolvem fora do EPUB) e os capítulos do
corpo viram marcadores do tipo ``[Chapter One](Contents.xhtml#krch1)``.
O md2resumo precisa de headers ATX (``# Capítulo``) para dividir o livro.

Regras aplicadas, nesta ordem (idempotentes e seguras para não-EPUB):
  a. bloco de sumário EPUB (sequência de ≥3 links para ``ChapterNNN.xhtml``)
     → convertido em ``## Índice`` com âncoras no estilo GitHub;
  b. linha que é só um link para ``Contents.xhtml#...`` → ``# {texto}``;
  c. imagem ``![](../...)`` (referência interna não extraída) → linha removida.
"""

import re
import unicodedata

# link solto cujo destino é um capítulo interno do EPUB (sumário)
_RE_TOC_LINK = re.compile(r"^\[(.+?)\]\([^)]*Chapter\d+\.x?html#[^)]+\)\s*$")
# marcador de capítulo no corpo do texto
_RE_CHAPTER_MARKER = re.compile(r"^\[(.+?)\]\([^)]*Contents\.x?html#[^)]+\)\s*$")
# imagem quebrada: destino relativo "subindo" (../), nunca resolvido fora do EPUB
_RE_BROKEN_IMG = re.compile(r"^!\[[^\]]*\]\(\.\./[^)]+\)\s*$")

_MIN_TOC_ENTRIES = 3  # mínimo de links para caracterizar um bloco de sumário


def _slug(texto: str) -> str:
    """Slug estilo GitHub: minúsculas, pontuação removida, espaços→hífens.

    Mantém letras acentuadas (``str.isalnum()`` as cobre).
    """
    t = unicodedata.normalize("NFC", texto.lower())
    t = "".join(c for c in t if c.isalnum() or c in " -")
    return "-".join(t.split())


def _destino(linha: str) -> str:
    """Extrai o destino ``(…)`` de uma linha que é só um link."""
    return linha[linha.index("](") + 2:linha.rindex(")")]


def _texto_link(linha: str, match: re.Match) -> str:
    """Extrai o texto ``[…]`` de uma linha que é só um link."""
    return match.group(1)


def _converter_indice(linhas: list[str]) -> tuple[list[str], bool]:
    """Regra (a): blocos de sumário EPUB viram ``## Índice``.

    Um bloco é uma sequência maximal de linhas em que toda linha não vazia
    casa :data:`_RE_TOC_LINK` (linhas em branco entre as entradas são
    absorvidas pelo bloco) e há pelo menos ``_MIN_TOC_ENTRIES`` links.
    As entradas são agrupadas por destino (o par ``Chapter One`` +
    ``Lesson 1: …`` aponta para o mesmo ``#kchN`` vira uma única entrada
    ``- [Chapter One — Lesson 1: …](#chapter-one)``).
    """
    out: list[str] = []
    i, achou = 0, False
    while i < len(linhas):
        if not _RE_TOC_LINK.match(linhas[i]):
            out.append(linhas[i])
            i += 1
            continue
        # achou candidato: mede o bloco maximal (linha vazia ou link de capítulo)
        j = i
        while j < len(linhas) and (not linhas[j].strip()
                                   or _RE_TOC_LINK.match(linhas[j])):
            j += 1
        entradas = [l for l in linhas[i:j] if l.strip()]
        if len(entradas) < _MIN_TOC_ENTRIES:
            out.extend(linhas[i:j])
            i = j
            continue
        # agrupa por destino, preservando a ordem de primeira aparição
        grupos: dict[str, list[str]] = {}
        for linha in entradas:
            m = _RE_TOC_LINK.match(linha)
            grupos.setdefault(_destino(linha), []).append(_texto_link(linha, m))
        out.append("## Índice")
        out.append("")
        for dest, textos in grupos.items():
            principal = textos[0]
            out.append(f"- [{' — '.join(textos)}](#{_slug(principal)})")
        out.append("")
        achou = True
        i = j
    return out, achou


def normalize_markdown(texto: str) -> tuple[str, str]:
    """Normaliza o Markdown convertido de um EPUB.

    Retorna ``(texto_normalizado, detalhe_curto_para_log)``. Idempotente:
    rodar duas vezes produz o mesmo resultado (o índice gerado é uma lista
    de links para âncoras locais ``#…``, que não casa nas regex de .xhtml).
    """
    linhas = texto.split("\n")  # split simples preserva \n finais ao remontar

    linhas, indice = _converter_indice(linhas)

    n_capitulos = 0  # regra (b): marcadores de capítulo no corpo viram H1
    for k, linha in enumerate(linhas):
        m = _RE_CHAPTER_MARKER.match(linha)
        if m:
            linhas[k] = f"# {m.group(1)}"
            n_capitulos += 1

    n_imgs = 0  # regra (c): remove imagens com destino ../ (nunca resolvidas)
    limpas = []
    for linha in linhas:
        if _RE_BROKEN_IMG.match(linha):
            n_imgs += 1
        else:
            limpas.append(linha)
    linhas = limpas

    partes = []
    if n_capitulos:
        partes.append(f"{n_capitulos} capítulo(s)")
    if indice:
        partes.append("índice gerado")
    if n_imgs:
        partes.append(f"{n_imgs} imagem(ns) quebrada(s) removida(s)")
    return "\n".join(linhas), ", ".join(partes)
