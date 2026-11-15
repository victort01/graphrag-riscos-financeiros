import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from avaliar_recuperacao import recall


class LocalizacaoEvidencias(unittest.TestCase):
    def test_exige_documento_pagina_e_termo(self):
        trecho = {"documento_id": "a", "pagina_inicio": 2, "pagina_fim": 3, "texto": "A variação cambial está descrita."}
        self.assertEqual(recall([trecho], [{"documento_id": "a", "pagina": 3, "termo": "variacao cambial"}]), 1)
        self.assertEqual(recall([trecho], [{"documento_id": "b", "pagina": 3, "termo": "variacao cambial"}]), 0)
        self.assertEqual(recall([trecho], [{"documento_id": "a", "pagina": 4, "termo": "variacao cambial"}]), 0)
        self.assertIsNone(recall([trecho], []))


if __name__ == "__main__":
    unittest.main()
