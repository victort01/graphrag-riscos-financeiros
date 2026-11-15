"""Casos derivados da revisão assistida por IA (docs/revisao-assistida-IA).

As frases reproduzem construções das DFPs revisadas; os testes não dependem do corpus.
"""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.extracao import extrair
from riscos.respostas import montar_contexto, validar_resposta


class QualificadoresDaExtracao(unittest.TestCase):
    fonte = {"id": "companhia-teste-2025", "empresa": "Companhia Exemplo",
             "identificacao_cvm": {"CNPJ_CIA": "00.000.000/0001-00"}, "data_referencia": "2025-12-31"}

    def extrair_texto(self, texto):
        trecho = {"id": "trecho-teste", "sha256": "hash-teste", "natureza": "narrativa", "recorte": False, "texto": texto}
        entidades, _, declaracoes = extrair(trecho, self.fonte)
        nomes = {e["id"]: e["nome"] for e in entidades}
        return [{**d, "sujeito": nomes[d["sujeito_id"]], "objeto": nomes[d["objeto_id"]]} for d in declaracoes]

    def test_negativa_de_hedge_accounting_e_registrada_sem_relacao_positiva(self):
        declaracoes = self.extrair_texto("A Companhia não adota a modalidade de contabilização hedge accounting.")
        self.assertEqual([(d["predicado"], d["objeto"], d["polaridade"]) for d in declaracoes],
                         [("DECLARA_CONTABILIDADE_HEDGE", "sem hedge accounting", "negativa")])

    def test_outras_negativas_continuam_sem_declaracao(self):
        self.assertFalse(self.extrair_texto(
            "A Companhia não contrata instrumentos financeiros Zero Cost Collar para exposição cambial líquida."))

    def test_hedge_natural_e_protecao_economica(self):
        declaracoes = self.extrair_texto(
            "A Companhia realiza a contratação de dívida em moeda estrangeira como estratégia de hedge natural, "
            "uma vez que a geração de caixa é denominada em dólar.")
        protecao = [d for d in declaracoes if d["predicado"] == "ADOTA_PROTECAO"]
        self.assertEqual([d["tratamento_contabil"] for d in protecao], ["protecao_economica"])
        self.assertFalse(any(d["predicado"] == "DECLARA_CONTABILIDADE_HEDGE" for d in declaracoes))

    def test_swaps_de_juros_com_indexadores_diferentes_nao_se_unem(self):
        ipca = self.extrair_texto("A Companhia adota a contabilidade de hedge accounting de taxa de juros, com o objetivo "
                                  "de proteção contra o risco de variação do IPCA como indexador de dívidas em BRL alvo de operação de swap para CDI.")
        sofr = self.extrair_texto("A Companhia adota a contabilidade de hedge de taxa de juros, com o objetivo de proteção "
                                  "contra o risco de variação da SOFR como indexador de dívida em US$, o qual derivou na "
                                  "contratação de instrumento financeiro swap convertendo para taxa pré-fixada.")
        medida = lambda ds: {d["objeto_id"] for d in ds if d["predicado"] == "ADOTA_PROTECAO"}
        self.assertTrue(medida(ipca) and medida(sofr))
        self.assertFalse(medida(ipca) & medida(sofr))
        self.assertIn(("CONVERTE_DE", "IPCA"), {(d["predicado"], d["objeto"]) for d in ipca})
        self.assertIn(("CONVERTE_PARA", "pré-fixado"), {(d["predicado"], d["objeto"]) for d in sofr})
        self.assertTrue(all(d["tratamento_contabil"] == "hedge_accounting" for d in ipca if d["predicado"] == "PROTEGE"))

    def test_troca_de_indexador_para_otimizar_nao_vira_protecao_literal(self):
        declaracoes = self.extrair_texto(
            "O instrumento financeiro derivativo swap em vigência foi contratado com o objetivo de troca de indexador "
            "de taxa de juros para otimizar a estratégia de gestão dos passivos financeiros e do caixa no longo prazo.")
        self.assertTrue(any(d["predicado"] == "ADOTA_PROTECAO" for d in declaracoes))
        self.assertFalse(any(d["predicado"] == "PROTEGE" for d in declaracoes))

    def test_objetivo_de_politica_nao_e_contratacao(self):
        declaracoes = self.extrair_texto(
            "Objetivo de hedge: Designar Opções Zero Cost Collar (ZCC) e/ou Non-Deliverable Forwards (NDFs) como "
            "instrumentos de hedge para proteger de 25% a 50% da exposição cambial líquida da Companhia em até 24 meses.")
        protecao = [d for d in declaracoes if d["predicado"] in ("ADOTA_PROTECAO", "PROTEGE")]
        self.assertTrue(protecao)
        self.assertEqual({d["natureza"] for d in protecao}, {"politica"})
        self.assertTrue(all(d["condicoes"] for d in protecao))
        exposicao = [d for d in declaracoes if d["predicado"] == "TEM_EXPOSICAO"]
        self.assertEqual({d["natureza"] for d in exposicao}, {"declaracao"})

    def test_mencao_solta_a_valor_justo_nao_define_categoria_do_hedge(self):
        declaracoes = self.extrair_texto(
            "A Companhia adota programas de contabilidade de hedge e os auditores recalcularam o valor justo dos instrumentos financeiros.")
        categorias = {d["objeto"] for d in declaracoes if d["predicado"] == "DECLARA_CONTABILIDADE_HEDGE"}
        self.assertEqual(categorias, {"hedge accounting (categoria não especificada no trecho)"})


