"""Compara fatos e vetores por conteúdo, permitindo migração dos IDs técnicos."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.banco import Banco
from riscos.config import ROOT
from riscos.ingestao import PIPELINE


def resumo():
    manifesto = json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))
    ids = [d["id"] for d in manifesto["documentos"]]
    banco = Banco()
    documentos = banco.consultar("""MATCH (d:Documento) WHERE d.id IN $ids
        RETURN d.id AS id,d.sha256 AS sha256,d.pipeline AS pipeline,d.versao AS versao,
        coalesce(d.vigente,true) AS vigente,d.chave_versao AS chave_versao""", {"ids": ids})
    if len(documentos) != len(ids):
        raise ValueError("Há documento do manifesto ainda não publicado.")
    declaracoes = banco.consultar("""MATCH (c:Declaracao) WHERE c.documento_id IN $ids
        RETURN c.documento_id AS documento,c.sujeito_id AS sujeito,c.predicado AS predicado,
        c.objeto_id AS objeto,c.periodo AS periodo,c.empresa_id AS empresa,c.evidencia AS evidencia,
        c.escopo AS escopo,c.condicoes AS condicoes,c.polaridade AS polaridade""", {"ids": ids})
    vetores = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE d.id IN $ids AND t.embedding IS NOT NULL
        RETURN d.id AS documento,d.empresa AS empresa,d.data_referencia AS periodo,
        t.sha256 AS sha256,t.texto AS texto,t.pagina_inicio AS pagina_inicio,t.pagina_fim AS pagina_fim,
        t.inicio_original AS inicio_original,t.fim_original AS fim_original,
        t.embedding AS embedding,t.modelo_embedding AS modelo_embedding""", {"ids": ids})
    divergentes = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE d.id IN $ids AND t.documento_id<>d.id RETURN count(t) AS total""", {"ids": ids})[0]["total"]
    def checksum(linhas):
        serializadas = sorted(json.dumps(l, sort_keys=True, ensure_ascii=False) for l in linhas)
        return hashlib.sha256("\n".join(serializadas).encode()).hexdigest()
    return {"uso": "Auditoria operacional do corpus do manifesto, sem métrica de qualidade semântica.",
        "data_utc": datetime.now(timezone.utc).isoformat(), "pipeline_codigo": PIPELINE,
        "documentos": sorted(documentos, key=lambda d: d["id"]),
        "totais": {"documentos": len(documentos), "declaracoes": len(declaracoes), "vetores": len(vetores)},
        "sha256_declaracoes_por_conteudo": checksum(declaracoes),
        "sha256_vetores_por_conteudo": checksum(vetores), "trechos_com_origem_divergente": divergentes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--saida", type=Path, default=ROOT / "data/reports/auditoria-corpus.json")
    parser.add_argument("--comparar", type=Path)
    args = parser.parse_args()
    atual = resumo()
    if args.comparar:
        anterior = json.loads(args.comparar.read_text(encoding="utf-8"))
        campos = ("totais", "sha256_declaracoes_por_conteudo", "sha256_vetores_por_conteudo", "trechos_com_origem_divergente")
        divergencias = [c for c in campos if atual[c] != anterior[c]]
        atual["comparacao"] = {"baseline_sha256": hashlib.sha256(args.comparar.read_bytes()).hexdigest(),
            "campos_comparados": list(campos), "divergencias": divergencias}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(atual, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(atual["totais"], ensure_ascii=False))
    if atual.get("comparacao", {}).get("divergencias"):
        parser.error("Migração alterou o conteúdo auditado: " + ", ".join(atual["comparacao"]["divergencias"]))
