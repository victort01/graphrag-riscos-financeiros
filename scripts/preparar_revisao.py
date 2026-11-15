"""Prepara revisão cega das previsões, sem preencher julgamentos humanos."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.config import ROOT


def preparar():
    origem = ROOT / "data/anotacoes-desenvolvimento-extracao.json"
    anotacoes = json.loads(origem.read_text(encoding="utf-8"))
    fontes = {f["id"]: f for f in json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))["documentos"]}
    amostras = []
    for indice, anotacao in enumerate(anotacoes["amostras"], 1):
        fonte = fontes[anotacao["documento_id"]]
        documento = json.loads((ROOT / "data/processed" / (fonte["id"] + ".json")).read_text(encoding="utf-8"))
        if documento["sha256"] != fonte["sha256"]:
            raise ValueError("PDF e texto processado divergentes: " + fonte["id"])
        pagina = " ".join(documento["paginas"][anotacao["pagina"]-1]["texto"].split())
        inicio = pagina.casefold().index(anotacao["ancora"].casefold())
        fim = re.search(r"\.\s+(?=[A-ZÀ-Ü])", pagina[inicio:])
        texto = pagina[inicio:inicio+fim.start()+1] if fim else pagina[inicio:]
        amostras.append({"id": f"R{indice:02}", "documento_id": fonte["id"],
            "pagina": anotacao["pagina"], "url": fonte["url"] + "#page=" + str(anotacao["pagina"]),
            "sha256_pdf": fonte["sha256"], "ancora": anotacao["ancora"], "texto": texto,
            "estado": "pendente", "mencoes": [], "relacoes": [], "observacoes": ""})
    return {"uso": "Revisão humana da amostra de desenvolvimento; não constitui teste reservado.",
        "origem_amostragem": "Excertos previamente selecionados com assistência de IA e usados para ajustar regras.",
        "sha256_selecao": hashlib.sha256(origem.read_bytes()).hexdigest(),
        "revisor": "", "estado": "pendente", "amostras": amostras}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--saida", type=Path, default=ROOT / "data/revisao-extracao")
    args = parser.parse_args()
    destinos = [args.saida / f"revisor-{i}.json" for i in (1, 2)]
    if any(p.exists() for p in destinos):
        parser.error("A pasta já contém uma revisão. Use outra pasta para não sobrescrever anotações humanas.")
    pacote = preparar()
    args.saida.mkdir(parents=True, exist_ok=True)
    for destino in destinos:
        destino.write_text(json.dumps(pacote, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Dois formulários com {len(pacote['amostras'])} excertos, sem rótulos humanos preenchidos.")
