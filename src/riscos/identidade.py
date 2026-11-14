"""Identidade canônica com escopo de companhia e aliases explícitos."""
import hashlib
import re
import unicodedata


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def chave_hash(*partes):
    return hashlib.sha256("\x1f".join(str(p) for p in partes).encode()).hexdigest()[:32]


GLOBAIS = {"Moeda", "Indexador", "FatorRisco", "CategoriaHedge"}
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
}


def entidade(tipo, nome, empresa_id, qualificacao=""):
    canonico = ALIASES.get((tipo, normalizar(nome)), nome)
    # A chave da companhia impede unir instrumentos de emissores diferentes.
    dominio = "global" if tipo in GLOBAIS else empresa_id
    identidade = chave_hash(tipo, dominio, normalizar(canonico), normalizar(qualificacao))
    return {"id": f"{tipo.lower()}:{identidade}", "tipo": tipo, "nome": canonico,
            "empresa_id": None if tipo in GLOBAIS else empresa_id,
            "aliases": [nome], "granularidade": "conceito" if tipo in GLOBAIS else "classe_de_instrumento",
            "qualificacao": qualificacao}
