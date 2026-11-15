import argparse
import json
import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.respostas import responder
from riscos.execucoes import salvar


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("pergunta")
    parser.add_argument("--empresa", action="append", default=[])
    parser.add_argument("--periodo", default="")
    parser.add_argument("--salvar", type=Path)
    args = parser.parse_args()
    resultado = responder(args.pergunta, ["empresa:"+e for e in args.empresa], args.periodo)
    salvar(resultado)
    texto = json.dumps(resultado, ensure_ascii=False, indent=2)
    if args.salvar:
        args.salvar.parent.mkdir(parents=True, exist_ok=True)
        args.salvar.write_text(texto, encoding="utf-8")
    print(json.dumps(resultado["resposta"], ensure_ascii=False, indent=2))
