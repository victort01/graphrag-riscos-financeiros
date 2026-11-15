import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.revisao_respostas import preparar, comparar


def ler(p):
    return json.loads(p.read_text(encoding="utf-8"))


def escrever(p, dados):
    if p.exists():
        raise ValueError("Preserve o arquivo existente; escolha outro destino: " + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preparar lote de revisão ou comparar dois formulários concluídos.")
    modos = parser.add_subparsers(dest="modo", required=True)
    novo = modos.add_parser("preparar")
    novo.add_argument("geracao", type=Path)
    novo.add_argument("pasta", type=Path)
    novo.add_argument("--mapa", type=Path, required=True, help="Arquivo fora dos formulários; omitir dos revisores até a conclusão.")
    comp = modos.add_parser("comparar")
    comp.add_argument("lote", type=Path)
    comp.add_argument("revisor1", type=Path)
    comp.add_argument("revisor2", type=Path)
    args = parser.parse_args()
    if args.modo == "preparar":
        lote, mapa = preparar(ler(args.geracao))
        destinos = [args.pasta/n for n in ("lote.json", "revisor-1.json", "revisor-2.json")]
        if any(p.exists() for p in [*destinos, args.mapa]):
            parser.error("O lote já existe; use uma pasta e um mapa novos.")
        for p in destinos:
            escrever(p, lote)
        escrever(args.mapa, mapa)
        print(f"{len(lote['itens'])} respostas preparadas; revisão humana pendente.")
    else:
        print(json.dumps(comparar(ler(args.revisor1), ler(args.revisor2), ler(args.lote)), ensure_ascii=False, indent=2))
