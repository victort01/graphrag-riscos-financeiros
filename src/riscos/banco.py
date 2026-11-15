"""Cliente transacional Neo4j: HTTP local ou Bolt com TLS para o Aura."""
import base64
import json
import atexit
import ssl
from functools import lru_cache
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .config import ambiente


@lru_cache(maxsize=4)
def conexao_bolt(uri, autenticacao, timeout, ca_bundle=""):
    from neo4j import GraphDatabase
    opcoes = {}
    if ca_bundle:
        endereco = urlsplit(uri)
        if endereco.scheme not in {"neo4j+s", "bolt+s", "neo4j", "bolt"}:
            raise ValueError("O certificado personalizado exige URI Neo4j/Bolt com TLS verificado.")
        # O driver exige esquema simples para receber um SSLContext explícito.
        # A validação da cadeia e do hostname permanece habilitada.
        uri = endereco._replace(scheme=endereco.scheme.removesuffix("+s")).geturl()
        opcoes = {"encrypted": True, "ssl_context": ssl.create_default_context(cafile=ca_bundle)}
    driver = GraphDatabase.driver(uri, auth=autenticacao,
        connection_timeout=timeout, max_connection_pool_size=2, max_connection_lifetime=300, **opcoes)
    atexit.register(driver.close)
    return driver


class Banco:
    def __init__(self, timeout=90):
        self.timeout = timeout
        config = ambiente()
        senha = config.get("NEO4J_PASSWORD")
        if not senha:
            raise ValueError("Defina NEO4J_PASSWORD no .env ou no ambiente.")
        usuario = config.get("NEO4J_USER", "neo4j")
        token = base64.b64encode(f"{usuario}:{senha}".encode()).decode()
        self.url = config.get("NEO4J_HTTP_URL", "http://127.0.0.1:17474").rstrip("/") + "/db/neo4j/tx/commit"
        self.headers = {"Content-Type": "application/json", "Authorization": "Basic " + token}
        self.uri = config.get("NEO4J_URI", "")
        self.autenticacao = (usuario, senha)
        self.database = config.get("NEO4J_DATABASE", "neo4j")
        self.ca_bundle = config.get("NEO4J_CA_BUNDLE", "")
        self.modo = config.get("NEO4J_ACCESS_MODE", "READ").upper()
        if self.modo not in {"READ", "WRITE"}:
            raise ValueError("NEO4J_ACCESS_MODE deve ser READ ou WRITE.")

    def transacao(self, comandos, limite_ms=None):
        """Executa os comandos atomicamente, ou propaga a falha e o rollback."""
        if self.uri:
            return self._bolt(comandos, limite_ms)
        payload = {"statements": [{"statement": texto, "parameters": parametros}
                                  for texto, parametros in comandos]}
        headers = dict(self.headers)
        if limite_ms:
            headers["max-execution-time"] = str(limite_ms)
        req = Request(self.url, headers=headers, data=json.dumps(payload).encode())
        with urlopen(req, timeout=self.timeout) as resposta:
            resultado = json.load(resposta)
        if resultado["errors"]:
            erro = resultado["errors"][0]
            raise RuntimeError(f"{erro['code']}: {erro['message']}")
        return [dict(colunas=r["columns"], linhas=[d["row"] for d in r["data"]], plano=r.get("plan"))
                for r in resultado["results"]]

    def _bolt(self, comandos, limite_ms):
        from neo4j.exceptions import Neo4jError
        # A transação explícita preserva a atomicidade entre todos os comandos,
        # inclusive na ingestão; não repetimos escritas implicitamente.
        try:
            driver = conexao_bolt(self.uri, self.autenticacao, self.timeout, self.ca_bundle)
            with driver.session(database=self.database, default_access_mode=self.modo) as sessao:
                with sessao.begin_transaction(timeout=(limite_ms / 1000 if limite_ms else self.timeout)) as tx:
                    saidas = []
                    for texto, parametros in comandos:
                        resultado = tx.run(texto, parametros)
                        colunas = list(resultado.keys())
                        linhas = [list(r.values()) for r in resultado]
                        resumo = resultado.consume()
                        saidas.append({"colunas": colunas, "linhas": linhas, "plano": resumo.plan})
                    tx.commit()
                    return saidas
        except Neo4jError as erro:
            raise RuntimeError(f"{erro.code}: {erro.message}") from erro

    def consultar(self, consulta, parametros=None):
        resultado = self.transacao([(consulta, parametros or {})])[0]
        return [dict(zip(resultado["colunas"], linha)) for linha in resultado["linhas"]]
