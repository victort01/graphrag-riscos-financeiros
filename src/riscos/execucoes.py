"""Arquivo local das execuções, para auditoria e retomada após desconexões."""
import json
from datetime import datetime, timezone
from uuid import uuid4
from .config import ROOT


PASTA = ROOT / "data" / "reports" / "execucoes"


def salvar(resultado, pasta=PASTA):
    pasta.mkdir(parents=True, exist_ok=True)
    nome = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + uuid4().hex + ".json"
    arquivo = pasta / nome
    temporario = arquivo.with_suffix(".tmp")
    temporario.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(arquivo)
    return arquivo


def carregar_ultima(pasta=PASTA):
    arquivos = sorted(pasta.glob("*.json"), reverse=True)
    if not arquivos:
        return None
    return json.loads(arquivos[0].read_text(encoding="utf-8"))
