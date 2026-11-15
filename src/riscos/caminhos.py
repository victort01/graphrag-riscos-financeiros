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
WHERE all(r IN relationships(p) WHERE r.empresa_id=$empresa AND r.periodo=$periodo
      AND coalesce(r.vigente,true)=true AND r.declaracao_id IN $declaracoes_permitidas)
RETURN [n IN nodes(p) | {id:n.id,nome:n.nome,rotulos:labels(n)}] AS nos,
       [r IN relationships(p) | {id:r.declaracao_id,tipo:type(r),origem:startNode(r).id,
          destino:endNode(r).id,periodo:r.periodo,empresa_id:r.empresa_id}] AS relacoes,
       length(p) AS saltos,$escopo AS escopo
ORDER BY saltos DESC,fim.id LIMIT 12""" % "|".join(RELACOES)


def sem_prefixos_redundantes(caminhos):
    unicos = {}
    for caminho in caminhos:
        chave = (caminho.get("escopo"), tuple(r["id"] for r in caminho["relacoes"]))
        unicos.setdefault(chave, caminho)
    return [c for (escopo, ids), c in unicos.items() if not any(
        outro_escopo == escopo and len(outros) > len(ids) and outros[:len(ids)] == ids
        for outro_escopo, outros in unicos)]


def enriquecer(pergunta, recuperacao, banco=None):
    banco = banco or Banco()
    ids = [t["id"] for t in recuperacao["trechos"]]
    grupos = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)-[:REFERE_SE_A]->(e:Empresa)
        WHERE t.id IN $ids AND coalesce(d.vigente,true)=true
        MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(origem:Trecho)-[:PERTENCE_A]->(d)
        RETURN DISTINCT e.id AS inicio,e.empresa_id AS empresa,c.periodo AS periodo,
          coalesce(c.escopo,'nao_especificado') AS escopo,
          CASE WHEN c.escopo IN ['controladora','consolidado'] THEN '' ELSE origem.id END AS trecho_escopo
        ORDER BY inicio,periodo,escopo,trecho_escopo""", {"ids": ids})
    caminhos, consultas = [], []
    termos = palavras(pergunta)
    for grupo in grupos:
        # Sem qualificação jurídica explícita, o trecho é o limite conservador:
        # uma classe de dívida não autoriza ligar fatos de blocos independentes.
        permitidas = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)-[:PERTENCE_A]->(d:Documento)
            WHERE c.empresa_id=$empresa AND c.periodo=$periodo AND coalesce(d.vigente,true)=true
              AND coalesce(c.escopo,'nao_especificado')=$escopo
              AND ($trecho_escopo='' OR t.id=$trecho_escopo)
            RETURN c.id AS id ORDER BY id""", grupo)
        grupo = {**grupo, "declaracoes_permitidas": [d["id"] for d in permitidas]}
        entidades = banco.consultar("""MATCH (a:Entidade)-[r]->(b:Entidade)
            WHERE r.empresa_id=$empresa AND r.periodo=$periodo AND coalesce(r.vigente,true)=true
              AND r.declaracao_id IN $declaracoes_permitidas
            UNWIND [a,b] AS n RETURN DISTINCT n.id AS id,n.nome AS nome,n.aliases AS aliases""", grupo)
        alvos = [(len(termos & palavras(e["nome"] + " " + " ".join(e["aliases"] or []))), e["id"])
                 for e in entidades if e["id"] != grupo["inicio"]]
        destinos = [id_ for pontos, id_ in sorted(alvos, key=lambda a: (-a[0], a[1])) if pontos > 0][:12]
        origem_destinos = "termos_da_pergunta"
        if not destinos:
            sementes = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)
                MATCH (c)-[:OBJETO]->(n:Entidade)
                WHERE t.id IN $ids AND c.empresa_id=$empresa AND c.periodo=$periodo
                  AND c.id IN $declaracoes_permitidas
                RETURN DISTINCT n.id AS id ORDER BY id LIMIT 12""", {**grupo, "ids": ids})
            destinos = [n["id"] for n in sementes]
            origem_destinos = "declaracoes_recuperadas"
        if not destinos:
            continue
        parametros = {**grupo, "destinos": destinos, "origem_destinos": origem_destinos}
        encontrados = banco.consultar(CONSULTA_CAMINHOS, parametros)
        caminhos.extend(encontrados)
        consultas.append({"cypher": CONSULTA_CAMINHOS, "parametros": parametros})
    antes_compactacao = len(caminhos)
    caminhos = sem_prefixos_redundantes(caminhos)
    for indice, caminho in enumerate(caminhos, 1):
        caminho["id"] = f"C{indice}"
    declaracoes = list(dict.fromkeys(r["id"] for p in caminhos for r in p["relacoes"]))
    evidencias = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)-[:PERTENCE_A]->(d:Documento)
        MATCH (d)-[:REFERE_SE_A]->(em:Empresa)
        WHERE c.id IN $ids AND coalesce(d.vigente,true)=true RETURN c.id AS declaracao_id,c.predicado AS predicado,
        c.evidencia AS citacao,c.condicoes AS condicoes,c.escopo AS escopo,
        coalesce(c.natureza,'declaracao') AS natureza,coalesce(c.polaridade,'afirmativa') AS polaridade,
        coalesce(c.tratamento_contabil,'nao_identificado') AS tratamento_contabil,
        c.empresa_id AS empresa_id,em.id AS empresa_canonica_id,c.periodo AS periodo,
        t.id AS trecho_id,t.texto AS texto,t.pagina_inicio AS pagina_inicio,t.pagina_fim AS pagina_fim,
        d.id AS documento_id,d.empresa AS empresa,d.url AS url,d.versao AS versao,
        d.data_recebimento_cvm AS data_recebimento_cvm,
        [(dc:Declaracao)-[:EVIDENCIADA_POR]->(t) | dc.escopo] AS escopos
        ORDER BY declaracao_id""", {"ids": declaracoes})
    adicionais = list(dict.fromkeys(e["trecho_id"] for e in evidencias if e["trecho_id"] not in ids))
    return {"caminhos": caminhos, "evidencias": evidencias, "trechos_adicionais": adicionais,
            "rastreio": {"algoritmo": "shortestPath dirigido, por empresa/entidade, período e escopo, até 4 saltos",
                         "regra_escopo": "Não mistura controladora/consolidado; escopo não especificado exige relações do mesmo trecho.",
                         "compactacao": {"antes": antes_compactacao, "depois": len(caminhos),
                            "regra": "Duplicatas e prefixos com as mesmas arestas são cobertos pelo caminho maior."},
                         "consultas": consultas, "trechos_antes": ids,
                         "trechos_depois": list(dict.fromkeys(ids + adicionais))}}
