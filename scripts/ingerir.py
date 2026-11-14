"""Extrai entidades/relações e publica um documento atomicamente no Neo4j."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.config import ROOT
from riscos.ingestao import executar

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", action="append")
    parser.add_argument("--reprocessar", action="store_true")
    parser.add_argument("--somente-preparar", action="store_true")
    args = parser.parse_args()
    fontes = json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))["documentos"]
    if args.id:
        desconhecidos = set(args.id) - {f["id"] for f in fontes}
        if desconhecidos:
            parser.error(f"IDs ausentes do manifesto: {desconhecidos}")
        fontes = [f for f in fontes if f["id"] in args.id]
    for fonte in fontes:
        print(json.dumps(executar(fonte, args.reprocessar, args.somente_preparar), ensure_ascii=False), flush=True)
