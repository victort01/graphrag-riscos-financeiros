"""Reconcilia empresas/exercícios mencionados com os filtros do recorte atual."""
import re

EMPRESAS = {"Irani": "empresa:92791243000103", "Klabin": "empresa:89637490000145", "Suzano": "empresa:16404287000155"}


class FiltrosIncompativeis(ValueError):
    pass


def reconciliar(pergunta, empresas=None, periodo=""):
    mencionadas = {nome: id_ for nome, id_ in EMPRESAS.items() if re.search(r"\b"+nome+r"\b", pergunta, re.I)}
    if empresas and set(mencionadas.values()) - set(empresas):
        raise FiltrosIncompativeis("A pergunta menciona empresas fora da seleção. Ajuste o campo Empresas para incluir " + ", ".join(mencionadas) + ".")
    anos = set()
    for candidato in re.finditer(r"\b20\d{2}\b", pergunta):
        prefixo = pergunta[max(0, candidato.start()-12):candidato.start()]
        sufixo = pergunta[candidato.end():candidato.end()+18]
        if re.search(r"(?:R\$|US\$|USD|BRL)\s*$", prefixo, re.I) or re.match(r"\s*(?:reais|d[oó]lares|mil\b|milh|bilh|%)", sufixo, re.I):
            continue
        anos.add(candidato.group())
    if periodo and anos and anos != {periodo[:4]}:
        raise FiltrosIncompativeis("A pergunta e o exercício selecionado são diferentes. Ajuste Exercício ou escolha Comparar exercícios.")
    if not empresas and mencionadas:
        empresas = list(mencionadas.values())
    if not periodo and len(anos) == 1:
        periodo = next(iter(anos)) + "-12-31"
    return empresas, periodo
