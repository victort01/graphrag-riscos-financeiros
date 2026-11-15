import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from riscos.versoes import metadados, validar_publicacao, hash_fonte
from riscos.segmentacao import segmentar
from riscos.ingestao import validar_dados


class RegrasDeVersao(unittest.TestCase):
    def setUp(self):
        self.fonte = {"id": "doc-1", "identificacao_cvm": {"CNPJ_CIA": "00.000.000/0001-00"},
            "empresa": "Empresa de teste", "tipo": "dfp", "data_referencia": "2025-12-31",
            "versao_declarada_cvm": "1", "sha256": "hash", "url": "https://example.org/doc.pdf"}
        self.anterior = {"id": "doc-1", "sha": "hash", "versao": "1", "vigente": True, "substitui": None}

    def test_nova_versao_explicita_pode_conservar_os_mesmos_bytes(self):
        nova = {**self.fonte, "id": "doc-2", "versao_declarada_cvm": "2", "substitui": "doc-1"}
        self.assertNotEqual(validar_publicacao(nova, [self.anterior])["chave_versao"], metadados(self.fonte)["chave_versao"])
        doc = {"documento_id": "doc-1", "sha256": "hash", "paginas": [{"pagina_pdf": 1,
            "texto": "A Companhia mantém empréstimos em moeda estrangeira (ACC) para compensar variações de clientes de exportações."}]}
        outra = {**doc, "documento_id": "doc-2"}
        self.assertNotEqual(segmentar(doc)[0]["id"], segmentar(outra)[0]["id"])

    def test_rejeita_id_reutilizado_e_substituicao_implicita(self):
        for nova in ({**self.fonte, "sha256": "outro"},
                     {**self.fonte, "id": "doc-2", "versao_declarada_cvm": "2"}):
            with self.assertRaises(ValueError):
                validar_publicacao(nova, [self.anterior])

    def test_preserva_versao_arquivada_ao_reprocessar_e_rejeita_ramificacao(self):
        antiga = {**self.anterior, "vigente": False}
        nova = {"id": "doc-2", "sha": "hash", "versao": "2", "vigente": True, "substitui": "doc-1"}
        validar_publicacao(self.fonte, [antiga, nova])
        terceira = {**self.fonte, "id": "doc-3", "versao_declarada_cvm": "3", "substitui": "doc-1"}
        with self.assertRaises(ValueError):
            validar_publicacao(terceira, [antiga, nova])

    def test_hash_identifica_mudanca_de_metadados_e_validacao_exige_versao(self):
        alterada = copy.deepcopy(self.fonte)
        alterada["url"] = "https://example.org/outro.pdf"
        self.assertNotEqual(hash_fonte(alterada), hash_fonte(self.fonte))
        alterada["versao_declarada_cvm"] = "incerta"
        with self.assertRaises(ValueError):
            metadados(alterada)

    def test_trecho_nao_pode_ser_anexado_a_outro_registro_do_mesmo_pdf(self):
        dados = {"fonte": self.fonte, "entidades": [], "declaracoes": [],
            "trechos": [{"id": "trecho", "documento_id": "outro-registro", "sha256": "hash"}]}
        with self.assertRaises(ValueError):
            validar_dados(dados)


if __name__ == "__main__":
    unittest.main()
