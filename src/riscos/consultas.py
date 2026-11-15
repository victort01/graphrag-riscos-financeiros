"""Validação de consultas geradas usando a análise de plano do próprio Neo4j."""
import re
from .esquema import RELACOES, ROTULOS

TEMPO_CONSULTA_GERADA_MS = 15000

OPERADORES_LEITURA = {
    "ProduceResults", "Projection", "Filter", "NodeByLabelScan", "AllNodesScan",
    "NodeIndexSeek", "NodeUniqueIndexSeek", "NodeIndexSeekByRange", "NodeIndexScan",
    "Expand(All)", "Expand(Into)", "OptionalExpand(All)", "OptionalExpand(Into)",
    "Distinct", "OrderedDistinct", "Limit", "Sort", "Top", "Argument", "Apply",
    "Optional", "SemiApply", "AntiSemiApply", "LetSemiApply", "SelectOrSemiApply",
    "EagerAggregation", "OrderedAggregation", "Unwind", "NodeHashJoin", "ValueHashJoin",
    "RollUpApply", "ShortestPath", "VarLengthExpand(All)", "VarLengthExpand(Pruning)",
    "BFSPruningVarExpand", "CacheProperties", "DirectedRelationshipTypeScan",
}


def validar_consulta(banco, consulta, parametros):
    if len(consulta) > 5000 or not re.match(r"\s*(?:OPTIONAL\s+)?MATCH\b", consulta, re.I):
        raise ValueError("A consulta deve começar por MATCH e ter até 5.000 caracteres.")
    if ";" in consulta or "//" in consulta or "/*" in consulta:
        raise ValueError("Consultas múltiplas e comentários não são aceitos.")
    if "*" in consulta or "<-" in consulta or "`" in consulta:
        raise ValueError("Use padrões dirigidos com tamanho fixo e nomes explícitos do esquema.")
    proibidos = r"\b(?:CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|ALTER|CALL|LOAD|USE|FOREACH|UNION|DBMS|APOC)\b"
    if re.search(proibidos, consulta, re.I):
        raise ValueError("Operação fora do contrato de leitura.")
    if re.search(r"(?:id\s*:\s*|\.id\s*=\s*)\$empresas\b", consulta, re.I):
        raise ValueError("$empresas é uma lista. Use e.id IN $empresas, sem id: $empresas.")
    parametros_usados = set(re.findall(r"\$(\w+)", consulta))
    if parametros_usados != {"empresas", "periodo"}:
        raise ValueError("Use os dois parâmetros $empresas e $periodo para filtrar empresa e documento.")
    tipos = dict(re.findall(r"\((\w+)\s*:\s*(\w+)", consulta))
    if re.search(r"\(\w+:Empresa\s*\{", consulta):
        raise ValueError("Empresa deve ser filtrada por e.id IN $empresas, sem propriedades literais no MATCH.")
    variaveis_relacao = set(re.findall(r"\[(\w+):\w+\]", consulta))
    for variavel in re.findall(r"(\w+)\.declaracao_id", consulta):
        if variavel not in variaveis_relacao:
            raise ValueError("declaracao_id pertence à relação financeira, não ao nó.")
    if set(tipos.values()) - set(ROTULOS):
        raise ValueError("Rótulo inexistente no esquema: " + str(set(tipos.values()) - set(ROTULOS)))
    permitidas = {**RELACOES, "EVIDENCIADA_POR": (("Declaracao",), ("Trecho",)),
                  "PERTENCE_A": (("Trecho",), ("Documento",)), "REFERE_SE_A": (("Documento",), ("Empresa",))}
    arestas = re.findall(r"(?=\((\w+)[^)]*\)\s*-\[\w*:(\w+)\]\s*->\s*\((\w+))", consulta)
    for origem, relacao, destino in arestas:
        if relacao not in permitidas:
            raise ValueError("Relação inexistente: " + relacao)
        de, para = permitidas[relacao]
        if tipos.get(origem) not in de or tipos.get(destino) not in para:
            raise ValueError(f"Tipos inválidos em {origem}-[:{relacao}]->{destino}. Permitidos: {de} -> {para}.")
    if not re.search(r"RETURN\s+(?:DISTINCT\s+)?\w+\.id\s+AS\s+trecho_id\s+LIMIT\s+(?:[1-9]|1[0-6])\s*$", consulta, re.I):
        raise ValueError("Retorne um ID de trecho e aplique LIMIT de até 16.")
    retorno = re.search(r"RETURN\s+(?:DISTINCT\s+)?(\w+)\.id", consulta, re.I).group(1)
    if tipos.get(retorno) != "Trecho":
        raise ValueError("A variável retornada deve ter rótulo Trecho.")
    resultado = banco.transacao([("EXPLAIN " + consulta, parametros)], limite_ms=TEMPO_CONSULTA_GERADA_MS)[0]
    plano = resultado["plano"]
    if not plano:
        raise ValueError("O banco não retornou o plano da consulta.")
    fila = [plano.get("root", plano)]
    operadores = []
    while fila:
        atual = fila.pop()
        operador = atual["operatorType"].split("@")[0]
        if operador not in OPERADORES_LEITURA:
            raise ValueError(f"Operador fora da lista de leitura: {operador}")
        operadores.append(operador)
        fila.extend(atual.get("children", []))
    return operadores
