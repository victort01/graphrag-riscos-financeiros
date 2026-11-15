import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.respostas import validar_resposta, concluir, completar_procedencia, filtrar_pertinencia


class ValidacaoResposta(unittest.TestCase):
    def setUp(self):
        self.contexto = {"fontes": {"E1": {"texto": "A dívida de 100 está denominada em USD.", "periodo": "2025-12-31"}}}

    def test_rejeita_fonte_inventada(self):
        resposta = {"afirmacoes": [{"texto": "Há dívida.", "fontes": ["E2"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_rejeita_valor_inventado(self):
        resposta = {"afirmacoes": [{"texto": "A dívida é 900.", "fontes": ["E1"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_rejeita_protecao_absoluta(self):
        resposta = {"afirmacoes": [{"texto": "A companhia tem proteção total.", "fontes": ["E1"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_negacao_na_fonte_nao_sustenta_conclusao_positiva(self):
        self.contexto["fontes"]["E1"]["texto"] = "As operações não asseguram proteção total."
        resposta = {"afirmacoes": [{"texto": "Existe proteção total.", "fontes": ["E1"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_preserva_conclusao_negativa_sobre_protecao_total(self):
        self.contexto["fontes"]["E1"]["texto"] = "As operações não asseguram proteção total."
        resposta = {"afirmacoes": [{"texto": "As operações não asseguram proteção total.", "fontes": ["E1"]}], "cobertura": "direta"}
        self.assertFalse(validar_resposta(resposta, self.contexto))

    def test_conflito_limita_confianca(self):
        resposta = {"afirmacoes": [{"texto": "Há dívida em USD.", "fontes": ["E1"]}],
                    "cobertura": "direta", "possivel_conflito": True}
        self.assertEqual(concluir(resposta, self.contexto, [])["confianca"]["nivel"], "limitada")

    def test_escopo_nao_especificado_limita_confianca_mesmo_com_cobertura_direta(self):
        self.contexto["caminhos"] = [{"id": "C1", "escopo": "nao_especificado"}]
        resposta = {"afirmacoes": [{"texto": "Há obrigação financeira.", "fontes": ["E1"], "caminhos": ["C1"]}],
            "cobertura": "direta", "possivel_conflito": False}
        final = concluir(resposta, self.contexto, [])
        self.assertEqual(final["confianca"]["nivel"], "limitada")
        self.assertIn("Escopo jurídico", final["confianca"]["motivo"])
        resposta["cobertura"] = "parcial"
        motivo = concluir(resposta, self.contexto, [])["confianca"]["motivo"]
        self.assertIn("Cobertura parcial", motivo)
        self.assertIn("Escopo jurídico", motivo)

    def test_criterio_de_escopo_tambem_vale_sem_caminho_de_grafo(self):
        resposta = {"afirmacoes": [{"texto": "Há dívida em USD.", "fontes": ["E1"], "caminhos": []}],
            "cobertura": "direta", "possivel_conflito": False}
        self.assertEqual(concluir(resposta, self.contexto, [])["confianca"]["nivel"], "limitada")
        self.contexto["fontes"]["E1"]["escopos"] = ["consolidado"]
        self.assertEqual(concluir(resposta, self.contexto, [])["confianca"]["nivel"], "moderada")

    def test_atribuicao_a_controladora_exige_qualificacao_inclusive_negativa(self):
        for texto in ("A controladora tem dívida em USD.", "A controladora não tem dívida em USD."):
            resposta = {"afirmacoes": [{"texto": texto, "fontes": ["E1"], "caminhos": []}], "cobertura": "direta"}
            self.assertTrue(any("escopo" in e for e in validar_resposta(resposta, self.contexto)))
        self.contexto["fontes"]["E1"]["escopos"] = ["consolidado"]
        self.assertTrue(any("escopo" in e for e in validar_resposta(resposta, self.contexto)))
        self.contexto["fontes"]["E1"]["escopos"] = ["controladora"]
        resposta["afirmacoes"][0]["texto"] = "A controladora tem dívida em USD."
        self.assertFalse(any("escopo" in e for e in validar_resposta(resposta, self.contexto)))

    def test_falha_produz_abstencao(self):
        resultado = concluir({"afirmacoes": [], "cobertura": "insuficiente"}, self.contexto, ["Fonte inválida"])
        self.assertEqual(resultado["confianca"]["nivel"], "sem suporte")
        self.assertEqual(resultado["afirmacoes"], [])

    def test_numero_nao_pode_ser_substring(self):
        self.contexto["fontes"]["E1"]["texto"] = "A dívida é de 1900."
        resposta = {"afirmacoes": [{"texto": "A dívida é 900.", "fontes": ["E1"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_rejeita_caminho_inventado(self):
        resposta = {"afirmacoes": [{"texto": "Há dívida.", "fontes": ["E1"], "caminhos": ["C9"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_caminho_exige_fontes_de_todas_as_arestas(self):
        self.contexto["caminhos"] = [{"id": "C1", "fontes": ["E1", "E2"], "relacoes": ["A", "B"]}]
        resposta = {"afirmacoes": [{"texto": "Há dívida.", "fontes": ["E1"], "caminhos": ["C1"]}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto))

    def test_conexao_exige_citacao_multi_hop_disponivel(self):
        self.contexto["caminhos"] = [{"id": "C1", "fontes": ["E1"], "relacoes": ["A", "B"]}]
        resposta = {"afirmacoes": [{"texto": "Há dívida.", "fontes": ["E1"], "caminhos": []}], "cobertura": "direta"}
        self.assertTrue(validar_resposta(resposta, self.contexto, "Como a dívida se relaciona com a moeda?"))

    def test_resolve_fontes_do_caminho_sem_alterar_texto_original(self):
        contexto = {"caminhos": [{"id": "C1", "fontes": ["E1", "E2"]}]}
        original = {"afirmacoes": [{"texto": "Texto a conferir.", "fontes": ["E1"], "caminhos": ["C1"]}]}
        normalizada, complementos = completar_procedencia(original, contexto)
        self.assertEqual(normalizada["afirmacoes"][0]["fontes"], ["E1", "E2"])
        self.assertEqual(original["afirmacoes"][0]["fontes"], ["E1"])
        self.assertEqual(normalizada["afirmacoes"][0]["texto"], original["afirmacoes"][0]["texto"])
        self.assertTrue(complementos)

    def test_filtra_contextualizacao_sem_conceito_perguntado(self):
        original = {"afirmacoes": [{"texto": "O ACC se relaciona com exportações."},
                                   {"texto": "A conversão contábil ocorre na data da transação."}], "cobertura": "direta"}
        filtrada, removidas = filtrar_pertinencia(original, "Como ACC se relaciona com recebíveis?")
        self.assertEqual(removidas, [2])
        self.assertEqual(len(filtrada["afirmacoes"]), 1)
        self.assertEqual(filtrada["cobertura"], "parcial")
        self.assertEqual(len(original["afirmacoes"]), 2)


if __name__ == "__main__":
    unittest.main()
