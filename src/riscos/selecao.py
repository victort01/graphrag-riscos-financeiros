"""Reordena evidências por conteúdo e conserva fontes equivalentes no rastreio."""
import math
import re
from collections import Counter
from .identidade import normalizar

IGNORADAS = {"como", "qual", "quais", "que", "para", "com", "dos", "das", "uma", "por", "seu", "sua",
             "companhia", "empresa", "empresas", "irani", "klabin", "suzano", "declarou", "declara", "relatorio"}


def termos(texto):
    return set(re.findall(r"[a-z]{3,}", normalizar(texto))) - IGNORADAS


def selecionar(pergunta, candidatos, limite=8):
    consulta = termos(pergunta)
    frequencias = Counter(p for t in candidatos for p in termos(t["texto"]))
    total = len(candidatos)
    grupos, detalhes = {}, []
    for posicao, trecho in enumerate(candidatos):
        palavras = termos(trecho["texto"])
        intersecao = consulta & palavras
        lexical = sum(1 + math.log((total+1)/(frequencias[p]+1)) for p in intersecao)
        especificidade = lexical / math.sqrt(max(len(palavras), 1))
        # Nomes de emissor não tornam educação corporativa evidência financeira.
        # A expressão contábil distingue o tratamento do hedge econômico.
        contabil = bool(re.search(r"hedge accounting|contabilidade de hedge", normalizar(pergunta)))
        if contabil and re.search(r"hedge accounting|contabilidade de hedge", normalizar(trecho["texto"])):
            especificidade += 2
        registro = {**trecho, "pontuacao_evidencia": round(especificidade, 6)}
        chave = (trecho.get("empresa_canonica_id", trecho.get("empresa")), trecho.get("periodo"), normalizar(trecho["texto"]))
        if chave in grupos:
            grupos[chave]["ocorrencias_equivalentes"].append(trecho["id"])
            continue
        registro["ocorrencias_equivalentes"] = [trecho["id"]]
        grupos[chave] = registro
        detalhes.append({"id": trecho["id"], "posicao_rrf": posicao+1, "pontuacao_lexical": registro["pontuacao_evidencia"],
                         "termos_comuns": sorted(intersecao)})
    ordenados = sorted(grupos.values(), key=lambda t: (-t["pontuacao_evidencia"], -t.get("rrf", 0), t["id"]))
    return ordenados[:limite], {"algoritmo": "sobreposição lexical ponderada por frequência nos candidatos; RRF como desempate",
        "duplicatas": [t["ocorrencias_equivalentes"] for t in ordenados if len(t["ocorrencias_equivalentes"])>1],
        "candidatos": detalhes, "selecionados": [t["id"] for t in ordenados[:limite]]}
