import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.consultas import validar_consulta
from riscos.recuperacao import combinar


class ContratoConsultas(unittest.TestCase):
    def test_escrita_rejeitada_antes_do_banco(self):
        banco = Mock()
        for consulta in ("MATCH (n) DELETE n RETURN n.id AS trecho_id LIMIT 1",
                         "CALL db.labels()", "MATCH (n) RETURN n.id AS trecho_id LIMIT 1; MATCH (x) RETURN x"):
            with self.assertRaises(ValueError):
                validar_consulta(banco, consulta, {})
        banco.transacao.assert_not_called()

    def test_lista_nao_e_id(self):
        banco = Mock()
        with self.assertRaisesRegex(ValueError, "lista"):
            validar_consulta(banco, "MATCH (e:Empresa {id:$empresas}) RETURN e.id AS trecho_id LIMIT 1", {})
        banco.transacao.assert_not_called()

    def test_relacao_de_protecao_nao_leva_a_trecho(self):
        banco = Mock()
        with self.assertRaisesRegex(ValueError, "Tipos inválidos"):
            validar_consulta(banco, "MATCH (m:MedidaProtecao)-[:PROTEGE]->(t:Trecho) "
                             "WHERE m.id IN $empresas AND t.periodo=$periodo RETURN t.id AS trecho_id LIMIT 1", {})
        banco.transacao.assert_not_called()

    def test_operador_desconhecido_rejeitado(self):
        banco = Mock()
        banco.transacao.return_value = [{"plano": {"root": {"operatorType": "ProcedureCall@neo4j", "children": []}}}]
        with self.assertRaisesRegex(ValueError, "Operador"):
            validar_consulta(banco, "MATCH (t:Trecho) WHERE t.id IN $empresas AND t.periodo=$periodo "
                             "RETURN t.id AS trecho_id LIMIT 1", {})

    def test_rrf_deduplica_e_preserva_contribuicoes(self):
        resultado = combinar([("vetor", [{"id": "a"}, {"id": "b"}]), ("texto", [{"id": "b"}])])
        self.assertEqual([r["id"] for r in resultado], ["b", "a"])
        self.assertEqual(resultado[0]["metodos"], ["vetor", "texto"])


if __name__ == "__main__":
    unittest.main()
