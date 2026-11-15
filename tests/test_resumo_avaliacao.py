"""Falhas não entram como acerto de abstenção nem somem do resumo."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("resumo", Path(__file__).resolve().parents[1] / "scripts/resumir_avaliacao.py")
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)


class ResumoAvaliacao(unittest.TestCase):
    def test_falha_tecnica_e_controle_nao_inflam_as_metricas(self):
        conjunto = {"uso": "teste sintético", "perguntas": [
            {"id": "A", "evidencias": [{}], "abstencao_esperada": False},
            {"id": "B", "evidencias": [{}], "proximidade_desenvolvimento": True, "abstencao_esperada": False},
            {"id": "C", "evidencias": [], "abstencao_esperada": True}]}
        linhas = [{"pergunta_id": "A", "metodo": "vetorial", "erro": None, "recall_contexto": 0, "recall_candidatos": 1},
                  {"pergunta_id": "B", "metodo": "vetorial", "erro": None, "recall_contexto": 1, "recall_candidatos": 1},
                  {"pergunta_id": "C", "metodo": "vetorial", "erro": "timeout"}]
        recuperacao = {"linhas": linhas, "estado": "concluida_com_falhas", "sha256_conjunto": "teste", "versao_execucao": {}}
        respostas = {"linhas": [{"pergunta_id": "C", "metodo": "vetorial", "erro": "timeout"}],
                     "estado": "concluida_com_falhas", "versao_geracao": {}}
        r = modulo.resumir(conjunto, recuperacao, respostas)["variantes"]["vetorial"]
        self.assertEqual(r["falhas_recuperacao"], 1)
        self.assertEqual(r["recuperacao"]["com_evidencia"]["recall_contexto_macro"], .5)
        self.assertEqual(r["recuperacao"]["sem_controles_desenvolvimento"]["recall_contexto_macro"], 0)
        self.assertEqual(r["geracao"]["falhas"], 1)
        self.assertEqual(r["geracao"]["abstencoes_nesses_casos"], 0)
