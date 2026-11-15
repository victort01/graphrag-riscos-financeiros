"""Uma consulta local por vez, independente da conexão WebSocket da tela."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from threading import Lock
from uuid import uuid4
from .config import ROOT
from .execucoes import salvar, PASTA

FORMATO_ID = re.compile(r"\d{8}T\d{12}-[0-9a-f]{32}")


class ConsultaEmAndamento(ValueError):
    pass


class Gerenciador:
    def __init__(self, pasta=ROOT / "data/reports/trabalhos", resultados=PASTA, processar=None):
        self.pasta, self.resultados, self.processar = pasta, resultados, processar
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="consulta-graphrag")
        self.trava, self.futuro = Lock(), None
        # Há um único processo Streamlit neste deployment local. A reinicialização
        # não pode apresentar uma tarefa perdida como se ainda estivesse ativa.
        for arquivo in self.pasta.glob("*.json"):
            estado = json.loads(arquivo.read_text(encoding="utf-8"))
            if estado["estado"] in {"aguardando", "em_execucao"}:
                estado.update(estado="interrompida", erro="O servidor foi reiniciado. Repita a consulta.")
                self._gravar(estado)

    def _gravar(self, estado):
        arquivo = self.pasta / (estado["id"] + ".json")
        temporario = arquivo.with_suffix(".tmp")
        temporario.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(arquivo)

    def iniciar(self, pergunta, empresas, periodo):
        with self.trava:
            if self.futuro is not None and not self.futuro.done():
                raise ConsultaEmAndamento("Já há uma consulta em processamento. Aguarde a conclusão antes de enviar outra pergunta.")
            id_ = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + uuid4().hex
            estado = {"id": id_, "pergunta": pergunta, "empresas": empresas, "periodo": periodo,
                "data_criacao": datetime.now(timezone.utc).isoformat(), "estado": "aguardando", "etapa": "Preparando consulta"}
            self._gravar(estado)
            self.futuro = self.executor.submit(self._executar, estado)
            return id_

    def _executar(self, estado):
        def andamento(etapa):
            estado.update(estado="em_execucao", etapa=etapa)
            self._gravar(estado)

        try:
            andamento("Consultando fontes e validando Cypher")
            processar = self.processar
            if processar is None:
                from .respostas import responder
                processar = responder
            resultado = processar(estado["pergunta"], estado["empresas"], estado["periodo"], andamento=andamento)
            arquivo = salvar(resultado, self.resultados)
            estado.update(estado="concluida", etapa="Concluída", arquivo_resultado=arquivo.name)
        except Exception as erro:
            estado.update(estado="falhou", erro=str(erro))
        self._gravar(estado)

    def consultar(self, id_):
        if not FORMATO_ID.fullmatch(id_):
            raise ValueError("Identificador de consulta inválido.")
        return json.loads((self.pasta / (id_ + ".json")).read_text(encoding="utf-8"))

    def ultima(self):
        arquivos = sorted(self.pasta.glob("*.json"), reverse=True)
        return self.consultar(arquivos[0].stem) if arquivos else None

    def carregar_resultado(self, estado):
        nome = estado["arquivo_resultado"]
        if estado["estado"] != "concluida" or Path(nome).name != nome:
            raise ValueError("A consulta não possui resultado concluído.")
        return json.loads((self.resultados / nome).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def gerenciador():
    return Gerenciador()
