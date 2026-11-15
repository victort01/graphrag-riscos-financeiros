"""Busca híbrida com filtros de fonte, RRF e Cypher proposto pelo LLM."""
import re
import logging
from time import perf_counter
from .banco import Banco
from .consultas import validar_consulta, TEMPO_CONSULTA_GERADA_MS
from .embeddings import IDENTIFICADOR, codificar
from .llm import gerar_json
from .caminhos import palavras
from .intencao import reconciliar

CAMPOS = """t.id AS id,t.texto AS texto,t.pagina_inicio AS pagina_inicio,t.pagina_fim AS pagina_fim,
d.id AS documento_id,d.empresa AS empresa,e.empresa_id AS empresa_id,e.id AS empresa_canonica_id,
d.data_referencia AS periodo,d.url AS url,d.versao AS versao,
d.data_recebimento_cvm AS data_recebimento_cvm,
[(dc:Declaracao)-[:EVIDENCIADA_POR]->(t) | dc.escopo] AS escopos"""
FILTROS = """MATCH (t)-[:PERTENCE_A]->(d:Documento)-[:REFERE_SE_A]->(e:Empresa)
WHERE ($empresas=[] OR e.id IN $empresas) AND ($periodo='' OR d.data_referencia=$periodo)
AND coalesce(d.vigente,true)=true AND t.natureza='narrativa' AND t.recorte=false"""


def lexical(pergunta):
    ignoradas = {"qual", "quais", "como", "sobre", "para", "dos", "das", "que", "uma", "com", "pelo", "pela", "tem"}
    termos = [t.casefold() for t in re.findall(r"[A-Za-zÀ-ÿ]{3,}", pergunta) if t.casefold() not in ignoradas]
    if any("dólar" in t or "dolar" in t for t in termos):
        termos.extend(["USD", "dólares"])
    return " OR ".join(dict.fromkeys(termos[:18]))


def combinar(listas):
    combinados = {}
    for metodo, linhas in listas:
        for posicao, linha in enumerate(linhas, 1):
            registro = combinados.setdefault(linha["id"], {**linha, "rrf": 0.0, "metodos": []})
            registro["rrf"] += 1 / (60 + posicao)
            registro["metodos"].append(metodo)
    return sorted(combinados.values(), key=lambda l: (-l["rrf"], l["id"]))


def sugerir_predicados(pergunta):
    termos = palavras(pergunta)
    regras = [({"acc", "recebiveis"}, ["TEM_OBRIGACAO", "COMPENSA_VARIACOES_DE"]),
              ({"divida", "dividas", "obrigacoes", "financiamento"}, ["TEM_OBRIGACAO", "DENOMINADO_EM"]),
              ({"dolar", "dolares", "usd", "moeda"}, ["DENOMINADO_EM"]),
              ({"swap", "swaps", "hedge", "instrumentos"}, ["ADOTA_PROTECAO", "PROTEGE", "CONVERTE_DE", "CONVERTE_PARA"]),
              ({"juros", "taxas"}, ["PROTEGE", "SENSIVEL_A", "ADOTA_PROTECAO"]),
              ({"categoria", "classificacao", "enquadramento"}, ["CATEGORIZADA_COMO"])]
    return list(dict.fromkeys(p for conceitos, predicados in regras if termos & conceitos for p in predicados))


def gerar_cypher(pergunta, filtros, banco):
    propriedades = {"cypher": {"type": "string"}}
    schema = {"type": "object", "properties": propriedades, "required": ["cypher"], "additionalProperties": False}
    instrucoes = """Translate the Portuguese question into one read-only Neo4j Cypher query.
Return JSON with a cypher string. All answers must retrieve evidence through this chain:
(c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)-[:PERTENCE_A]->(d:Documento)-[:REFERE_SE_A]->(e:Empresa)
The filters are ($empresas=[] OR e.id IN $empresas) AND ($periodo='' OR d.data_referencia=$periodo).
Also filter coalesce(d.vigente,true)=true to exclude superseded document versions.
Do not add literal company names, IDs or dates. Filters are provided through parameters.
Declaracao.predicado describes a financial statement. Available values:
ADOTA_PROTECAO = adopted hedging instrument; PROTEGE = what the instrument protects;
TEM_OBRIGACAO = company's debt; TEM_RECEITA = company's revenue; TEM_EXPOSICAO = exposure;
DENOMINADO_EM = currency denomination; COMPENSA_VARIACOES_DE = debt offsets receivables;
CONVERTE_DE, CONVERTE_PARA = swap changes currency/index; ASSOCIADA_A, SENSIVEL_A = risk factor.
DECORRE_DE = exposure originates from an obligation or revenue; CATEGORIZADA_COMO = hedge accounting category.
Filter c.predicado using the values relevant to the question.
Example question: Quais instrumentos de proteção a companhia declara?
Example query:
MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)-[:PERTENCE_A]->(d:Documento)-[:REFERE_SE_A]->(e:Empresa)
WHERE ($empresas=[] OR e.id IN $empresas) AND ($periodo='' OR d.data_referencia=$periodo)
AND coalesce(d.vigente,true)=true
AND c.predicado IN ['ADOTA_PROTECAO','PROTEGE']
RETURN DISTINCT t.id AS trecho_id LIMIT 16
Only MATCH, WHERE, RETURN, LIMIT. Always return DISTINCT t.id AS trecho_id LIMIT 16.
"""
    erro = None
    tentativas = []
    for tentativa in range(2):
        resposta = gerar_json(instrucoes, {"pergunta": pergunta, "predicados_sugeridos": sugerir_predicados(pergunta), "erro_anterior": erro,
                                          "consulta_anterior": tentativas[-1]["consulta"] if tentativas else None}, schema, 700)
        consulta = resposta["cypher"]
        try:
            operadores = validar_consulta(banco, consulta, filtros)
            tentativas.append({"consulta": consulta, "erro": None})
            return consulta, operadores, tentativas
        except (RuntimeError, ValueError) as falha:
            erro = str(falha)
            tentativas.append({"consulta": consulta, "erro": erro})
    raise ValueError("Consulta rejeitada após uma tentativa de reparo: " + str(tentativas))


