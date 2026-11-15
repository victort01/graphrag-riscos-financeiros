import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.config import ROOT
from riscos.revisao import comparar


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compara duas revisões humanas concluídas, mantendo as divergências.")
    parser.add_argument("primeira", type=Path)
    parser.add_argument("segunda", type=Path)
    parser.add_argument("--saida", type=Path, default=ROOT / "data/reports/comparacao-revisoes.json")
    args = parser.parse_args()
    try:
        resultado = comparar(*(json.loads(p.read_text(encoding="utf-8")) for p in (args.primeira, args.segunda)))
    except (ValueError, KeyError) as erro:
        parser.error(str(erro))
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(resultado["metricas_concordancia"], ensure_ascii=False, indent=2))