class ValidadorNarrativo(unittest.TestCase):
    def setUp(self):
        self.contexto = {"fontes": {"E1": {"texto": "Em 31 de dezembro de 2025, conforme nota explicativa 28, a Companhia "
            "não contrata operações alavancadas. A dívida de 100 está no quadro consolidado.", "periodo": "2025-12-31"}}}

    def erros(self, texto):
        return validar_resposta({"afirmacoes": [{"texto": texto, "fontes": ["E1"]}], "cobertura": "direta"}, self.contexto)

    def test_dia_de_data_e_numero_de_nota_nao_sao_montantes(self):
        self.assertFalse(self.erros("Em 31 de dezembro de 2025, a Companhia não contrata operações alavancadas (nota explicativa 28)."))

    def test_montante_continua_fora_do_escopo_narrativo(self):
        self.assertTrue(any("escopo narrativo" in e for e in self.erros("A dívida é de 100.")))

    def test_data_ausente_das_fontes_continua_rejeitada(self):
        self.assertTrue(any("ausente" in e for e in self.erros("Em 30 de junho de 2025 não há operações alavancadas.")))

    def test_escopo_literal_na_fonte_citada_e_aceito(self):
        self.assertFalse(any("escopo" in e for e in self.erros("O quadro consolidado apresenta a dívida.")))

    def test_escopo_ausente_da_fonte_continua_rejeitado(self):
        self.assertTrue(any("escopo" in e for e in self.erros("A controladora não contrata operações alavancadas.")))


class QualificadoresNoContexto(unittest.TestCase):
    def test_caminho_leva_natureza_e_tratamento_contabil(self):
        fonte = {"id": "t1", "texto": "Objetivo de hedge: designar ZCC.", "empresa": "Empresa teste", "periodo": "2025-12-31",
                 "pagina_inicio": 1, "pagina_fim": 1, "documento_id": "doc", "url": "https://example.org/f.pdf"}
        caminho = {"id": "C1", "saltos": 1,
                   "nos": [{"id": "e", "nome": "Empresa teste", "rotulos": ["Empresa"]},
                           {"id": "z", "nome": "Zero Cost Collar", "rotulos": ["MedidaProtecao"]}],
                   "relacoes": [{"id": "r1", "origem": "e", "destino": "z", "tipo": "ADOTA_PROTECAO", "periodo": "2025-12-31"}]}
        evidencia = {**fonte, "trecho_id": "t1", "declaracao_id": "r1", "citacao": fonte["texto"],
                     "natureza": "politica", "polaridade": "afirmativa", "tratamento_contabil": "hedge_accounting"}
        contexto = montar_contexto({"trechos": [fonte]}, {"caminhos": [caminho], "evidencias": [evidencia]})
        self.assertEqual(contexto["caminhos"][0]["qualificadores"],
                         [{"relacao": "ADOTA_PROTECAO", "natureza": "politica", "tratamento_contabil": "hedge_accounting"}])
        self.assertIn("qualificadores", json.dumps(contexto))


if __name__ == "__main__":
    unittest.main()
