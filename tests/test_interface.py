"""Fluxos da tela sem depender da disponibilidade do modelo ou do banco."""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.intencao import FiltrosIncompativeis


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "requer requirements-ui.txt")
class FluxosDaInterface(unittest.TestCase):
    def abrir(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()

    def test_pergunta_vazia_nao_consulta_backend(self):
        with patch("riscos.respostas.responder") as backend:
            app = self.abrir()
            app.button[0].click().run()
            backend.assert_not_called()
            self.assertIn("Escreva uma pergunta", app.warning[0].value)
            self.assertFalse(app.exception)

    def test_falha_do_backend_e_explicita(self):
        with patch("riscos.respostas.responder", side_effect=ConnectionError("modelo indisponível")):
            app = self.abrir()
            app.text_input[0].set_value("Como a Irani descreve o ACC?")
            app.button[0].click().run()
            self.assertIn("não foi concluída", app.error[0].value)
            self.assertFalse(app.exception)

    def test_filtros_incompativeis_solicitam_correcao(self):
        with patch("riscos.respostas.responder", side_effect=FiltrosIncompativeis("Ajuste a empresa selecionada.")):
            app = self.abrir()
            app.text_input[0].set_value("Como a Suzano descreve a dívida?")
            app.button[0].click().run()
            self.assertIn("Ajuste a empresa", app.warning[0].value)
            self.assertFalse(app.exception)

    def test_abstencao_sem_evidencias_e_arquivada_e_exibida(self):
        resultado = {"pergunta": "Há documentos de 2023?", "data_utc": "2026-11-15T00:00:00+00:00",
            "resposta": {"afirmacoes": [], "possivel_conflito": False,
                "confianca": {"nivel": "sem suporte", "motivo": "Não há documentos para o exercício."}, "validacao": {}},
            "grafo": {"caminhos": [], "evidencias": [], "rastreio": {}},
            "contexto_enviado": {"fontes": {}, "caminhos": []},
            "recuperacao": {"rastreio": {}}, "modelo_resposta": {}}
        with patch("riscos.respostas.responder", return_value=resultado), patch("riscos.execucoes.salvar") as arquivo:
            app = self.abrir()
            app.text_input[0].set_value(resultado["pergunta"])
            app.button[0].click().run()
            arquivo.assert_called_once_with(resultado)
            self.assertTrue(any("Não foi possível sustentar" in m.value for m in app.markdown))
            self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
