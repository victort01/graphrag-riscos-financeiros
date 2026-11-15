"""Indexação do mesmo universo narrativo elegível para Fulltext e vetor."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.banco import Banco
from riscos.embeddings import IDENTIFICADOR, codificar

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reindexar", action="store_true", help="Recalcula também os vetores já presentes.")
    args = parser.parse_args()
    banco = Banco()
    linhas = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE t.natureza='narrativa' AND t.recorte=false AND coalesce(d.vigente,true)=true
          AND ($reindexar OR t.modelo_embedding IS NULL OR t.modelo_embedding<>$modelo)
        RETURN t.id AS id,t.texto AS texto,d.empresa AS empresa,d.data_referencia AS periodo ORDER BY id""",
        {"modelo": IDENTIFICADOR, "reindexar": args.reindexar})
    print(f"{len(linhas)} trechos pendentes de indexação", flush=True)
    for inicio in range(0, len(linhas), 8):
        lote = linhas[inicio:inicio+8]
        vetores = codificar([l["empresa"] + " " + l["periodo"] + " " + l["texto"] for l in lote], manter_carregado=True)
        parametros = [{"id": l["id"], "vetor": vetor} for l, vetor in zip(lote, vetores)]
        banco.transacao([("""UNWIND $linhas AS row MATCH (t:Trecho {id:row.id})
            SET t.embedding=row.vetor,t.modelo_embedding=$modelo""",
            {"linhas": parametros, "modelo": IDENTIFICADOR})])
        print(f"{min(inicio+8,len(linhas))}/{len(linhas)}", flush=True)
