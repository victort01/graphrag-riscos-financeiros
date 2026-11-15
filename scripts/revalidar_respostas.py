"""Reaplica guardas às saídas arquivadas, sem nova inferência ou alteração da origem."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.respostas import processar_saida
from riscos.versao import identificar


def revalidar(origem):
    relatorio = json.loads(json.dumps(origem))
    if origem["estado"] not in {"concluida", "concluida_com_falhas"}:
        raise ValueError("A geração precisa estar concluída.")
    relatorio["uso"] += " Revalidação determinística após observar erros; não é nova inferência nem avaliação independente da correção."
    relatorio["revalidacao"] = {"data_utc": datetime.now(timezone.utc).isoformat(),
        "nova_inferencia": False, "versao": identificar(), "revisao_semantica_humana": "pendente"}
    for linha in relatorio["linhas"]:
        if linha["erro"]:
            continue
        contexto = {k: v for k, v in linha["contexto_enviado"].items() if k != "pergunta"}
        linha.update(processar_saida(linha["pergunta"], contexto, linha["resposta_original_modelo"]))
    return relatorio


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("origem", type=Path)
    parser.add_argument("saida", type=Path)
    args = parser.parse_args()
    if args.saida.exists():
        parser.error("A saída já existe. Preserve a revisão anterior e use outro arquivo.")
    if args.origem.resolve() == args.saida.resolve():
        parser.error("Origem e saída precisam ser arquivos distintos.")
    relatorio = revalidar(json.loads(args.origem.read_text(encoding="utf-8")))
    relatorio["revalidacao"]["sha256_geracao_original"] = hashlib.sha256(args.origem.read_bytes()).hexdigest()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(relatorio['linhas'])} execuções preservadas; nenhuma nova inferência.")
