"""Seleciona caminhos financeiros mínimos antes de montar o contexto de resposta."""
import re
import unicodedata
from .banco import Banco
from .esquema import RELACOES


def palavras(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    ignoradas = {"que", "quais", "como", "dos", "das", "para", "uma", "com", "sua", "seu",
                 "empresa", "exposicao", "declarada", "financeira", "financeiro", "protecao"}
    return set(re.findall(r"[a-z]{3,}", texto)) - ignoradas


CONSULTA_CAMINHOS = """MATCH (inicio:Empresa {id:$inicio}), (fim:Entidade)
WHERE fim.id IN $destinos AND fim.id<>inicio.id
MATCH p=shortestPath((inicio)-[:%s*1..4]->(fim))
WHERE all(r IN relationships(p) WHERE r.empresa_id=$empresa AND r.periodo=$periodo AND coalesce(r.vigente,true)=true)
RETURN [n IN nodes(p) | {id:n.id,nome:n.nome,rotulos:labels(n)}] AS nos,
       [r IN relationships(p) | {id:r.declaracao_id,tipo:type(r),origem:startNode(r).id,
          destino:endNode(r).id,periodo:r.periodo,empresa_id:r.empresa_id}] AS relacoes,
       length(p) AS saltos
ORDER BY saltos DESC,fim.id LIMIT 12""" % "|".join(RELACOES)


def enriquecer(pergunta, recuperacao, banco=None):
    banco = banco or Banco()
    ids = [t["id"] for t in recuperacao["trechos"]]
    grupos = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)-[:REFERE_SE_A]->(e:Empresa)
        WHERE t.id IN $ids AND coalesce(d.vigente,true)=true
        RETURN DISTINCT e.id AS inicio,e.empresa_id AS empresa,d.data_referencia AS periodo""", {"ids": ids})
    caminhos, consultas = [], []
    termos = palavras(pergunta)
    for grupo in grupos:
        entidades = banco.consultar("""MATCH (a:Entidade)-[r]->(b:Entidade)
            WHERE r.empresa_id=$empresa AND r.periodo=$periodo AND coalesce(r.vigente,true)=true
            UNWIND [a,b] AS n RETURN DISTINCT n.id AS id,n.nome AS nome,n.aliases AS aliases""", grupo)
        alvos = [(len(termos & palavras(e["nome"] + " " + " ".join(e["aliases"] or []))), e["id"])
                 for e in entidades if e["id"] != grupo["inicio"]]
        destinos = [id_ for pontos, id_ in sorted(alvos, key=lambda a: (-a[0], a[1])) if pontos > 0][:12]
        origem_destinos = "termos_da_pergunta"
        if not destinos:
            sementes = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)
                MATCH (c)-[:OBJETO]->(n:Entidade)
                WHERE t.id IN $ids AND c.empresa_id=$empresa AND c.periodo=$periodo
                RETURN DISTINCT n.id AS id ORDER BY id LIMIT 12""", {**grupo, "ids": ids})
            destinos = [n["id"] for n in sementes]
            origem_destinos = "declaracoes_recuperadas"
        if not destinos:
            continue
        parametros = {**grupo, "destinos": destinos, "origem_destinos": origem_destinos}
        encontrados = banco.consultar(CONSULTA_CAMINHOS, parametros)
        caminhos.extend(encontrados)
        consultas.append({"cypher": CONSULTA_CAMINHOS, "parametros": parametros})
    for indice, caminho in enumerate(caminhos, 1):
        caminho["id"] = f"C{indice}"
    declaracoes = list(dict.fromkeys(r["id"] for p in caminhos for r in p["relacoes"]))
    evidencias = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE c.id IN $ids AND coalesce(d.vigente,true)=true RETURN c.id AS declaracao_id,c.predicado AS predicado,
        c.evidencia AS citacao,c.condicoes AS condicoes,c.escopo AS escopo,
        c.empresa_id AS empresa_id,c.periodo AS periodo,
        t.id AS trecho_id,t.texto AS texto,t.pagina_inicio AS pagina_inicio,t.pagina_fim AS pagina_fim,
        d.id AS documento_id,d.empresa AS empresa,d.url AS url,d.versao AS versao,
        d.data_recebimento_cvm AS data_recebimento_cvm ORDER BY declaracao_id""", {"ids": declaracoes})
    adicionais = list(dict.fromkeys(e["trecho_id"] for e in evidencias if e["trecho_id"] not in ids))
    return {"caminhos": caminhos, "evidencias": evidencias, "trechos_adicionais": adicionais,
            "rastreio": {"algoritmo": "shortestPath dirigido, por par empresa/entidade, até 4 saltos",
                         "consultas": consultas, "trechos_antes": ids,
                         "trechos_depois": list(dict.fromkeys(ids + adicionais))}}
