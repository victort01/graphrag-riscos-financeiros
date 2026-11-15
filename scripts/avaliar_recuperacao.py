"""Ablation de recuperação. Não mede correção de respostas nem alucinação."""
import argparse
import hashlib
import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.recuperacao import recuperar
from riscos.caminhos import enriquecer
from riscos.respostas import montar_contexto
from riscos.config import ROOT, ambiente
from riscos.embeddings import IDENTIFICADOR
from riscos.versao import identificar
from riscos.banco import Banco
from riscos.ingestao import PIPELINE


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).split())


def recall(trechos, esperadas):
    if not esperadas:
        return None
    acertos = sum(any(t["documento_id"] == e["documento_id"]
                     and t["pagina_inicio"] <= e["pagina"] <= t["pagina_fim"]
                     and normalizar(e["termo"]) in normalizar(t["texto"]) for t in trechos) for e in esperadas)
    return acertos / len(esperadas)


def medir(id_, metodo, busca, grafo, esperadas):
    contexto = montar_contexto(busca, grafo)
    candidatos = {t["id"]: t for t in busca["trechos"]}
    for evidencia in grafo["evidencias"]:
        candidatos.setdefault(evidencia["trecho_id"], evidencia)
    return {"pergunta_id": id_, "metodo": metodo, "erro": None,
            "recall_candidatos": recall(list(candidatos.values()), esperadas),
            "recall_contexto": recall(list(contexto["fontes"].values()), esperadas),
            "fontes_enviadas": len(contexto["fontes"]), "caminhos_enviados": len(contexto["caminhos"]),
            "caracteres_contexto": len(json.dumps(contexto, ensure_ascii=False)),
            "contexto": contexto, "rastreio": busca["rastreio"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conjunto", type=Path, default=ROOT / "data/perguntas-smoke-recuperacao.json")
    parser.add_argument("--saida", type=Path, default=ROOT / "data/reports/avaliacao-recuperacao-smoke.json")
    args = parser.parse_args()
    conjunto = json.loads(args.conjunto.read_text(encoding="utf-8"))
    manifesto = ROOT / "data/manifesto.json"
    ids_corpus = [d["id"] for d in json.loads(manifesto.read_text(encoding="utf-8"))["documentos"]]
    corpus = Banco().consultar("""MATCH (d:Documento) WHERE d.id IN $ids
        RETURN d.id AS id,d.sha256 AS sha256,d.pipeline AS pipeline,d.versao AS versao,
        coalesce(d.vigente,true) AS vigente ORDER BY id""", {"ids": ids_corpus})
    if {d["id"] for d in corpus} != set(ids_corpus) or any(d["pipeline"] != PIPELINE for d in corpus):
        parser.error("Publique todo o manifesto com o pipeline atual antes da comparação.")
    indexacao = Banco().consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE d.id IN $ids AND coalesce(d.vigente,true)=true AND t.natureza='narrativa' AND t.recorte=false
        RETURN count(t) AS elegiveis,sum(CASE WHEN t.modelo_embedding=$modelo THEN 1 ELSE 0 END) AS indexados""",
        {"ids": ids_corpus, "modelo": IDENTIFICADOR})[0]
    if indexacao["elegiveis"] != indexacao["indexados"]:
        parser.error("O índice vetorial não cobre todos os trechos elegíveis. Execute scripts/indexar.py antes de comparar.")
    relatorio = {"uso": conjunto["uso"], "estado": "em_execucao", "etapa_em_andamento": None,
                 "data_utc": datetime.now(timezone.utc).isoformat(),
                 "sha256_conjunto": hashlib.sha256(args.conjunto.read_bytes()).hexdigest(),
                 "sha256_manifesto": hashlib.sha256(manifesto.read_bytes()).hexdigest(),
                 "versao_execucao": identificar(), "corpus": corpus, "cobertura_indice": indexacao,
                 "modelo_embedding": IDENTIFICADOR, "modelo_llm": ambiente().get("LLM_ARTIFACT", "não registrado"),
                 "orcamento_contexto_caracteres": 3500, "linhas": [],
                 "nota_latencia": "Tempos descritivos; incluem aquecimento e caches. Grafo reutiliza os candidatos híbridos para isolar o algoritmo."}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    vazio = {"caminhos": [], "evidencias": []}
    for pergunta in conjunto["perguntas"]:
        hibrida = None
        for metodo in ("vetorial", "hibrido", "grafo"):
            relatorio["etapa_em_andamento"] = {"pergunta_id": pergunta["id"], "metodo": metodo}
            args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
            inicio = perf_counter()
            try:
                if metodo != "grafo":
                    busca = recuperar(pergunta["pergunta"], pergunta["empresas"], pergunta["periodo"], somente_vetor=metodo == "vetorial")
                    if metodo == "hibrido":
                        hibrida = busca
                else:
                    if hibrida is None:
                        raise ValueError("A recuperação híbrida falhou; comparação do algoritmo indisponível.")
                    busca = hibrida
                grafo = enriquecer(pergunta["pergunta"], busca) if metodo == "grafo" else vazio
                linha = medir(pergunta["id"], metodo, busca, grafo, pergunta["evidencias"])
            except Exception as erro:
                linha = {"pergunta_id": pergunta["id"], "metodo": metodo, "erro": str(erro),
                         "recall_candidatos": None, "recall_contexto": None}
            linha["tempo_etapa_segundos"] = round(perf_counter()-inicio, 3)
            relatorio["linhas"].append(linha)
            relatorio["etapa_em_andamento"] = None
            args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
            print(pergunta["id"], metodo, "erro" if linha["erro"] else "ok", flush=True)
    relatorio["estado"] = "concluida_com_falhas" if any(l["erro"] for l in relatorio["linhas"]) else "concluida"
    args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
