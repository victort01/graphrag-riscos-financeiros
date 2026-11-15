import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.caminhos import sem_prefixos_redundantes


class TestCompactacao(unittest.TestCase):
    def caminho(self, id_, relacoes, escopo="consolidado"):
        return {"id": id_, "escopo": escopo, "relacoes": [{"id": r} for r in relacoes]}

    def test_remove_prefixo_sem_perder_arestas_de_evidencia(self):
        caminhos = [self.caminho("curto", ["r1"]), self.caminho("longo", ["r1", "r2"]),
            self.caminho("duplicado", ["r1", "r2"])]
        selecionados = sem_prefixos_redundantes(caminhos)
        self.assertEqual([p["id"] for p in selecionados], ["longo"])
        self.assertEqual({r["id"] for p in selecionados for r in p["relacoes"]}, {"r1", "r2"})

    def test_preserva_outra_evidencia_e_outro_escopo(self):
        caminhos = [self.caminho("um", ["r1"]), self.caminho("dois", ["r3", "r4"]),
            self.caminho("tres", ["r1", "r2"], "controladora")]
        self.assertEqual(len(sem_prefixos_redundantes(caminhos)), 3)


if __name__ == "__main__":
    unittest.main()
