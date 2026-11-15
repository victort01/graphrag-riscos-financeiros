"""Consulta auditável, com recuperação híbrida e enriquecimento por caminhos."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.recuperacao import recuperar
from riscos.caminhos import enriquecer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pergunta")
    parser.add_argument("--empresa", action="append", default=[], help="CNPJ com 14 dígitos")
    parser.add_argument("--periodo", default="", help="AAAA-12-31")
    parser.add_argument("--sem-cypher-llm", action="store_true")
    parser.add_argument("--sem-caminhos", action="store_true")
    parser.add_argument("--salvar", type=Path)
    args = parser.parse_args()
    empresas = ["empresa:" + e for e in args.empresa]
    resultado = recuperar(args.pergunta, empresas, args.periodo, not args.sem_cypher_llm)
    if not args.sem_caminhos:
        resultado["grafo"] = enriquecer(args.pergunta, resultado)
    saida = json.dumps(resultado, ensure_ascii=False, indent=2)
    if args.salvar:
        args.salvar.parent.mkdir(parents=True, exist_ok=True)
        args.salvar.write_text(saida, encoding="utf-8")
    print(saida)
