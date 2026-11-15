"""Espera o banco autenticado aceitar Cypher, além da simples abertura da porta HTTP."""
import argparse
import sys
import time
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.banco import Banco


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tempo", type=int, default=180)
    args = parser.parse_args()
    banco = Banco(timeout=130)
    inicio, ultimo_erro = time.monotonic(), "sem resposta"
    while time.monotonic() - inicio < args.tempo:
        try:
            banco.consultar("RETURN 1 AS pronto")
            banco.transacao([("CALL db.awaitIndexes(120)", {})], limite_ms=120000)
            print("Neo4j pronto para consultas autenticadas.", flush=True)
            raise SystemExit(0)
        except HTTPError as erro:
            if erro.code in (401, 403):
                raise SystemExit("Autenticação recusada. Confira o .env e as credenciais do volume existente.")
            ultimo_erro = str(erro)
        except (URLError, TimeoutError, ConnectionError, HTTPException, RuntimeError) as erro:
            ultimo_erro = str(erro)
        time.sleep(1)
    raise SystemExit("Neo4j ainda indisponível após a espera: " + ultimo_erro)
