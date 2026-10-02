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
    └── images.py           # extração de imagens .png

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
