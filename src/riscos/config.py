"""Configuração local com precedência para variáveis do ambiente."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ambiente():
    valores = {}
    arquivo = ROOT / ".env"
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8-sig").splitlines():
            if linha.strip() and not linha.lstrip().startswith("#"):
                chave, separador, valor = linha.partition("=")
                if separador:
                    valores[chave.strip()] = valor.strip()
    valores.update(os.environ)
    return valores
