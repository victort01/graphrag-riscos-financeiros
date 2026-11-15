import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.respostas import montar_contexto
from riscos.visualizacao import pagina_grafo, rastrear_nos


class ContextoEVisualizacao(unittest.TestCase):
    def test_orcamento_cobre_empresas_antes_de_repetir_mesma_empresa(self):
        fontes = []
        for id_, empresa in [("a1", "Empresa A"), ("a2", "Empresa A"), ("b1", "Empresa B"), ("c1", "Empresa C")]:
            fontes.append({"id": id_, "texto": "X" * 200, "empresa": "Alias da empresa A" if id_ == "a2" else empresa,
                "empresa_canonica_id": "empresa:" + id_[0], "periodo": "2025-12-31",
                "pagina_inicio": 1, "pagina_fim": 1, "documento_id": id_, "url": "https://example.org/doc.pdf"})
        contexto = montar_contexto({"trechos": fontes}, {"caminhos": [], "evidencias": []}, limite_caracteres=1500)
        self.assertEqual({f["empresa"] for f in contexto["fontes"].values()}, {"Empresa A", "Empresa B", "Empresa C"})
        self.assertLessEqual(len(json.dumps(contexto, ensure_ascii=False)), 1500)

    def test_orcamento_inclui_caminhos_e_grafo_mostra_apenas_contexto_enviado(self):
        fontes, caminhos, evidencias = [], [], []
        for i, texto in [(1, "Um financiamento em moeda estrangeira."), (2, "X" * 4000)]:
            fonte = {"id": f"t{i}", "texto": texto, "empresa": "Empresa teste", "periodo": "2025-12-31",
                     "pagina_inicio": i, "pagina_fim": i, "documento_id": f"doc{i}", "url": "https://example.org/fonte.pdf"}
            fontes.append(fonte)
            caminhos.append({"id": f"C{i}", "saltos": 1,
                "nos": [{"id": "empresa", "nome": "Empresa teste", "rotulos": ["Empresa"]},
                        {"id": f"no{i}", "nome": f"conceito_{i}", "rotulos": ["ObrigacaoFinanceira"]}],
                "relacoes": [{"id": f"r{i}", "origem": "empresa", "destino": f"no{i}", "tipo": "TEM_OBRIGACAO", "periodo": "2025-12-31"}]})
            evidencias.append({**fonte, "trecho_id": f"t{i}", "declaracao_id": f"r{i}", "citacao": texto})
        busca, grafo = {"trechos": fontes}, {"caminhos": caminhos, "evidencias": evidencias}
        contexto = montar_contexto(busca, grafo, limite_caracteres=1200)
        self.assertLessEqual(len(json.dumps(contexto, ensure_ascii=False)), 1200)
        self.assertEqual([p["id"] for p in contexto["caminhos"]], ["C1"])
        resultado = {"contexto_enviado": contexto, "grafo": grafo,
                     "resposta": {"afirmacoes": [{"texto": "Afirmação teste", "fontes": ["E1"], "caminhos": ["C1"]}]}}
        pagina = pagina_grafo(resultado)
        self.assertIn('"id": "no1"', pagina)
        self.assertNotIn('"id": "no2"', pagina)
        rastreio = rastrear_nos(resultado)
        self.assertIn("no2", rastreio["nos_financeiros_recuperados"])
        self.assertNotIn("no2", rastreio["nos_financeiros_enviados"])
        self.assertEqual(rastreio["trechos_citados"], {"E1": "t1"})


if __name__ == "__main__":
    unittest.main()