def recuperar(pergunta, empresas=None, periodo="", usar_llm=True, somente_vetor=False):
    inicio = perf_counter()
    empresas, periodo = reconciliar(pergunta, empresas, periodo)
    if periodo and not re.fullmatch(r"20\d{2}-12-31", periodo):
        raise ValueError("O período deve ser o encerramento anual no formato AAAA-12-31.")
    if any(not re.fullmatch(r"empresa:\d{14}", e) for e in empresas or []):
        raise ValueError("Identificador de empresa inválido.")
    banco = Banco()
    filtros = {"empresas": empresas or [], "periodo": periodo}
    documentos = banco.consultar("""MATCH (d:Documento)-[:REFERE_SE_A]->(e:Empresa)
        WHERE ($empresas=[] OR e.id IN $empresas) AND ($periodo='' OR d.data_referencia=$periodo)
        AND coalesce(d.vigente,true)=true
        RETURN count(d) AS total""", filtros)[0]["total"]
    if not documentos:
        return {"trechos": [], "rastreio": {"filtros": filtros, "estado": "sem_documentos_no_filtro",
                "metodos_executados": [], "latencia_segundos": round(perf_counter()-inicio, 3)}}
    logging.getLogger(__name__).info("Codificando a pergunta com o modelo de embeddings local.")
    vetor = codificar([pergunta])[0]
    logging.getLogger(__name__).info("Consultando índices vetorial e Fulltext.")
    total = banco.consultar("MATCH (t:Trecho) WHERE t.modelo_embedding=$modelo RETURN count(t) AS total",
                           {"modelo": IDENTIFICADOR})[0]["total"]
    if not total:
        raise ValueError("Execute a indexação antes de consultar.")
    consulta_vetor = ("CALL db.index.vector.queryNodes('trechos_vetor',$quantidade,$vetor) YIELD node AS t,score\n"
                      + FILTROS + " AND t.modelo_embedding=$modelo\nRETURN " + CAMPOS + ",score ORDER BY score DESC LIMIT 12")
    vetoriais = banco.consultar(consulta_vetor, {**filtros, "vetor": vetor, "quantidade": total, "modelo": IDENTIFICADOR})
    texto_lucene = lexical(pergunta)
    consulta_texto = ("CALL db.index.fulltext.queryNodes('trechos_texto',$texto) YIELD node AS t,score\n"
                      + FILTROS + "\nRETURN " + CAMPOS + ",score ORDER BY score DESC LIMIT 12")
    textuais = banco.consultar(consulta_texto, {**filtros, "texto": texto_lucene}) if texto_lucene and not somente_vetor else []
    registros = [("vetor", vetoriais), ("fulltext", textuais)]
    rastreio = {"vetorial": consulta_vetor, "fulltext": consulta_texto, "filtros": filtros, "modelo_embedding": IDENTIFICADOR}
    if usar_llm and not somente_vetor:
        logging.getLogger(__name__).info("Gerando e validando Cypher.")
        consulta, operadores, tentativas = gerar_cypher(pergunta, filtros, banco)
        resultado = banco.transacao([(consulta, filtros)], limite_ms=TEMPO_CONSULTA_GERADA_MS)[0]
        ids = [linha[0] for linha in resultado["linhas"]]
        linhas = banco.consultar("MATCH (t:Trecho) WHERE t.id IN $ids " + FILTROS + "\nRETURN " + CAMPOS,
                                {**filtros, "ids": ids})
        registros.append(("cypher_llm", linhas))
        rastreio.update(cypher_llm=consulta, operadores=operadores, tentativas_cypher=tentativas)
    rastreio["latencia_segundos"] = round(perf_counter() - inicio, 3)
    rastreio["metodos_executados"] = [nome for nome, _ in registros if nome != "fulltext" or not somente_vetor]
    rastreio["candidatos_por_metodo"] = {nome: [linha["id"] for linha in linhas] for nome, linhas in registros}
    selecionados = combinar(registros)[:8]
    rastreio["trechos_apos_fusao"] = [t["id"] for t in selecionados]
    return {"trechos": selecionados, "rastreio": rastreio}
