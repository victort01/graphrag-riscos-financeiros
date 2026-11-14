import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.extracao import extrair
from riscos.identidade import entidade
from riscos.segmentacao import segmentar


class TestExtracao(unittest.TestCase):
    fonte = {"id": "companhia-teste-2025", "empresa": "Companhia Exemplo",
             "identificacao_cvm": {"CNPJ_CIA": "00.000.000/0001-00"}, "data_referencia": "2025-12-31"}

    def extrair_texto(self, texto):
        trecho = {"id": "trecho-teste", "sha256": "hash-teste", "natureza": "narrativa",
                  "recorte": False, "texto": texto}
        return extrair(trecho, self.fonte)

    def test_negacao_preserva_ausencia_de_relacao_positiva(self):
        _, _, declaracoes = self.extrair_texto("A Companhia não contrata instrumentos financeiros Zero Cost Collar para exposição cambial líquida.")
        self.assertFalse(declaracoes)

    def test_acc_com_procedencia(self):
        _, _, declaracoes = self.extrair_texto("A Companhia mantém empréstimos em moeda estrangeira (ACC) para fazer frente às variações do saldo de clientes de exportações.")
        self.assertTrue(any(d["predicado"] == "COMPENSA_VARIACOES_DE" for d in declaracoes))
        self.assertTrue(all(d["trecho_id"] == "trecho-teste" for d in declaracoes))

    def test_continuacao_de_frase(self):
        doc = {"documento_id": "teste", "sha256": "teste", "paginas": [
            {"pagina_pdf": 1, "texto": "A Companhia mantém empréstimos em moeda estrangeira (ACC) que tem por objetivo\n\nfazer frente às variações do saldo de clientes de exportações."}]}
        trechos = segmentar(doc)
        self.assertEqual(len(trechos), 1)
        self.assertEqual(len(trechos[0]["origens"]), 2)
        _, _, declaracoes = self.extrair_texto(trechos[0]["texto"])
        self.assertTrue(any(d["predicado"] == "COMPENSA_VARIACOES_DE" for d in declaracoes))

    def test_identidades_preservam_companhia_e_alias(self):
        self.assertEqual(entidade("Moeda", "USD", "A")["id"], entidade("Moeda", "dólar americano", "B")["id"])
        self.assertNotEqual(entidade("MedidaProtecao", "swap de juros", "A")["id"],
                            entidade("MedidaProtecao", "swap de juros", "B")["id"])
