import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.trabalhos import Gerenciador, ConsultaEmAndamento


class PersistenciaDoProcessamento(unittest.TestCase):
    def setUp(self):
        self.temporario = TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.raiz = Path(self.temporario.name)

    def criar(self, processar):
        servico = Gerenciador(self.raiz / "trabalhos", self.raiz / "resultados", processar)
        self.addCleanup(servico.executor.shutdown)
        return servico

    def test_conclui_e_arquiva_sem_precisar_de_cliente_conectado(self):
        resultado = {"pergunta": "Como o ACC é descrito?", "resposta": {"afirmacoes": []}}
        servico = self.criar(lambda *args, **kwargs: resultado)
        id_ = servico.iniciar(resultado["pergunta"], [], "2025-12-31")
        servico.futuro.result(timeout=3)
        estado = servico.consultar(id_)
        self.assertEqual(estado["estado"], "concluida")
        self.assertEqual(servico.carregar_resultado(estado), resultado)
        self.assertEqual(servico.ultima()["id"], id_)

    def test_recusa_concorrencia_e_preserva_a_consulta_original(self):
        liberar = Event()
        self.addCleanup(liberar.set)
        def processar(*args, **kwargs):
            liberar.wait(timeout=2)
            return {"pergunta": args[0]}
        servico = self.criar(processar)
        id_ = servico.iniciar("Primeira", [], "")
        with self.assertRaises(ConsultaEmAndamento):
            servico.iniciar("Segunda", [], "")
        liberar.set()
        servico.futuro.result(timeout=3)
        self.assertEqual(servico.carregar_resultado(servico.consultar(id_))["pergunta"], "Primeira")

    def test_timeout_e_falha_operacional_nao_viram_resposta_sem_suporte(self):
        def falhar(*args, **kwargs):
            raise TimeoutError("Modelo excedeu o prazo.")
        servico = self.criar(falhar)
        id_ = servico.iniciar("Pergunta", [], "")
        servico.futuro.result(timeout=3)
        self.assertEqual(servico.consultar(id_)["estado"], "falhou")
        self.assertFalse(list((self.raiz / "resultados").glob("*.json")))

    def test_reinicio_marca_processamento_perdido_e_rejeita_caminho_arbitrario(self):
        servico = self.criar(lambda *args, **kwargs: {})
        id_ = servico.iniciar("Pergunta", [], "")
        servico.futuro.result(timeout=3)
        arquivo = servico.pasta / (id_ + ".json")
        estado = servico.consultar(id_)
        estado["estado"] = "em_execucao"
        arquivo.write_text(json.dumps(estado), encoding="utf-8")
        novo = self.criar(lambda *args, **kwargs: {})
        self.assertEqual(novo.consultar(id_)["estado"], "interrompida")
        with self.assertRaises(ValueError):
            novo.consultar("../.env")


if __name__ == "__main__":
    unittest.main()
