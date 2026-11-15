"""Interface estruturada para o modelo local, com contrato JSON explícito."""
import json
from urllib.request import Request, urlopen
from .config import ambiente


def gerar_json(instrucoes, entrada, esquema, limite_tokens=1200):
    config = ambiente()
    corpo = {
        "model": config.get("LLM_MODEL", "qwen-riscos-local"), "temperature": 0, "seed": 42,
        "max_tokens": limite_tokens,
        "response_format": {"type": "json_schema", "json_schema": {"name": "resultado", "schema": esquema}},
        "messages": [{"role": "system", "content": instrucoes},
                     {"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}],
    }
    requisicao = Request(config.get("LLM_URL", "http://127.0.0.1:18081/v1/chat/completions"),
                        headers={"Content-Type": "application/json"}, data=json.dumps(corpo).encode())
    with urlopen(requisicao, timeout=int(config.get("LLM_TIMEOUT", "360"))) as resposta:
        retorno = json.load(resposta)
    if retorno["choices"][0]["finish_reason"] == "length":
        raise ValueError("Resposta truncada pelo limite de tokens.")
    return json.loads(retorno["choices"][0]["message"]["content"])
