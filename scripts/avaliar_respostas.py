"""Geração sobre contextos congelados; suporte semântico depende de revisão."""
import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.config import ROOT, ambiente
from riscos.respostas import responder_contexto
from riscos.versao import identificar


def gravar(caminho, conteudo):
    temporario = caminho.with_suffix(".tmp")
    temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(caminho)


def executar(entrada, saida, conjunto, retomar=False):
    recuperacao = json.loads(entrada.read_text(encoding="utf-8"))
    if recuperacao["estado"] != "concluida" or any(l["erro"] for l in recuperacao["linhas"]):
        raise ValueError("A recuperação precisa estar concluída sem falhas.")
    assinatura = hashlib.sha256(entrada.read_bytes()).hexdigest()
    if hashlib.sha256(conjunto.read_bytes()).hexdigest() != recuperacao["sha256_conjunto"]:
        raise ValueError("O conjunto informado difere daquele congelado na recuperação.")
    perguntas = {p["id"]: p["pergunta"] for p in json.loads(conjunto.read_text(encoding="utf-8"))["perguntas"]}
    codigo = identificar()
    config = {"artefato": ambiente().get("LLM_ARTIFACT", "não registrado"),
              "alias": ambiente().get("LLM_MODEL", "qwen-riscos-local"), "temperatura": 0, "seed": 42,
              "max_tokens": 800}
    linhas = list(recuperacao["linhas"])
    random.Random(42).shuffle(linhas)
    chaves = [(l["pergunta_id"], l["metodo"]) for l in linhas]
    if len(chaves) != len(set(chaves)):
        raise ValueError("Há pares pergunta/método duplicados no relatório de entrada.")
    if saida.exists():
        if not retomar:
            raise ValueError("A saída já existe. Use outro arquivo ou --retomar.")
        relatorio = json.loads(saida.read_text(encoding="utf-8"))
        if (relatorio["sha256_recuperacao"] != assinatura or relatorio["modelo"] != config or
                relatorio["versao_geracao"]["sha256_codigo_catalogos_dependencias"] != codigo["sha256_codigo_catalogos_dependencias"]):
            raise ValueError("Entrada, modelo ou código mudou; inicie outra rodada.")
    else:
        relatorio = {"uso": recuperacao["uso"], "data_utc": datetime.now(timezone.utc).isoformat(),
            "sha256_recuperacao": assinatura, "versao_recuperacao": recuperacao["versao_execucao"],
            "versao_geracao": codigo, "modelo": config, "estado": "em_execucao", "em_andamento": None,
            "ordem": chaves, "linhas": [], "limites": [
                "Não mede suporte semântico automaticamente; nenhuma taxa de alucinação é calculada.",
                "Latência de geração descritiva; não inclui a recuperação anterior.",
                conjunto.name + ": " + recuperacao["uso"]]}
    concluidas = {(l["pergunta_id"], l["metodo"]) for l in relatorio["linhas"]}
    saida.parent.mkdir(parents=True, exist_ok=True)
    for linha in linhas:
        chave = (linha["pergunta_id"], linha["metodo"])
        if chave in concluidas:
            continue
        pergunta = perguntas[chave[0]]
        if "pergunta" in linha["contexto"] and linha["contexto"]["pergunta"] != pergunta:
            raise ValueError("A pergunta no contexto diverge do conjunto congelado.")
        contexto = {k: v for k, v in linha["contexto"].items() if k != "pergunta"}
        relatorio["em_andamento"] = chave
        gravar(saida, relatorio)
        inicio = perf_counter()
        resultado = {"pergunta_id": chave[0], "metodo": chave[1], "pergunta": pergunta,
            "sha256_contexto": hashlib.sha256(json.dumps(contexto, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "erro": None}
        try:
            resultado.update(responder_contexto(pergunta, contexto))
        except Exception as erro:
            resultado["erro"] = {"tipo": type(erro).__name__, "mensagem": str(erro)}
        resultado["latencia_geracao_segundos"] = round(perf_counter()-inicio, 3)
        relatorio["linhas"].append(resultado)
        relatorio["em_andamento"] = None
        gravar(saida, relatorio)
        print(*chave, "erro" if resultado["erro"] else "ok", flush=True)
    relatorio["estado"] = "concluida_com_falhas" if any(l["erro"] for l in relatorio["linhas"]) else "concluida"
    gravar(saida, relatorio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--recuperacao", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--conjunto", type=Path, default=ROOT / "data/perguntas-smoke-recuperacao.json")
    parser.add_argument("--retomar", action="store_true", help="Retoma apenas pares ainda não registrados; preserva erros anteriores.")
    args = parser.parse_args()
    executar(args.recuperacao, args.saida, args.conjunto, args.retomar)
