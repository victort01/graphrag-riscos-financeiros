"""Compara anotações independentes, sem confundir concordância com acerto."""
import re
from .esquema import ROTULOS, RELACOES
from .identidade import normalizar


def validar(revisao):
    if revisao.get("estado") != "revisado" or not revisao.get("revisor", "").strip():
        raise ValueError("A revisão precisa estar concluída e identificar o revisor.")
    amostras = revisao["amostras"]
    if not amostras or len({a["id"] for a in amostras}) != len(amostras):
        raise ValueError("A revisão precisa de amostras com IDs únicos.")
    for amostra in amostras:
        if amostra["estado"] not in {"revisado", "rejeitado"}:
            raise ValueError("Há excerto pendente: " + amostra["id"])
        if amostra["estado"] == "rejeitado" and not amostra.get("observacoes", "").strip():
            raise ValueError("A rejeição exige justificativa: " + amostra["id"])


def rotulos(amostra):
    mencoes = set()
    for tipo, superficie in amostra["mencoes"]:
        if tipo not in ROTULOS or not superficie:
            raise ValueError("Tipo ou superfície de menção inválida em " + amostra["id"])
        ocorrencias = list(re.finditer(re.escape(superficie), amostra["texto"], re.I))
        if not ocorrencias:
            raise ValueError("Menção ausente do excerto: " + superficie)
        mencoes.update((tipo, m.start(), m.end()) for m in ocorrencias)
    relacoes = set()
    for sujeito, predicado, objeto in amostra["relacoes"]:
        if predicado not in RELACOES or not sujeito.strip() or not objeto.strip():
            raise ValueError("Tripla inválida em " + amostra["id"])
        relacoes.add(tuple(normalizar(p) for p in (sujeito, predicado, objeto)))
    return {"ner": mencoes, "re": relacoes}


def comparar(primeira, segunda):
    validar(primeira)
    validar(segunda)
    if normalizar(primeira["revisor"]) == normalizar(segunda["revisor"]):
        raise ValueError("A comparação exige dois revisores identificados separadamente.")
    if primeira["sha256_selecao"] != segunda["sha256_selecao"]:
        raise ValueError("As revisões usam seleções diferentes.")
    pares = {a["id"]: a for a in segunda["amostras"]}
    if set(pares) != {a["id"] for a in primeira["amostras"]}:
        raise ValueError("As revisões contêm excertos diferentes.")
    totais = {"ner": [0, 0, 0], "re": [0, 0, 0]}
    casos, rejeitados = [], []
    for amostra in primeira["amostras"]:
        outra = pares[amostra["id"]]
        for campo in ("documento_id", "pagina", "sha256_pdf", "texto"):
            if amostra[campo] != outra[campo]:
                raise ValueError("Fontes ou textos divergentes em " + amostra["id"])
        if "rejeitado" in {amostra["estado"], outra["estado"]}:
            rejeitados.append({"id": amostra["id"], "motivos": [amostra["observacoes"], outra["observacoes"]]})
            continue
        a, b = rotulos(amostra), rotulos(outra)
        caso = {"id": amostra["id"]}
        for tipo in totais:
            totais[tipo] = [total + parcela for total, parcela in zip(totais[tipo], (len(a[tipo] & b[tipo]), len(a[tipo]), len(b[tipo])))]
            caso[tipo] = {"somente_revisor_1": sorted(a[tipo]-b[tipo]), "somente_revisor_2": sorted(b[tipo]-a[tipo])}
        casos.append(caso)
    metricas = {}
    for tipo, (comuns, n1, n2) in totais.items():
        metricas[tipo] = {"itens_comuns": comuns, "itens_revisor_1": n1, "itens_revisor_2": n2,
            "f1_concordancia": 2*comuns/(n1+n2) if n1+n2 else None,
            "jaccard": comuns/(n1+n2-comuns) if n1+n2-comuns else None}
    return {"uso": primeira["uso"], "revisores": [primeira["revisor"], segunda["revisor"]],
        "amostras_comparadas": len(casos), "amostras_rejeitadas": rejeitados,
        "metricas_concordancia": metricas, "divergencias": casos,
        "interpretacao": "Concordância de rótulos positivos por NER/RE, não acurácia contra um gabarito nem kappa. Ambos vazios produzem null. Rejeições são relatadas separadamente."}
