"""NER e RE por regras de domínio com evidência e condições preservadas.

As regras procuram construções financeiras em qualquer documento do manifesto.
Elas produzem um baseline auditável, com cobertura medida na fase de avaliação.
"""
import re
from .identidade import entidade, chave_hash, normalizar, resolver_mencoes
from .esquema import RELACOES

VERSAO = "regras-financeiras-v4"
TERMOS = [
    ("Moeda", "USD", r"\bUSD\b|US\$|d[oó]lar(?:es)? (?:americanos?|dos Estados Unidos(?: da Am[eé]rica)?)"),
    ("Moeda", "BRL", r"\bBRL\b|R\$|\breais\b|(?-i:\bReal\b)"),
    ("Indexador", "CDI", r"\bCDI\b"),
    ("Indexador", "IPCA", r"\bIPCA\b"),
    ("Indexador", "SOFR", r"\bSOFR\b"),
    ("ObrigacaoFinanceira", "ACC", r"\bACCs?\b|Adiantamento sobre Contrato de C[aâ]mbio"),
    ("MedidaProtecao", "Zero Cost Collar", r"Zero Cost Collar|\bZCCs?\b"),
    ("MedidaProtecao", "NDF", r"Non.?Deliverable Forward[s]?|Non.?Deriverable Forward[s]?|\bNDFs?\b"),
    ("MedidaProtecao", "swap", r"\bswaps?\b"),
]


