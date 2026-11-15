"""Ontologia financeira e migrações idempotentes de constraints e índices."""
ROTULOS = ("Entidade", "Empresa", "Documento", "Trecho", "Declaracao", "Periodo", "ObrigacaoFinanceira",
           "FluxoFinanceiro", "MedidaProtecao", "Exposicao", "FatorRisco", "Moeda",
           "Indexador", "CategoriaHedge")
# Cada declaração preserva uma observação temporal. O conceito pode reaparecer em outro exercício.
RELACOES = {
    "TEM_EXPOSICAO": (("Empresa",), ("Exposicao",)),
    "TEM_OBRIGACAO": (("Empresa",), ("ObrigacaoFinanceira",)),
    "TEM_RECEITA": (("Empresa",), ("FluxoFinanceiro",)),
    "ADOTA_PROTECAO": (("Empresa",), ("MedidaProtecao",)),
    "DECORRE_DE": (("Exposicao",), ("ObrigacaoFinanceira", "FluxoFinanceiro")),
    "ASSOCIADA_A": (("Exposicao",), ("FatorRisco",)),
    "DENOMINADO_EM": (("ObrigacaoFinanceira", "FluxoFinanceiro", "Exposicao"), ("Moeda",)),
    "PROTEGE": (("MedidaProtecao", "ObrigacaoFinanceira"), ("ObrigacaoFinanceira", "FluxoFinanceiro", "Exposicao")),
    "COMPENSA_VARIACOES_DE": (("ObrigacaoFinanceira",), ("FluxoFinanceiro",)),
    "SENSIVEL_A": (("ObrigacaoFinanceira", "FluxoFinanceiro", "Exposicao"), ("FatorRisco", "Indexador")),
    "CONVERTE_DE": (("MedidaProtecao",), ("Indexador", "Moeda")),
    "CONVERTE_PARA": (("MedidaProtecao",), ("Indexador", "Moeda")),
    "CATEGORIZADA_COMO": (("MedidaProtecao",), ("CategoriaHedge",)),
}


def migrar(banco):
    comandos = [(f"CREATE CONSTRAINT {rotulo.lower()}_id IF NOT EXISTS "
                 f"FOR (n:{rotulo}) REQUIRE n.id IS UNIQUE", {}) for rotulo in ROTULOS]
    comandos += [
        ("CREATE CONSTRAINT documento_versao IF NOT EXISTS FOR (n:Documento) REQUIRE n.chave_versao IS UNIQUE", {}),
        ("CREATE CONSTRAINT documento_vigente IF NOT EXISTS FOR (n:Documento) REQUIRE n.chave_vigente IS UNIQUE", {}),
        ("CREATE RANGE INDEX declaracao_periodo IF NOT EXISTS FOR (n:Declaracao) ON (n.periodo,n.empresa_id)", {}),
        ("CREATE RANGE INDEX documento_hash IF NOT EXISTS FOR (n:Documento) ON (n.sha256)", {}),
        ("CREATE FULLTEXT INDEX trechos_texto IF NOT EXISTS FOR (n:Trecho) ON EACH [n.texto]", {}),
        ("CREATE FULLTEXT INDEX entidades_nome IF NOT EXISTS FOR (n:Entidade) ON EACH [n.nome,n.aliases_texto]", {}),
        ("""CREATE VECTOR INDEX trechos_vetor IF NOT EXISTS FOR (n:Trecho) ON (n.embedding)
            OPTIONS {indexConfig: {`vector.dimensions`:384,`vector.similarity_function`:'cosine'}}""", {}),
    ]
    for comando in comandos:
        banco.transacao([comando])
    banco.transacao([("CALL db.awaitIndexes(120)", {})])
