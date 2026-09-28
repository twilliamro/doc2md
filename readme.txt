doc2md/
├── main.py                 # ponto de entrada (enxuto)
├── requirements.txt
└── doc2md/                 # pacote com a lógica
    ├── __init__.py
    ├── config.py           # constantes e tipos suportados
    ├── cli.py              # interface com o usuário (banner, interativo, orquestração)
    ├── inputs.py           # resolução de arquivos/pastas/globs/URLs
    ├── net.py              # download de URLs (Dropbox, Drive, SSL)
    ├── converters.py       # conversão de documentos (markitdown, LibreOffice)
    └── images.py           # extração de imagens .png