def extrair(trecho, fonte):
    texto = trecho["texto"]
    companhia = fonte["identificacao_cvm"]["CNPJ_CIA"].replace(".", "").replace("/", "").replace("-", "")
    empresa = {"id": "empresa:" + companhia, "tipo": "Empresa", "nome": fonte["empresa"],
               "empresa_id": companhia, "aliases": [fonte["empresa"]], "granularidade": "pessoa_juridica", "qualificacao": ""}
    entidades = {empresa["id"]: empresa}
    mencoes, declaracoes = [], []
    for tipo, nome, padrao in TERMOS:
        for match in re.finditer(padrao, texto, re.I):
            registro = entidade(tipo, nome, companhia)
            registro["aliases"] = [nome, match.group()]
            existente = entidades.setdefault(registro["id"], registro)
            existente["aliases"].extend(a for a in registro["aliases"] if a not in existente["aliases"])
            mencoes.append({"entidade_id": registro["id"], "texto": match.group(),
                            "inicio": match.start(), "fim": match.end()})
    if trecho["natureza"] == "tabela" or trecho["recorte"]:
        return list(entidades.values()), mencoes, declaracoes
    for sentenca in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ü])", texto):
        n = normalizar(sentenca)
        if len(n) < 40:
            continue
        if re.search(r"\bnao\b|\bnunca\b|vedad", n):
            continue
        natureza = "cenario" if re.search(r"analise de sensibilidade|cenario (?:adverso|remoto|base|provavel)", n) else "declaracao"
        if natureza == "cenario":
            continue
        condicoes = sentenca if re.search(r"parcela|parte |limita|provav|politica|horizonte|objetivo", n) else ""
        escopo = "consolidado" if "consolidado" in n else "controladora" if "controladora" in n else "nao_especificado"

        def no(tipo, nome):
            registro = entidade(tipo, nome, companhia)
            entidades[registro["id"]] = registro
            return registro

        def rel(sujeito, predicado, objeto, regra):
            origens, destinos = RELACOES[predicado]
            if sujeito["tipo"] not in origens or objeto["tipo"] not in destinos:
                raise ValueError(f"Relação incompatível com a ontologia: {predicado}")
            identificador = chave_hash(trecho["sha256"], trecho["id"], sujeito["id"], predicado, objeto["id"], sentenca, regra)
            declaracoes.append({"id": "declaracao:" + identificador, "sujeito_id": sujeito["id"],
                                "objeto_id": objeto["id"], "predicado": predicado, "empresa_id": companhia,
                                "periodo": fonte["data_referencia"], "periodo_origem": "referencia_documento",
                                "escopo": escopo, "natureza": natureza, "polaridade": "afirmativa",
                                "condicoes": condicoes, "evidencia": sentenca, "trecho_id": trecho["id"],
                                "documento_id": fonte["id"], "regra": regra, "extrator": VERSAO,
                                "revisao_temporal": bool(re.search(r"\b20\d{2}\b", sentenca))})

        def adotar(nome, regra):
            medida = no("MedidaProtecao", nome)
            rel(empresa, "ADOTA_PROTECAO", medida, regra)
            return medida

        if re.search(r"(?:companhia|controladas|ativos e passivos).{0,250}expost.{0,100}(?:cambial|moeda estrangeira|cambio)", n):
            exposicao = no("Exposicao", "exposição cambial declarada")
            rel(empresa, "TEM_EXPOSICAO", exposicao, "exposicao-explicita")
            rel(exposicao, "ASSOCIADA_A", no("FatorRisco", "variação cambial"), "exposicao-explicita")
        if re.search(r"(?:mantem|contrata|captacao).{0,100}(?:emprestimos|financiamentos|divida).{0,80}moeda estrangeira", n):
            rel(empresa, "TEM_OBRIGACAO", no("ObrigacaoFinanceira", "obrigações em moeda estrangeira"), "obrigacao-estrangeira")
        if re.search(r"financiamentos de exportacao em dolares", n):
            obrigacao = no("ObrigacaoFinanceira", "financiamentos de exportação em USD")
            rel(empresa, "TEM_OBRIGACAO", obrigacao, "financiamento-exportacao-usd")
            rel(obrigacao, "DENOMINADO_EM", no("Moeda", "USD"), "financiamento-exportacao-usd")
        if "receita" in n and re.search(r"proveniente de exportacoes|fluxos de recebimento das vendas no mercado externo", n):
            receita = no("FluxoFinanceiro", "receitas de exportação")
            rel(empresa, "TEM_RECEITA", receita, "receita-exportacao")
            if re.search(r"dolares|\busd\b|us ", n):
                rel(receita, "DENOMINADO_EM", no("Moeda", "USD"), "receita-exportacao-usd")
        if re.search(r"proporcionando um hedge natural|como estrategia de hedge natural", n):
            medida = adotar("hedge natural de caixa", "hedge-natural-explicito")
            if "financiamentos de exportacao em dolares" in n:
                rel(medida, "PROTEGE", no("ObrigacaoFinanceira", "financiamentos de exportação em USD"), "hedge-natural-explicito")
        if re.search(r"(?:mantem|contrata|captacoes).{0,100}", n) and re.search(r"\baccs?\b", n):
            acc = no("ObrigacaoFinanceira", "ACC")
            rel(empresa, "TEM_OBRIGACAO", acc, "acc-mantido")
            if re.search(r"fazer frente.{0,100}clientes de exportacoes", n):
                rel(acc, "COMPENSA_VARIACOES_DE", no("FluxoFinanceiro", "recebíveis de exportações"), "acc-recebiveis")
        if "designando" in n and "instrumentos de divida" in n and "receitas futuras" in n and "hedge" in n:
            obrigacao = no("ObrigacaoFinanceira", "instrumentos de dívida designados para hedge")
            receita = no("FluxoFinanceiro", "receitas futuras altamente prováveis")
            rel(empresa, "TEM_OBRIGACAO", obrigacao, "divida-designada-hedge")
            rel(obrigacao, "PROTEGE", receita, "divida-designada-hedge")
            if re.search(r"\bUSD\b|US\$|d[oó]lar(?:es)? americanos?", sentenca, re.I):
                rel(receita, "DENOMINADO_EM", no("Moeda", "USD"), "receita-protegida-usd")
        if "swap" in n and re.search(r"(?:contratad|em vigencia|companhia adota)", n) and "taxa de juros" in n:
            medida = adotar("swap para troca de indexador de juros", "swap-finalidade-juros")
            rel(medida, "PROTEGE", no("Exposicao", "exposição a taxas de juros"), "swap-finalidade-juros")
        if "swap" in n and re.search(r"convertendo|converter", n) and re.search(r"moeda (?:local|nacional)", n) and "dolares americanos" in n:
            medida = adotar("swap de BRL para USD", "swap-conversao-cambial")
            rel(medida, "CONVERTE_DE", no("Moeda", "BRL"), "swap-conversao-cambial")
            rel(medida, "CONVERTE_PARA", no("Moeda", "USD"), "swap-conversao-cambial")
        if re.search(r"companhia contrata|companhia se baseia na contratacao|objetivo de hedge", n):
            for tipo, nome, padrao in TERMOS:
                if tipo == "MedidaProtecao" and nome != "swap" and re.search(padrao, sentenca, re.I):
                    medida = adotar(nome, "derivativo-contratado")
                    if re.search(r"exposicao liquida|exposicao cambial liquida", n):
                        exposicao = no("Exposicao", "exposição cambial líquida de caixa")
                        rel(empresa, "TEM_EXPOSICAO", exposicao, "exposicao-protegida")
                        rel(medida, "PROTEGE", exposicao, "derivativo-objeto-explicito")
                        if re.search(r"variacao cambial|exposicao cambial", n):
                            rel(exposicao, "ASSOCIADA_A", no("FatorRisco", "variação cambial"), "objeto-cambial-explicito")
    resolver_mencoes(entidades, mencoes)
    return list(entidades.values()), mencoes, declaracoes
