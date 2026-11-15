import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.identidade import entidade, resolver_mencoes


class TestIdentidade(unittest.TestCase):
    def test_sinonimos_por_tipo(self):
        for tipo, nomes in [
            ("Moeda", ["USD", "US$", "dólar americano", "dólares americanos"]),
            ("MedidaProtecao", ["NDF", "NDFs", "Non-Deliverable Forward", "Non-Deliverable Forwards"]),
            ("MedidaProtecao", ["Zero Cost Collar", "ZCC", "ZCCs"]),
            ("ObrigacaoFinanceira", ["ACC", "ACCs", "Adiantamento sobre Contrato de Câmbio"]),
        ]:
            with self.subTest(tipo=tipo, nomes=nomes):
                self.assertEqual(len({entidade(tipo, nome, "cnpj-a")["id"] for nome in nomes}), 1)

    def test_instrumentos_de_companhias_distintas(self):
        self.assertNotEqual(entidade("MedidaProtecao", "NDF", "cnpj-a")["id"],
                            entidade("MedidaProtecao", "NDF", "cnpj-b")["id"])

    def test_finalidades_distintas(self):
        self.assertNotEqual(entidade("MedidaProtecao", "swap", "cnpj-a", "juros CDI")["id"],
                            entidade("MedidaProtecao", "swap", "cnpj-a", "câmbio USD/BRL")["id"])

    def test_mencao_ambigua_requer_revisao(self):
        self.assertTrue(entidade("Moeda", "dólar", "cnpj-a")["revisao_identidade"])
        self.assertTrue(entidade("MedidaProtecao", "swap", "cnpj-a")["revisao_identidade"])
        self.assertFalse(entidade("Moeda", "dólar americano", "cnpj-a")["revisao_identidade"])

    def test_resolucao_contextual_com_candidato_unico(self):
        generica = entidade("MedidaProtecao", "swap", "cnpj-a")
        especifica = entidade("MedidaProtecao", "swap de juros", "cnpj-a")
        entidades = {e["id"]: e for e in [generica, especifica]}
        mencoes = [{"entidade_id": generica["id"]}]
        resolver_mencoes(entidades, mencoes)
        self.assertNotIn(generica["id"], entidades)
        self.assertEqual(mencoes[0]["entidade_id"], especifica["id"])

    def test_ambiguidade_com_dois_objetivos(self):
        entidades = {e["id"]: e for e in [
            entidade("MedidaProtecao", "swap", "cnpj-a"),
            entidade("MedidaProtecao", "swap de juros", "cnpj-a"),
            entidade("MedidaProtecao", "swap de câmbio", "cnpj-a")]}
        resolver_mencoes(entidades, [])
        self.assertTrue(any(e["revisao_identidade"] for e in entidades.values()))
