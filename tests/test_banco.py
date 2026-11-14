"""Verificações operacionais do esquema no banco exclusivo deste projeto."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.banco import Banco
from riscos.esquema import migrar


@unittest.skipUnless(os.getenv("TESTAR_NEO4J") == "1", "requer o Neo4j local do projeto")
class TestEsquema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banco = Banco()
        migrar(cls.banco)

    def tearDown(self):
        self.banco.transacao([("MATCH (n:TesteEsquema) DETACH DELETE n", {})])

    def test_unicidade_e_rollback(self):
        self.banco.transacao([("CREATE (:Empresa:TesteEsquema {id:'teste-empresa'})", {})])
        with self.assertRaises(RuntimeError):
            self.banco.transacao([
                ("CREATE (:Documento:TesteEsquema {id:'teste-rollback'})", {}),
                ("CREATE (:Empresa:TesteEsquema {id:'teste-empresa'})", {}),
            ])
        self.assertEqual(self.banco.consultar("MATCH (n {id:'teste-rollback'}) RETURN count(n) AS total")[0]["total"], 0)

    def test_busca_fulltext_e_vetor(self):
        vetor = [1.0] + [0.0] * 383
        self.banco.transacao([("CREATE (:Trecho:TesteEsquema {id:'teste-texto',texto:$texto,embedding:$vetor})",
                              {"texto": "financiamento cambial dolar", "vetor": vetor})])
        texto = self.banco.consultar("CALL db.index.fulltext.queryNodes('trechos_texto','financiamento') "
                                     "YIELD node,score WHERE node.id='teste-texto' RETURN score")
        semantica = self.banco.consultar("CALL db.index.vector.queryNodes('trechos_vetor',5,$v) "
                                         "YIELD node,score WHERE node.id='teste-texto' RETURN score", {"v": vetor})
        self.assertTrue(texto)
        self.assertGreater(semantica[0]["score"], 0.99)

    def test_multi_hop_com_procedencia(self):
        self.banco.transacao([("""CREATE (e:Empresa:TesteEsquema {id:'teste-cnpj'}),
            (o:ObrigacaoFinanceira:TesteEsquema {id:'teste-divida',nome:'financiamento de exportacao'}),
            (m:Moeda:TesteEsquema {id:'teste-usd',nome:'USD'}),
            (d:Declaracao:TesteEsquema {id:'teste-relacao',periodo:'2024-12-31'}),
            (t:Trecho:TesteEsquema {id:'teste-evidencia',documento_id:'suzano-dfp-2024',pagina_inicio:40}),
            (e)-[:TEM_OBRIGACAO {declaracao_id:'teste-relacao'}]->(o),
            (o)-[:DENOMINADO_EM {declaracao_id:'teste-relacao'}]->(m),
            (d)-[:EVIDENCIADA_POR]->(t)""", {})])
        linhas = self.banco.consultar("""MATCH (e:Empresa {id:'teste-cnpj'})-[:TEM_OBRIGACAO]->
            (o:ObrigacaoFinanceira)-[:DENOMINADO_EM]->(m:Moeda)
            RETURN o.nome AS obrigacao,m.nome AS moeda""")
        self.assertEqual(linhas[0]["moeda"], "USD")


if __name__ == "__main__":
    unittest.main()
