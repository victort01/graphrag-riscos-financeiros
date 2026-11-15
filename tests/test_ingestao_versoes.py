"""Publicação e rollback de versões sintéticas no banco exclusivo do projeto."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.banco import Banco
from riscos.caminhos import enriquecer
from riscos.embeddings import IDENTIFICADOR
from riscos.esquema import migrar
from riscos.extracao import extrair
from riscos.identidade import GLOBAIS
from riscos.ingestao import PIPELINE, publicar
from riscos.recuperacao import FILTROS
from riscos.segmentacao import segmentar


def amostra(versao=1, substitui=None):
    fonte = {"id": f"teste-versionamento-v{versao}", "empresa": "Empresa sintética para testes",
        "identificacao_cvm": {"CNPJ_CIA": "00.000.000/0001-00"}, "tipo": "demonstracoes_financeiras_anuais",
        "data_referencia": "2025-12-31", "exercicio_principal": 2025, "versao_declarada_cvm": str(versao),
        "sha256": "f" * 64, "url": "https://example.org/fixture-sintetica.pdf"}
    if substitui:
        fonte["substitui"] = substitui
    documento = {"documento_id": fonte["id"], "sha256": fonte["sha256"], "paginas": [{"pagina_pdf": 1,
        "texto": "A Companhia mantém empréstimos em moeda estrangeira (ACC) para fazer frente às variações do saldo de clientes de exportações."}]}
    trechos = segmentar(documento)
    entidades, _, declaracoes = extrair(trechos[0], fonte)
    return {"fonte": fonte, "pipeline": PIPELINE, "trechos": trechos,
            "entidades": entidades, "declaracoes": declaracoes}


@unittest.skipUnless(os.getenv("TESTAR_NEO4J") == "1", "requer banco do projeto em modo de ingestão")
class PublicacaoDeVersoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banco = Banco()
        migrar(cls.banco)

    def setUp(self):
        self.v1 = amostra()
        self.v2 = amostra(2, self.v1["fonte"]["id"])
        self.ids = [f"teste-versionamento-v{i}" for i in (1, 2, 3)]
        self.limpar()

    def limpar(self):
        entidades = [e["id"] for e in self.v1["entidades"] if e["tipo"] not in GLOBAIS]
        self.banco.transacao([
            ("MATCH ()-[r]->() WHERE r.documento_id IN $ids DELETE r", {"ids": self.ids}),
            ("MATCH (n:Declaracao) WHERE n.documento_id IN $ids DETACH DELETE n", {"ids": self.ids}),
            ("MATCH (n:Trecho) WHERE n.documento_id IN $ids DETACH DELETE n", {"ids": self.ids}),
            ("MATCH (n:Documento) WHERE n.id IN $ids DETACH DELETE n", {"ids": self.ids}),
            ("MATCH (n:Entidade) WHERE n.id IN $ids DETACH DELETE n", {"ids": entidades}),
        ])

    def tearDown(self):
        self.limpar()

    def test_mesmo_pdf_preserva_fontes_vetores_e_apenas_nova_versao_na_busca(self):
        publicar(self.banco, self.v1)
        self.banco.transacao([("MATCH (t:Trecho {id:$id}) SET t.embedding=$v,t.modelo_embedding=$modelo",
            {"id": self.v1["trechos"][0]["id"], "v": [1.0] + [0.0]*383, "modelo": IDENTIFICADOR})])
        self.assertEqual(publicar(self.banco, self.v2)["embeddings_preservados"], 1)
        linhas = self.banco.consultar("""MATCH (d:Documento) WHERE d.id IN $ids
            RETURN d.id AS id,d.vigente AS vigente ORDER BY id""", {"ids": self.ids})
        self.assertEqual([l["vigente"] for l in linhas], [False, True])
        origens = self.banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
            WHERE d.id IN $ids RETURN t.documento_id AS declarado,d.id AS origem""", {"ids": self.ids})
        self.assertEqual(len(origens), 2)
        self.assertTrue(all(l["declarado"] == l["origem"] for l in origens))
        consulta = "MATCH (t:Trecho) WHERE t.id IN $ids " + FILTROS + " RETURN d.id AS documento"
        retornadas = self.banco.consultar(consulta, {"ids": [t["id"] for a in (self.v1, self.v2) for t in a["trechos"]],
            "empresas": ["empresa:00000000000100"], "periodo": "2025-12-31"})
        self.assertEqual(retornadas, [{"documento": self.v2["fonte"]["id"]}])
        grafo = enriquecer("Como ACC se relaciona com recebíveis?", {"trechos": self.v2["trechos"]}, self.banco)
        self.assertTrue(any(p["saltos"] == 2 for p in grafo["caminhos"]))
        self.assertTrue(all(e["documento_id"] == self.v2["fonte"]["id"] for e in grafo["evidencias"]))
        antigo = enriquecer("Como ACC se relaciona com recebíveis?", {"trechos": self.v1["trechos"]}, self.banco)
        self.assertFalse(antigo["caminhos"])

    def test_reprocessar_antiga_nao_a_reativa_e_ramificacao_e_recusada(self):
        publicar(self.banco, self.v1)
        publicar(self.banco, self.v2)
        publicar(self.banco, self.v1)
        vigente = self.banco.consultar("MATCH (d:Documento) WHERE d.id IN $ids AND d.vigente RETURN d.id AS id", {"ids": self.ids})
        self.assertEqual(vigente, [{"id": self.v2["fonte"]["id"]}])
        with self.assertRaises(ValueError):
            publicar(self.banco, amostra(3, self.v1["fonte"]["id"]))

    def test_falha_apos_substituicao_faz_rollback_e_reexecucao_nao_duplica(self):
        publicar(self.banco, self.v1)
        banco_real = self.banco
        class BancoComFalha:
            consultar = banco_real.consultar
            def transacao(self, comandos):
                return banco_real.transacao(comandos + [("CREATE (:Documento {id:$duplicado})", {"duplicado": "teste-versionamento-v1"})])
        with self.assertRaises(RuntimeError):
            publicar(BancoComFalha(), self.v2)
        depois = self.banco.consultar("MATCH (d:Documento) WHERE d.id IN $ids RETURN d.id AS id,d.vigente AS vigente", {"ids": self.ids})
        self.assertEqual(depois, [{"id": self.v1["fonte"]["id"], "vigente": True}])
        publicar(self.banco, self.v2)
        publicar(self.banco, self.v2)
        total = self.banco.consultar("MATCH (d:Documento) WHERE d.id IN $ids RETURN count(d) AS total", {"ids": self.ids})
        self.assertEqual(total[0]["total"], 2)


if __name__ == "__main__":
    unittest.main()
