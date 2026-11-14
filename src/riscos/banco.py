"""Cliente transacional HTTP para o Neo4j 5."""
import base64
import json
from urllib.request import Request, urlopen

from .config import ambiente


class Banco:
    def __init__(self):
        config = ambiente()
        senha = config.get("NEO4J_PASSWORD")
        if not senha:
            raise ValueError("Defina NEO4J_PASSWORD no .env ou no ambiente.")
        usuario = config.get("NEO4J_USER", "neo4j")
        token = base64.b64encode(f"{usuario}:{senha}".encode()).decode()
        self.url = config.get("NEO4J_HTTP_URL", "http://127.0.0.1:17474").rstrip("/") + "/db/neo4j/tx/commit"
        self.headers = {"Content-Type": "application/json", "Authorization": "Basic " + token}

    def transacao(self, comandos):
        """Executa os comandos atomicamente, ou propaga a falha e o rollback."""
        payload = {"statements": [{"statement": texto, "parameters": parametros}
                                  for texto, parametros in comandos]}
        req = Request(self.url, headers=self.headers, data=json.dumps(payload).encode())
        with urlopen(req, timeout=90) as resposta:
            resultado = json.load(resposta)
        if resultado["errors"]:
            erro = resultado["errors"][0]
            raise RuntimeError(f"{erro['code']}: {erro['message']}")
        return [dict(colunas=r["columns"], linhas=[d["row"] for d in r["data"]])
                for r in resultado["results"]]

    def consultar(self, consulta, parametros=None):
        resultado = self.transacao([(consulta, parametros or {})])[0]
        return [dict(zip(resultado["colunas"], linha)) for linha in resultado["linhas"]]
