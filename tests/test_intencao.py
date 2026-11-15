import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.intencao import reconciliar, FiltrosIncompativeis


class FiltrosDaPergunta(unittest.TestCase):
    def test_infere_empresa_e_exercicio_explicitos(self):
        self.assertEqual(reconciliar("Quais proteções a Irani declara em 2025?"), (["empresa:92791243000103"], "2025-12-31"))

    def test_rejeita_empresa_incompativel(self):
        with self.assertRaises(FiltrosIncompativeis):
            reconciliar("Como a Suzano protege receitas?", ["empresa:92791243000103"], "2025-12-31")

    def test_comparacao_temporal_exige_filtros_compativeis(self):
        with self.assertRaises(FiltrosIncompativeis):
            reconciliar("Como mudou entre 2024 e 2025?", None, "2025-12-31")

    def test_preserva_selecao_sem_mencoes(self):
        self.assertEqual(reconciliar("Quais obrigações foram declaradas?", ["empresa:92791243000103"], "2024-12-31"),
                         (["empresa:92791243000103"], "2024-12-31"))

    def test_montante_nao_e_ano(self):
        self.assertEqual(reconciliar("O que representa R$ 2025?", None, "2024-12-31"), (None, "2024-12-31"))


if __name__ == "__main__":
    unittest.main()
