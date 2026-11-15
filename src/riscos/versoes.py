"""Identidade da série documental e regras de substituição explícita."""
import hashlib
import json
import re
from datetime import date


VERSAO = "versoes-v1"


def metadados(fonte):
    cnpj = re.sub(r"\D", "", fonte["identificacao_cvm"]["CNPJ_CIA"])
    if len(cnpj) != 14:
        raise ValueError("O CNPJ da fonte precisa conter 14 dígitos.")
    periodo = date.fromisoformat(fonte["data_referencia"]).isoformat()
    versao = str(fonte["versao_declarada_cvm"])
    if not versao.isdecimal() or int(versao) < 1:
        raise ValueError("A versão documental deve ser um inteiro positivo.")
    serie = "|".join((cnpj, fonte["tipo"], periodo))
    return {"empresa_id": "empresa:" + cnpj, "tipo": fonte["tipo"],
        "chave_serie": serie, "chave_versao": serie + "|" + str(int(versao)),
        "versao": str(int(versao)), "substitui": fonte.get("substitui")}


def hash_fonte(fonte):
    identidade = {**metadados(fonte), **{k: fonte.get(k) for k in
        ("id", "sha256", "url", "empresa", "data_referencia", "data_recebimento_cvm")}}
    return hashlib.sha256(json.dumps(identidade, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validar_publicacao(fonte, documentos):
    meta = metadados(fonte)
    por_id = {d["id"]: d for d in documentos}
    atual = por_id.get(fonte["id"])
    if atual:
        if atual["sha"] != fonte["sha256"] or int(atual["versao"]) != int(meta["versao"]):
            raise ValueError("Outro conteúdo ou versão exige outro ID de documento.")
        if atual.get("substitui") != meta["substitui"]:
            raise ValueError("A cadeia de versões de um documento publicado é imutável.")
    anteriores = [d for d in documentos if d["id"] != fonte["id"]]
    if meta["substitui"]:
        anterior = por_id.get(meta["substitui"])
        if anterior is None or anterior["id"] == fonte["id"]:
            raise ValueError("A versão anterior deve existir na mesma empresa, tipo e exercício.")
        if int(anterior["versao"]) >= int(meta["versao"]):
            raise ValueError("A nova versão precisa ser maior que a versão substituída.")
        if not atual and not anterior["vigente"]:
            raise ValueError("Substitua a versão vigente, sem criar ramificações sobre uma versão antiga.")
    elif anteriores and not atual:
        raise ValueError("Uma nova versão da série exige o campo substitui no manifesto.")
    return meta
