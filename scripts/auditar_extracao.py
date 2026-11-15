"""Confere integridade e prepara a inspeção documental das declarações extraídas."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.config import ROOT
from riscos.ingestao import preparar, validar_dados, PIPELINE
from riscos.versao import identificar


def executar():
    fontes = json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))["documentos"]
    casos, erros, documentos = [], [], []
    for fonte in fontes:
        pdf = ROOT / "data/raw" / (fonte["id"] + ".pdf")
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != fonte["sha256"]:
            raise ValueError("Checksum divergente: " + fonte["id"])
        dados = preparar(fonte)
        validar_dados(dados)
        trechos = {t["id"]: t for t in dados["trechos"]}
        entidades = {e["id"]: e for e in dados["entidades"]}
        grupos = {}
        for d in dados["declaracoes"]:
            trecho = trechos[d["trecho_id"]]
            chave = (d["trecho_id"], d["evidencia"])
            caso = grupos.setdefault(chave, {
                "documento_id": fonte["id"], "empresa": fonte["empresa"],
                "periodo": fonte["data_referencia"], "sha256_pdf": fonte["sha256"],
                "pagina_inicio": trecho["pagina_inicio"], "pagina_fim": trecho["pagina_fim"],
                "url": fonte["url"] + "#page=" + str(trecho["pagina_inicio"]),
                "evidencia": d["evidencia"], "texto_trecho": trecho["texto"],
                "escopo": d["escopo"], "condicoes": d["condicoes"], "declaracoes": [],
                "revisao_documental": {"estado": "pendente", "revisor": "", "observacoes": ""}})
            caso["declaracoes"].append({
                "id": d["id"], "sujeito": entidades[d["sujeito_id"]]["nome"],
                "predicado": d["predicado"], "objeto": entidades[d["objeto_id"]]["nome"]})
            if d["empresa_id"] != entidades["empresa:" + d["empresa_id"]]["empresa_id"]:
                erros.append(d["id"] + ": empresa inconsistente")
        casos.extend(grupos.values())
        documentos.append({"id": fonte["id"], "trechos": len(trechos),
            "entidades": len(entidades), "declaracoes": len(dados["declaracoes"]),
            "escopos": dict(Counter(d["escopo"] for d in dados["declaracoes"]))})
    for numero, caso in enumerate(casos, 1):
        caso["id"] = f"D{numero:03}"
    return {"uso": "Auditoria automatizada de integridade; não mede suporte semântico, precisão ou recall.",
        "data_utc": datetime.now(timezone.utc).isoformat(), "pipeline": PIPELINE,
        "versao_execucao": identificar(), "documentos": documentos,
        "total_declaracoes": sum(d["declaracoes"] for d in documentos),
        "excertos_para_revisao": len(casos), "erros_integridade": erros,
        "revisao_humana": "pendente", "casos": casos}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--saida", type=Path, default=ROOT / "data/reports/auditoria-extracao.json")
    args = parser.parse_args()
    if args.saida.exists():
        parser.error("A saída já existe; escolha outro arquivo para preservar revisões.")
    resultado = executar()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in (
        "total_declaracoes", "excertos_para_revisao", "erros_integridade", "revisao_humana")}, ensure_ascii=False))
    if resultado["erros_integridade"]:
        raise SystemExit(1)
