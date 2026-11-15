import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import avaliar_respostas as avaliador
from riscos.respostas import responder_contexto, esquema_contextual, ESQUEMA


class GeracaoCongelada(unittest.TestCase):
    def test_contratos_de_ids_nao_contaminam_consultas_subsequentes(self):
        antes = json.loads(json.dumps(ESQUEMA))
        sem = esquema_contextual({"fontes": {"E1": {}}, "caminhos": []})
        com = esquema_contextual({"fontes": {"E2": {}}, "caminhos": [{"id": "C7"}]})
        a = sem["properties"]["afirmacoes"]["items"]["properties"]
        b = com["properties"]["afirmacoes"]["items"]["properties"]
        self.assertEqual(a["caminhos"]["maxItems"], 0)
        self.assertEqual(b["caminhos"]["items"]["enum"], ["C7"])
        self.assertEqual(a["fontes"]["items"]["enum"], ["E1"])
        self.assertEqual(b["fontes"]["items"]["enum"], ["E2"])
        self.assertNotIn("maxItems", b["caminhos"])
        self.assertEqual(ESQUEMA, antes)

    def test_sem_fontes_nao_invoca_modelo(self):
        with patch("riscos.respostas.gerar_json") as gerar:
            r = responder_contexto("Há dívida?", {"fontes": {}, "caminhos": []})
        gerar.assert_not_called()
        self.assertEqual(r["resposta"]["cobertura"], "insuficiente")

    def test_preserva_original_e_aplica_as_guardas_de_producao(self):
        bruto = {"afirmacoes": [{"texto": "Há proteção total para juros.", "fontes": ["E1"], "caminhos": []}],
                 "cobertura": "direta", "possivel_conflito": False}
        contexto = {"fontes": {"E1": {"texto": "As operações não asseguram proteção total.", "periodo": "2025-12-31"}}, "caminhos": []}
        with patch("riscos.respostas.gerar_json", return_value=bruto):
            r = responder_contexto("Há proteção para juros?", contexto)
        self.assertEqual(r["resposta_original_modelo"], bruto)
        self.assertEqual(r["resposta"]["afirmacoes"], [])
        self.assertTrue(r["resposta"]["validacao"]["erros"])

    def test_falha_de_inferencia_nao_vira_abstencao_e_retomada_nao_duplica(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            conjunto = base / "perguntas.json"
            conjunto.write_text(json.dumps({"perguntas": [{"id": "T1", "pergunta": "Quais juros?"}]}), encoding="utf-8")
            entrada, saida = base / "entrada.json", base / "saida.json"
            entrada.write_text(json.dumps({"estado": "concluida", "uso": "Teste sintético do avaliador",
                "sha256_conjunto": hashlib.sha256(conjunto.read_bytes()).hexdigest(), "versao_execucao": {},
                "linhas": [{"pergunta_id": "T1", "metodo": "vetorial", "erro": None,
                            "contexto": {"fontes": {}, "caminhos": []}}]}), encoding="utf-8")
            with patch.object(avaliador, "responder_contexto", side_effect=TimeoutError("Modelo indisponível")) as gerar:
                avaliador.executar(entrada, saida, conjunto)
                avaliador.executar(entrada, saida, conjunto, retomar=True)
                gerar.assert_called_once()
            r = json.loads(saida.read_text(encoding="utf-8"))
            self.assertEqual(r["estado"], "concluida_com_falhas")
            self.assertEqual(len(r["linhas"]), 1)
            self.assertEqual(r["linhas"][0]["erro"]["tipo"], "TimeoutError")
            self.assertNotIn("resposta", r["linhas"][0])
            conjunto.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "conjunto"):
                avaliador.executar(entrada, saida, conjunto, retomar=True)
