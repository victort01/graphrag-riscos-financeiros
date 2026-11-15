import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.execucoes import salvar, carregar_ultima


class ArquivoDeExecucoes(unittest.TestCase):
    def test_reabre_ultima_sem_sobrescrever_historico_ou_versao_original(self):
        with TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            self.assertIsNone(carregar_ultima(pasta))
            anterior = {"pergunta": "Pergunta anterior", "data_utc": "2025-01-01", "versao_execucao": {"hash": "antigo"}}
            atual = {**anterior, "pergunta": "Como são descritas as exportações?"}
            primeiro = salvar(anterior, pasta)
            segundo = salvar(atual, pasta)
            self.assertNotEqual(primeiro, segundo)
            self.assertTrue(primeiro.exists())
            self.assertEqual(carregar_ultima(pasta), atual)
            self.assertEqual(len(list(pasta.glob("*.json"))), 2)
            self.assertFalse(list(pasta.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
