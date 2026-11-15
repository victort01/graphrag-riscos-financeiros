import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.revisao import comparar


class ComparacaoDeRevisoes(unittest.TestCase):
    def setUp(self):
        self.primeira = {"estado": "revisado", "revisor": "Revisor A", "sha256_selecao": "selecao", "uso": "desenvolvimento",
            "amostras": [{"id": "R01", "estado": "revisado", "documento_id": "documento", "pagina": 1,
                "sha256_pdf": "hash", "texto": "A dívida em USD está sujeita a juros.", "observacoes": "",
                "mencoes": [["Moeda", "USD"]], "relacoes": []}]}
        self.segunda = copy.deepcopy(self.primeira)
        self.segunda["revisor"] = "Revisor B"

    def test_recusa_pendencias_e_revisor_duplicado(self):
        self.segunda["estado"] = "pendente"
        with self.assertRaises(ValueError):
            comparar(self.primeira, self.segunda)
        self.segunda["estado"] = "revisado"
        self.segunda["revisor"] = "Revisor A"
        with self.assertRaises(ValueError):
            comparar(self.primeira, self.segunda)

    def test_relata_divergencia_sem_inventar_gabarito(self):
        self.segunda["amostras"][0]["mencoes"] = []
        resultado = comparar(self.primeira, self.segunda)
        self.assertEqual(resultado["metricas_concordancia"]["ner"]["f1_concordancia"], 0)
        self.assertIsNone(resultado["metricas_concordancia"]["re"]["f1_concordancia"])
        self.assertTrue(resultado["divergencias"][0]["ner"]["somente_revisor_1"])

    def test_recusa_textos_diferentes_e_mencao_ausente(self):
        self.segunda["amostras"][0]["texto"] = "Outro texto."
        with self.assertRaises(ValueError):
            comparar(self.primeira, self.segunda)
        self.segunda["amostras"][0]["texto"] = self.primeira["amostras"][0]["texto"]
        self.segunda["amostras"][0]["mencoes"] = [["Moeda", "BRL"]]
        with self.assertRaises(ValueError):
            comparar(self.primeira, self.segunda)

    def test_rejeicao_justificada_fica_fora_da_concordancia_e_no_relatorio(self):
        self.segunda["amostras"][0].update(estado="rejeitado", observacoes="Contexto insuficiente.")
        resultado = comparar(self.primeira, self.segunda)
        self.assertEqual(resultado["amostras_comparadas"], 0)
        self.assertEqual(len(resultado["amostras_rejeitadas"]), 1)
        self.assertIsNone(resultado["metricas_concordancia"]["ner"]["f1_concordancia"])


if __name__ == "__main__":
    unittest.main()
