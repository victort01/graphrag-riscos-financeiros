"""Fluxos da tela sem depender da disponibilidade do modelo ou do banco."""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "requer requirements-ui.txt")
class FluxosDaInterface(unittest.TestCase):
    def setUp(self):
        self.servico = MagicMock()
        substituicao = patch("riscos.trabalhos.gerenciador", return_value=self.servico)
        substituicao.start()
        self.addCleanup(substituicao.stop)

    def abrir(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()

    def test_pergunta_vazia_nao_consulta_backend(self):
        app = self.abrir()
        app.button[0].click().run()
        self.servico.iniciar.assert_not_called()
        self.assertIn("Escreva uma pergunta", app.warning[0].value)
        self.assertFalse(app.exception)

    def test_falha_do_backend_e_explicita(self):
        self.servico.iniciar.return_value = "consulta-teste"
        self.servico.consultar.return_value = {"estado": "falhou", "pergunta": "Como a Irani descreve o ACC?", "erro": "modelo indisponível"}
        app = self.abrir()
        app.text_input[0].set_value("Como a Irani descreve o ACC?")
        app.button[0].click().run()
        self.assertIn("não foi concluída", app.error[0].value)
        self.assertFalse(app.exception)

    def test_filtros_incompativeis_solicitam_correcao(self):
        app = self.abrir()
        app.text_input[0].set_value("Como a Suzano descreve a dívida?")
        app.button[0].click().run()
        self.assertIn("fora da seleção", app.warning[0].value)
        self.servico.iniciar.assert_not_called()
        self.assertFalse(app.exception)

    def test_abstencao_sem_evidencias_e_arquivada_e_exibida(self):
        resultado = {"pergunta": "Há evidências para esta pergunta?", "data_utc": "2026-11-15T00:00:00+00:00",
            "resposta": {"afirmacoes": [], "possivel_conflito": False,
                "confianca": {"nivel": "sem suporte", "motivo": "Não há documentos para o exercício."}, "validacao": {}},
            "grafo": {"caminhos": [], "evidencias": [], "rastreio": {}},
            "contexto_enviado": {"fontes": {}, "caminhos": []},
            "recuperacao": {"rastreio": {}}, "modelo_resposta": {}}
        self.servico.iniciar.return_value = "consulta-teste"
        self.servico.consultar.return_value = {"estado": "concluida"}
        self.servico.carregar_resultado.return_value = resultado
        app = self.abrir()
        app.text_input[0].set_value(resultado["pergunta"])
        app.button[0].click().run()
        self.servico.iniciar.assert_called_once()
        self.servico.carregar_resultado.assert_called_once()
        self.assertTrue(any("Não foi possível sustentar" in m.value for m in app.markdown))
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
