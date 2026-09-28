"""Constantes e tipos de arquivo suportados."""

SUPPORTED = {".pdf", ".epub", ".docx", ".pptx", ".html", ".htm",
             ".txt", ".csv", ".md"}
VIA_LIBREOFFICE = {".doc", ".ppt"}
MIN_PNG_BYTES = 10 * 1024  # ignora imagens < 10 KB (ícones, bullets)

CONTENT_TYPE_MAP = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/msword": ".doc",
    "application/vnd.ms-powerpoint": ".ppt",
    "text/html": ".html",
    "text/plain": ".txt",
    "text/csv": ".csv",
}
