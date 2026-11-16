"""Subgrafo Cytoscape com IDs persistentes e evidências retornadas pelo Neo4j."""
import json
from .config import ROOT


def rastrear_nos(resultado):
    caminhos = resultado["grafo"]["caminhos"]
    enviados = {p["id"] for p in resultado["contexto_enviado"]["caminhos"]}
    citados = {id_ for a in resultado["resposta"]["afirmacoes"] for id_ in a.get("caminhos", [])}

    def listar(ids):
        return {n["id"]: n["nome"] for p in caminhos if ids is None or p["id"] in ids for n in p["nos"]}

    fontes = resultado["contexto_enviado"]["fontes"]
    fontes_citadas = {id_ for a in resultado["resposta"]["afirmacoes"] for id_ in a["fontes"]}
    return {"nos_financeiros_recuperados": listar(None), "nos_financeiros_enviados": listar(enviados),
            "nos_financeiros_citados": listar(citados),
            "trechos_enviados": {id_: f["trecho_id"] for id_, f in fontes.items()},
            "trechos_citados": {id_: fontes[id_]["trecho_id"] for id_ in sorted(fontes_citadas)}}


def nos_consultados(resultado):
    """Lista legível dos nós financeiros, do uso mais forte (citado) ao mais fraco (só recuperado)."""
    rastro = rastrear_nos(resultado)
    rotulos = {n["id"]: [r for r in n.get("rotulos", []) if r != "Entidade"]
               for p in resultado["grafo"]["caminhos"] for n in p["nos"]}
    linhas = []
    for id_, nome in rastro["nos_financeiros_recuperados"].items():
        situacao = ("citado na resposta" if id_ in rastro["nos_financeiros_citados"]
                    else "enviado ao modelo" if id_ in rastro["nos_financeiros_enviados"] else "recuperado, fora do contexto")
        linhas.append({"Nó": nome, "Tipo": ", ".join(rotulos.get(id_, [])) or "não registrado", "Situação": situacao, "ID": id_})
    ordem = {"citado na resposta": 0, "enviado ao modelo": 1, "recuperado, fora do contexto": 2}
    return sorted(linhas, key=lambda l: (ordem[l["Situação"]], l["Nó"]))


def cypher_gerado(resultado):
    """Consulta Cypher produzida pelo LLM, ou None quando a variante não a executou."""
    return resultado["recuperacao"]["rastreio"].get("cypher_llm")


def pagina_grafo(resultado):
    evidencias = {e["declaracao_id"]: e for e in resultado["grafo"]["evidencias"]}
    enviados = {p["id"] for p in resultado["contexto_enviado"]["caminhos"]}
    caminhos = [p for p in resultado["grafo"]["caminhos"] if p["id"] in enviados]
    elementos, vistos = [], set()
    for caminho in caminhos:
        for no in caminho["nos"]:
            if no["id"] not in vistos:
                elementos.append({"data": {**no, "label": no["nome"], "empresa": "Empresa" in no["rotulos"]}})
                vistos.add(no["id"])
        for relacao in caminho["relacoes"]:
            if relacao["id"] not in vistos:
                fonte = evidencias[relacao["id"]]
                elementos.append({"data": {**relacao, "source": relacao["origem"], "target": relacao["destino"],
                    "label": relacao["tipo"], "citacao": fonte["citacao"], "pagina": fonte["pagina_inicio"],
                    "url": fonte["url"], "documento": fonte["documento_id"], "trecho_id": fonte["trecho_id"],
                    "escopo": fonte.get("escopo", "nao_especificado")}})
                vistos.add(relacao["id"])
    fontes = resultado["contexto_enviado"]["fontes"]
    afirmacoes = [{"texto": a["texto"], "caminhos": a.get("caminhos", []), "trechos": [fontes[f]["trecho_id"] for f in a["fontes"]]}
                 for a in resultado["resposta"]["afirmacoes"]]
    dados = json.dumps({"elementos": elementos, "afirmacoes": afirmacoes,
                        "caminhos": caminhos}, ensure_ascii=False).replace("<", "\\u003c")
    biblioteca = (ROOT / "ui/vendor/cytoscape.min.js").read_text(encoding="utf-8")
    html = (ROOT / "ui/grafo.html").read_text(encoding="utf-8")
    return html.replace("__BIBLIOTECA__", biblioteca).replace("__DADOS__", dados)
