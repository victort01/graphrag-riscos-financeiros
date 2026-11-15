import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from riscos.revisao_respostas import preparar, comparar, validar


class RevisaoSemantica(unittest.TestCase):
    def setUp(self):
        r = {"estado": "concluida", "uso": "Teste sintético", "linhas": [{"erro": None, "pergunta_id": "T1", "metodo": "vetorial",
             "pergunta": "Há obrigação?", "resposta": {"afirmacoes": []},
             "contexto_enviado": {"fontes": {}, "caminhos": []}}]}
        self.lote, self.mapa = preparar(r)

    def concluida(self, nome):
        r = copy.deepcopy(self.lote)
        r["revisor"] = nome
        r["itens"][0]["revisao"] = {"estado": "concluida", "cobertura_pergunta": "nenhuma", "abstencao_adequada": "indeterminavel"}
        return r

    def test_pendente_nao_produz_concordancia(self):
        with self.assertRaises(ValueError):
            comparar(self.lote, self.lote, self.lote)
        self.assertNotIn("metodo", self.lote["itens"][0])

    def test_alteracao_de_conteudo_e_mesma_pessoa_sao_recusadas(self):
        a, b = self.concluida("Ana"), self.concluida("Beto")
        b["itens"][0]["fontes"] = {"E9": {"texto": "Fonte acrescentada"}}
        with self.assertRaisesRegex(ValueError, "imutável"):
            validar(b, self.lote)
        with self.assertRaisesRegex(ValueError, "distintas"):
            comparar(a, a, self.lote)

    def test_divergencia_de_abstencao_exige_adjudicacao(self):
        a, b = self.concluida("Ana"), self.concluida("Beto")
        b["itens"][0]["revisao"]["abstencao_adequada"] = "indevida"
        r = comparar(a, b, self.lote)
        self.assertTrue(r["adjudicacao_pendente"])
        self.assertEqual(len(r["divergencias"]), 1)
