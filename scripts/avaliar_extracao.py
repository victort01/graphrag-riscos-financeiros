"""Avalia menções com offsets e relações na amostra de desenvolvimento anotada."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.config import ROOT
from riscos.extracao import extrair, VERSAO
from riscos.identidade import normalizar


def metrica(acertos, previstos, esperados):
    precisao = acertos / previstos if previstos else 0
    revocacao = acertos / esperados if esperados else 0
    return {"verdadeiros_positivos": acertos, "previstos": previstos, "esperados": esperados,
            "precisao": precisao, "revocacao": revocacao,
            "f1": 2*precisao*revocacao/(precisao+revocacao) if precisao+revocacao else 0}


if __name__ == "__main__":
    fontes = {f["id"]: f for f in json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))["documentos"]}
    anotacoes = json.loads((ROOT / "data/anotacoes-desenvolvimento-extracao.json").read_text(encoding="utf-8"))
    totais = {"ner": [0, 0, 0], "re": [0, 0, 0]}
    casos = []
    for amostra in anotacoes["amostras"]:
        fonte = fontes[amostra["documento_id"]]
        paginas = json.loads((ROOT / "data/processed" / (fonte["id"] + ".json")).read_text(encoding="utf-8"))["paginas"]
        texto = " ".join(paginas[amostra["pagina"]-1]["texto"].split())
        inicio = texto.casefold().index(amostra["ancora"].casefold())
        fim = re.search(r"\.\s+(?=[A-ZÀ-Ü])", texto[inicio:])
        sentenca = texto[inicio:inicio+fim.start()+1] if fim else texto[inicio:]
        trecho = {"id": "avaliacao", "sha256": fonte["sha256"], "texto": sentenca, "natureza": "narrativa", "recorte": False}
        entidades, mencoes, relacoes = extrair(trecho, fonte)
        mapa = {e["id"]: e for e in entidades}
        ner_predito = {(mapa[m["entidade_id"]]["tipo"], m["inicio"], m["fim"]) for m in mencoes}
        ner_esperado = set()
        for tipo, superficie in amostra["mencoes"]:
            ocorrencias = list(re.finditer(re.escape(superficie), sentenca, re.I))
            if not ocorrencias:
                raise ValueError(f"Menção anotada ausente da fonte: {superficie}")
            ner_esperado.update((tipo, m.start(), m.end()) for m in ocorrencias)
        def nome(identificador):
            return "@empresa" if mapa[identificador]["tipo"] == "Empresa" else mapa[identificador]["nome"]
        re_predito = {tuple(normalizar(x) for x in (nome(d["sujeito_id"]), d["predicado"], nome(d["objeto_id"]))) for d in relacoes}
        re_esperado = {tuple(normalizar(x) for x in tripla) for tripla in amostra["relacoes"]}
        for chave, previsto, esperado in [("ner", ner_predito, ner_esperado), ("re", re_predito, re_esperado)]:
            totais[chave][0] += len(previsto & esperado)
            totais[chave][1] += len(previsto)
            totais[chave][2] += len(esperado)
        casos.append({"documento": fonte["id"], "pagina": amostra["pagina"], "ancora": amostra["ancora"],
                      "ner_faltantes": sorted(ner_esperado-ner_predito), "ner_extras": sorted(ner_predito-ner_esperado),
                      "re_faltantes": sorted(re_esperado-re_predito), "re_extras": sorted(re_predito-re_esperado)})
    resultado = {"extrator": VERSAO, "metodo": anotacoes["metodo"], "amostras": len(casos),
                 "metricas": {chave: metrica(*valores) for chave, valores in totais.items()}, "casos": casos}
    (ROOT / "data/avaliacao-extracao-desenvolvimento.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(resultado["metricas"], ensure_ascii=False, indent=2))
