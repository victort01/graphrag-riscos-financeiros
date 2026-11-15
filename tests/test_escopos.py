"""Casos sintéticos de escopo jurídico nas travessias financeiras."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.banco import Banco
from riscos.caminhos import enriquecer
from riscos.esquema import migrar


@unittest.skipUnless(os.getenv("TESTAR_NEO4J") == "1", "requer banco do projeto em modo de ingestão")
class ConsistenciaDeEscopo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banco = Banco()
        migrar(cls.banco)

    def setUp(self):
        self.limpar()

    def limpar(self):
        self.banco.transacao([("MATCH (n:TesteEscopo) DETACH DELETE n", {})])

    def tearDown(self):
        self.limpar()

    def consultar(self, escopo1, escopo2, mesmo_trecho=False, dois_documentos=True):
        texto1 = "A companhia possui financiamento de exportação com condições contratuais definidas."
        texto2 = "O financiamento de exportação é denominado em dólares americanos (USD)."
        self.banco.transacao([("""CREATE
          (e:Empresa:Entidade:TesteEscopo {id:'empresa:00000000000200',empresa_id:'00000000000200',nome:'Emissor sintético',aliases:[]}),
          (o:ObrigacaoFinanceira:Entidade:TesteEscopo {id:'teste-escopo-obrigacao',nome:'financiamento de exportação',aliases:[]}),
          (m:Moeda:Entidade:TesteEscopo {id:'teste-escopo-moeda',nome:'USD',aliases:['dólar americano']}),
          (d1:Documento:TesteEscopo {id:'teste-escopo-doc1',empresa:'Emissor sintético',data_referencia:'2025-12-31',tipo:'dfp',versao:'1',vigente:true,url:'https://example.org/dfp.pdf'}),
          (d2:Documento:TesteEscopo {id:'teste-escopo-doc2',empresa:'Emissor sintético',data_referencia:'2025-12-31',tipo:'fre',versao:'1',vigente:true,url:'https://example.org/fre.pdf'}),
          (t1:Trecho:TesteEscopo {id:'teste-escopo-t1',documento_id:'teste-escopo-doc1',texto:$texto1,pagina_inicio:1,pagina_fim:1}),
          (t2:Trecho:TesteEscopo {id:'teste-escopo-t2',texto:$texto2,pagina_inicio:2,pagina_fim:2}),
          (c1:Declaracao:TesteEscopo {id:'teste-escopo-c1',predicado:'TEM_OBRIGACAO',empresa_id:'00000000000200',periodo:'2025-12-31',escopo:$escopo1,evidencia:$citacao1,condicoes:''}),
          (c2:Declaracao:TesteEscopo {id:'teste-escopo-c2',predicado:'DENOMINADO_EM',empresa_id:'00000000000200',periodo:'2025-12-31',escopo:$escopo2,evidencia:$texto2,condicoes:''}),
          (d1)-[:REFERE_SE_A]->(e),(d2)-[:REFERE_SE_A]->(e),
          (t1)-[:PERTENCE_A]->(d1),
          (c1)-[:SUJEITO]->(e),(c1)-[:OBJETO]->(o),(c1)-[:EVIDENCIADA_POR]->(t1),
          (c2)-[:SUJEITO]->(o),(c2)-[:OBJETO]->(m),
          (e)-[:TEM_DECLARACAO]->(c1),(e)-[:TEM_DECLARACAO]->(c2),
          (e)-[:TEM_OBRIGACAO {declaracao_id:'teste-escopo-c1',empresa_id:'00000000000200',periodo:'2025-12-31',vigente:true}]->(o),
          (o)-[:DENOMINADO_EM {declaracao_id:'teste-escopo-c2',empresa_id:'00000000000200',periodo:'2025-12-31',vigente:true}]->(m)
          WITH *,CASE WHEN $mesmo_trecho THEN t1 ELSE t2 END AS origem2,
                 CASE WHEN $dois_documentos THEN d2 ELSE d1 END AS documento2
          CREATE (t2)-[:PERTENCE_A]->(documento2),(c2)-[:EVIDENCIADA_POR]->(origem2)
          SET t2.documento_id=documento2.id,c1.documento_id=d1.id,c1.trecho_id=t1.id,
              c2.documento_id=CASE WHEN $mesmo_trecho THEN d1.id ELSE documento2.id END,c2.trecho_id=origem2.id""",
            {"texto1": texto1 + (" " + texto2 if mesmo_trecho else ""), "citacao1": texto1, "texto2": texto2,
             "escopo1": escopo1, "escopo2": escopo2, "mesmo_trecho": mesmo_trecho, "dois_documentos": dois_documentos})])
        return enriquecer("Em que moeda o financiamento é denominado (USD)?", {"trechos": [{"id": "teste-escopo-t1"}]}, self.banco)

    def test_nao_conecta_controladora_a_consolidado(self):
        grafo = self.consultar("controladora", "consolidado")
        self.assertFalse(any(p["saltos"] == 2 for p in grafo["caminhos"]))
        self.assertNotIn("teste-escopo-t2", [e["trecho_id"] for e in grafo["evidencias"]])

    def test_mesmo_escopo_explicito_permite_cruzar_documentos(self):
        grafo = self.consultar("consolidado", "consolidado")
        self.assertTrue(any(p["saltos"] == 2 and p["escopo"] == "consolidado" for p in grafo["caminhos"]))
        self.assertEqual({e["documento_id"] for e in grafo["evidencias"]}, {"teste-escopo-doc1", "teste-escopo-doc2"})
        self.assertIn("teste-escopo-t2", grafo["trechos_adicionais"])

    def test_escopo_desconhecido_nao_cruza_blocos_mesmo_no_mesmo_documento(self):
        grafo = self.consultar("nao_especificado", "nao_especificado", dois_documentos=False)
        self.assertFalse(any(p["saltos"] == 2 for p in grafo["caminhos"]))

    def test_escopo_desconhecido_preserva_relacoes_do_mesmo_trecho(self):
        grafo = self.consultar("nao_especificado", "nao_especificado", mesmo_trecho=True, dois_documentos=False)
        self.assertTrue(any(p["saltos"] == 2 for p in grafo["caminhos"]))
        self.assertEqual({e["trecho_id"] for e in grafo["evidencias"]}, {"teste-escopo-t1"})


if __name__ == "__main__":
    unittest.main()
