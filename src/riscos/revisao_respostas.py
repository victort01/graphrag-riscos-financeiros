"""Lotes sem rótulo de variante para revisão semântica de respostas finais."""
import hashlib
import json
import random


def hash_json(valor):
    return hashlib.sha256(json.dumps(valor, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def preparar(relatorio):
    if relatorio["estado"] not in {"concluida", "concluida_com_falhas"}:
        raise ValueError("Conclua a geração antes de preparar a revisão.")
    linhas = [l for l in relatorio["linhas"] if l["erro"] is None]
    random.Random(137).shuffle(linhas)
    itens, mapa = [], {}
    for indice, linha in enumerate(linhas, 1):
        id_ = f"R{indice:03}"
        fontes = {id_f: {**{k: v for k, v in f.items() if k != "texto"},
                          "sha256_texto_contexto": hashlib.sha256(f["texto"].encode()).hexdigest()}
                  for id_f, f in linha["contexto_enviado"]["fontes"].items()}
        conteudo = {"pergunta": linha["pergunta"], "resposta": linha["resposta"],
                    "fontes": fontes, "caminhos": linha["contexto_enviado"]["caminhos"]}
        itens.append({"id": id_, "sha256_conteudo": hash_json(conteudo), **conteudo,
            "revisao": {"estado": "pendente", "cobertura_pergunta": None,
                        "abstencao_adequada": None, "observacoes": ""},
            "afirmacoes": [{"numero": n, "texto": a["texto"], "apoio": None, "pertinente": None,
                            "empresa_periodo_corretos": None, "justificativa": ""}
                           for n, a in enumerate(linha["resposta"]["afirmacoes"], 1)]})
        mapa[id_] = {"pergunta_id": linha["pergunta_id"], "metodo": linha["metodo"]}
    lote = {"uso": relatorio["uso"], "sha256_geracao": hash_json(relatorio), "revisor": "", "itens": itens,
            "total_execucoes": len(relatorio["linhas"]), "falhas_excluidas": len(relatorio["linhas"])-len(linhas),
            "limites": "O rótulo da variante foi omitido; a presença de caminhos pode permitir inferi-la. As fontes são localizadores e hashes: abrir as páginas dos PDFs para julgar suporte. O contexto integral está no relatório local, separado do formulário."}
    return lote, mapa


def validar(revisao, lote):
    if not revisao["revisor"].strip():
        raise ValueError("Identifique o revisor.")
    if revisao["sha256_geracao"] != lote["sha256_geracao"]:
        raise ValueError("A revisão pertence a outra geração.")
    esperados = {i["id"]: i for i in lote["itens"]}
    itens = {i["id"]: i for i in revisao["itens"]}
    if set(itens) != set(esperados) or len(itens) != len(revisao["itens"]):
        raise ValueError("Itens ausentes, desconhecidos ou duplicados.")
    rotulos = {}
    for id_, item in itens.items():
        original = esperados[id_]
        conteudo = {k: item[k] for k in ("pergunta", "resposta", "fontes", "caminhos")}
        if hash_json(conteudo) != original["sha256_conteudo"]:
            raise ValueError("Conteúdo imutável alterado: " + id_)
        r = item["revisao"]
        if r["estado"] != "concluida" or r["cobertura_pergunta"] not in {"completa", "parcial", "nenhuma", "indeterminavel"}:
            raise ValueError("Revisão pendente ou cobertura inválida: " + id_)
        if len(item["afirmacoes"]) != len(original["afirmacoes"]):
            raise ValueError("Não remova ou acrescente afirmações: " + id_)
        if item["afirmacoes"]:
            if r["abstencao_adequada"] is not None:
                raise ValueError("Resposta com afirmações não deve receber rótulo de abstenção: " + id_)
        elif r["abstencao_adequada"] not in {"adequada", "indevida", "indeterminavel"}:
            raise ValueError("Qualifique a abstenção: " + id_)
        rotulos[id_ + "/cobertura"] = r["cobertura_pergunta"]
        rotulos[id_ + "/abstencao"] = r["abstencao_adequada"]
        for a, esperado in zip(item["afirmacoes"], original["afirmacoes"]):
            if (a["numero"], a["texto"]) != (esperado["numero"], esperado["texto"]):
                raise ValueError("Texto ou ordem de afirmações alterados: " + id_)
            if a["apoio"] not in {"integral", "parcial", "sem_apoio", "indeterminavel"} or type(a["pertinente"]) is not bool or type(a["empresa_periodo_corretos"]) is not bool:
                raise ValueError("Qualifique todas as afirmações: " + id_)
            if (a["apoio"] != "integral" or not a["pertinente"] or not a["empresa_periodo_corretos"]) and not a["justificativa"].strip():
                raise ValueError("Justifique apoio incompleto ou erro: " + id_)
            for campo in ("apoio", "pertinente", "empresa_periodo_corretos"):
                rotulos[f"{id_}/{a['numero']}/{campo}"] = a[campo]
    return rotulos


def comparar(primeira, segunda, lote):
    a, b = validar(primeira, lote), validar(segunda, lote)
    if primeira["revisor"].strip().casefold() == segunda["revisor"].strip().casefold():
        raise ValueError("As revisões devem ser de pessoas distintas.")
    divergencias = [{"campo": c, "revisor_1": a[c], "revisor_2": b[c]} for c in a if a[c] != b[c]]
    return {"uso": "Concordância de revisão; não é acurácia nem taxa de alucinação.",
        "revisores": [primeira["revisor"], segunda["revisor"]], "itens": len(lote["itens"]),
        "rotulos_comparados": len(a), "rotulos_concordantes": len(a)-len(divergencias),
        "divergencias": divergencias, "adjudicacao_pendente": bool(divergencias)}
