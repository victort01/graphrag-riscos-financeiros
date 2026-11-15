"""Integração com os seis documentos oficiais previamente ingeridos."""
import sys
import os
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.banco import Banco
from riscos.caminhos import enriquecer
from riscos.respostas import responder


@unittest.skipUnless(os.getenv("TESTAR_CORPUS") == "1", "requer o corpus financeiro ingerido")
class CaminhosFinanceiros(unittest.TestCase):
    def test_acervo_sem_exercicio_produz_abstencao_sem_chamar_modelos(self):
        with patch("riscos.recuperacao.codificar") as embedding, patch("riscos.recuperacao.gerar_json") as cypher, patch("riscos.respostas.gerar_json") as resposta:
            resultado = responder("Quais exposições constam no relatório de 2030?", ["empresa:92791243000103"], "2030-12-31")
        embedding.assert_not_called()
        cypher.assert_not_called()
        resposta.assert_not_called()
        self.assertEqual(resultado["resposta"]["cobertura"], "insuficiente")
        self.assertEqual(resultado["recuperacao"]["rastreio"]["estado"], "sem_documentos_no_filtro")

    def test_acrescenta_evidencia_de_juros_e_preserva_exercicio(self):
        banco = Banco()
        sementes = banco.consultar("""MATCH (c:Declaracao)-[:EVIDENCIADA_POR]->(t:Trecho)
            WHERE c.empresa_id=$empresa AND c.periodo=$periodo AND c.predicado='COMPENSA_VARIACOES_DE'
            RETURN t.id AS id LIMIT 1""", {"empresa": "92791243000103", "periodo": "2025-12-31"})
        self.assertTrue(sementes, "Execute a ingestão do corpus antes deste teste de integração.")
        contexto = enriquecer("Como a Irani protege sua exposição a taxas de juros?", {"trechos": sementes}, banco)
        self.assertTrue(contexto["trechos_adicionais"])
        self.assertTrue(any(p["saltos"] >= 2 for p in contexto["caminhos"]))
        for caminho in contexto["caminhos"]:
            for relacao in caminho["relacoes"]:
                self.assertEqual(relacao["empresa_id"], "92791243000103")
                self.assertEqual(relacao["periodo"], "2025-12-31")
        for evidencia in contexto["evidencias"]:
            self.assertIn(evidencia["citacao"], evidencia["texto"])


if __name__ == "__main__":
    unittest.main()
