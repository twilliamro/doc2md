doc2md/
├── main.py                 # ponto de entrada (enxuto)
├── requirements.txt
├── doc2md.spec             # build do executável (PyInstaller)
└── doc2md/                 # pacote com a lógica
    ├── __init__.py
    ├── config.py           # constantes e tipos suportados
    ├── cli.py              # interface com o usuário (banner, interativo, orquestração)
    ├── inputs.py           # resolução de arquivos/pastas/globs/URLs
    ├── net.py              # download de URLs (Dropbox, Drive, SSL)
    ├── converters.py       # conversão de documentos (markitdown, LibreOffice)
    ├── images.py           # extração de imagens .png
    └── normalize.py        # normalização pós-conversão de EPUB (v2)

Uso
---
  doc2md Livro.pdf              # converte para ./saida/Livro/md/Livro.md
  doc2md *.epub                 # cada arquivo gera sua própria pasta ./saida/<origem>/md
  doc2md Livro.pdf -o ./pasta   # -o define a pasta FINAL de saída (sem subpastas)
  doc2md                        # sem argumentos, abre o modo interativo

Layout de saída padrão (sem -o), por arquivo de entrada:
  ./saida/<origem>/md/<origem>.md          # Markdown convertido
  ./saida/<origem>/md/assets/<origem>/...  # imagens extraídas (quando houver)
onde <origem> é o nome do arquivo de entrada sem extensão. O caminho é
relativo ao diretório de onde o comando é executado.

Pipeline integrado: doc2md → md2resumo → md2pdf. Este layout é o esperado
pelo md2resumo, que lê ./saida/<origem>/md/<origem>.md para gerar o resumo
do documento.

Normalização pós-conversão (v2)
-------------------------------
EPUBs convertidos pelo markitdown saem sem estrutura: o sumário vira links
soltos para .xhtml internos e os capítulos viram links para Contents.xhtml.
O módulo doc2md/normalize.py corrige isso (doc2md/normalize.py,
função normalize_markdown, aplicada após a extração de imagens):
  1. Bloco de sumário EPUB (≥3 links para ChapterNNN.xhtml) vira um
     "## Índice" Markdown, com as entradas duplicadas agrupadas por
     destino (ex.: "Chapter One" + "Lesson 1: …" viram uma entrada só,
     com âncora no estilo GitHub apontando para o header do capítulo).
  2. Marcadores de capítulo no corpo (linha só com link para
     Contents.xhtml#…) viram headers ATX "# Chapter One" — é o que o
     md2resumo usa para dividir o livro em capítulos.
  3. Imagens quebradas "![](../images/…)" (referências internas do
     arquivo-fonte, nunca resolvidas) são removidas; imagens reais em
     assets/, URLs http(s) e data URIs são mantidas.
A normalização é idempotente e não afeta documentos que não seguem o
padrão de EPUB (metadados **Title:** etc. são preservados).
