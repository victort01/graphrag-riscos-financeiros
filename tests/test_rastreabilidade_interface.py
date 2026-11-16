"""A aba de rastreabilidade expõe o Cypher gerado e os nós consultados fora do JSON bruto."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.visualizacao import cypher_gerado, nos_consultados


def resultado(cypher=None):
    nos = [{"id": "e", "nome": "Irani", "rotulos": ["Entidade", "Empresa"]},
           {"id": "a", "nome": "ACC", "rotulos": ["Entidade", "ObrigacaoFinanceira"]},
           {"id": "r", "nome": "recebíveis de exportações", "rotulos": ["Entidade", "FluxoFinanceiro"]},
           {"id": "u", "nome": "USD", "rotulos": ["Entidade", "Moeda"]}]
    rastreio = {"vetorial": "CALL ..."}
    if cypher:
        rastreio["cypher_llm"] = cypher
    return {"recuperacao": {"rastreio": rastreio},
            "grafo": {"caminhos": [{"id": "C1", "nos": nos[:3]}, {"id": "C2", "nos": [nos[0], nos[3]]}]},
            "contexto_enviado": {"caminhos": [{"id": "C1"}], "fontes": {"E1": {"trecho_id": "t1"}}},
            "resposta": {"afirmacoes": [{"texto": "x", "fontes": ["E1"], "caminhos": ["C1"]}]}}


class RastreabilidadeVisivel(unittest.TestCase):
    def test_nos_ordenados_por_uso_com_tipo(self):
        linhas = nos_consultados(resultado())
        self.assertEqual([(l["Nó"], l["Situação"]) for l in linhas],
                         [("ACC", "citado na resposta"), ("Irani", "citado na resposta"),
                          ("recebíveis de exportações", "citado na resposta"), ("USD", "recuperado, fora do contexto")])
        self.assertEqual(linhas[0]["Tipo"], "ObrigacaoFinanceira")

    def test_cypher_gerado_ou_ausente(self):
        self.assertEqual(cypher_gerado(resultado("MATCH (t:Trecho) RETURN t.id")), "MATCH (t:Trecho) RETURN t.id")
        self.assertIsNone(cypher_gerado(resultado()))


if __name__ == "__main__":
    unittest.main()
