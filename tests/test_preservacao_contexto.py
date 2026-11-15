"""Uma conexão adicional não pode remover uma negativa já recuperada."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.respostas import combinar_contextos


class PreservacaoDeContexto(unittest.TestCase):
    def test_fonte_negativa_permanece_quando_caminho_nao_cabe(self):
        fonte = {"trecho_id": "negativa", "texto": "A Companhia não adota hedge accounting."}
        base = {"fontes": {"E1": fonte}, "caminhos": []}
        grafo = {"fontes": {"E1": {"trecho_id": "outro", "texto": "x" * 600}},
                 "caminhos": [{"id": "C1", "relacoes": ["ADOTA_PROTECAO"], "fontes": ["E1"]}]}
        final = combinar_contextos(base, grafo, len(json.dumps(base, ensure_ascii=False)) + 50)
        self.assertEqual(final, base)

    def test_resolve_ids_sem_trocar_fontes_ao_acrescentar_caminho(self):
        base = {"fontes": {"E1": {"trecho_id": "negativa", "texto": "Não adota."}}, "caminhos": []}
        grafo = {"fontes": {"E1": {"trecho_id": "operacao", "texto": "Mantém ACC."}},
                 "caminhos": [{"id": "C1", "relacoes": ["TEM_OBRIGACAO", "COMPENSA_VARIACOES_DE"], "fontes": ["E1"]}]}
        final = combinar_contextos(base, grafo)
        self.assertEqual(final["fontes"]["E1"], base["fontes"]["E1"])
        self.assertEqual(final["caminhos"][0]["fontes"], ["E2"])
        self.assertEqual(final["fontes"]["E2"]["trecho_id"], "operacao")
        self.assertEqual(grafo["caminhos"][0]["fontes"], ["E1"])
