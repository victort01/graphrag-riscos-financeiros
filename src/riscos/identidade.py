"""Identidade canônica com escopo de companhia e aliases explícitos."""
import hashlib
import re
import unicodedata


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def chave_hash(*partes):
    return hashlib.sha256("\x1f".join(str(p) for p in partes).encode()).hexdigest()[:32]


GLOBAIS = {"Moeda", "Indexador", "FatorRisco", "CategoriaHedge", "TipoInstrumento"}
VERSAO = "identidades-v2"
ALIASES = {
    ("Moeda", "usd"): "USD",
    ("Moeda", "us"): "USD",
    ("Moeda", "dolar americano"): "USD",
    ("Moeda", "dolares americanos"): "USD",
    ("Moeda", "dolares dos estados unidos da america"): "USD",
    ("Moeda", "brl"): "BRL",
    ("Moeda", "reais"): "BRL",
    ("Indexador", "cdi"): "CDI",
    ("Indexador", "ipca"): "IPCA",
    ("Indexador", "sofr"): "SOFR",
    ("FatorRisco", "variacao cambial"): "variação cambial",
    ("FatorRisco", "risco cambial"): "variação cambial",
    ("FatorRisco", "taxa de juros"): "taxas de juros",
    ("FatorRisco", "risco de taxa de juros"): "taxas de juros",
    ("MedidaProtecao", "non deliverable forward"): "NDF",
    ("MedidaProtecao", "non deliverable forwards"): "NDF",
    ("MedidaProtecao", "ndfs"): "NDF",
    ("MedidaProtecao", "zero cost collar"): "Zero Cost Collar",
    ("MedidaProtecao", "zcc"): "Zero Cost Collar",
    ("MedidaProtecao", "zccs"): "Zero Cost Collar",
    ("ObrigacaoFinanceira", "adiantamento sobre contrato de cambio"): "ACC",
    ("ObrigacaoFinanceira", "accs"): "ACC",
}


def entidade(tipo, nome, empresa_id, qualificacao=""):
    canonico = ALIASES.get((tipo, normalizar(nome)), nome)
    # A chave da companhia impede unir instrumentos de emissores diferentes.
    dominio = "global" if tipo in GLOBAIS else empresa_id
    identidade = chave_hash(tipo, dominio, normalizar(canonico), normalizar(qualificacao))
    ambigua = (tipo == "Moeda" and normalizar(nome) in {"dolar", "dolares"}) or (
        tipo == "MedidaProtecao" and normalizar(nome) in {"swap", "swaps", "derivativos"} and not qualificacao)
    return {"id": f"{tipo.lower()}:{identidade}", "tipo": tipo, "nome": canonico,
            "empresa_id": None if tipo in GLOBAIS else empresa_id,
            "aliases": [nome], "granularidade": "conceito" if tipo in GLOBAIS else "classe_de_instrumento",
            "qualificacao": qualificacao, "revisao_identidade": ambigua}


def resolver_mencoes(entidades, mencoes):
    """Resolve uma menção genérica somente se o próprio trecho qualificar um único candidato."""
    for generica in list(entidades.values()):
        if not generica.get("revisao_identidade"):
            continue
        raiz = normalizar(generica["nome"]).rstrip("s")
        candidatas = [e for e in entidades.values() if e["tipo"] == generica["tipo"]
                      and not e.get("revisao_identidade") and normalizar(e["nome"]).startswith(raiz + " ")]
        if len(candidatas) == 1:
            escolhida = candidatas[0]
            escolhida["aliases"].extend(a for a in generica["aliases"] if a not in escolhida["aliases"])
            for mencao in mencoes:
                if mencao["entidade_id"] == generica["id"]:
                    mencao["entidade_id"] = escolhida["id"]
                    mencao["resolucao"] = "qualificacao_unica_no_trecho"
            del entidades[generica["id"]]
