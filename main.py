#!/usr/bin/env python3
"""Ponto de entrada do doc2md. Toda a lógica está no pacote doc2md/."""
import sys

from doc2md.cli import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        sys.exit(130)



