"""Regressões para conteúdo financeiro que antes se confundia no contexto."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from riscos.segmentacao import segmentar
from riscos.extracao import extrair
from riscos.selecao import selecionar


class ProgramasEEvidencias(unittest.TestCase):
    fonte = {'id': 'sintetico-2025', 'empresa': 'Emissor sintético',
             'identificacao_cvm': {'CNPJ_CIA': '00.000.000/0001-00'}, 'data_referencia': '2025-12-31'}

    def extrair(self, texto):
        return extrair({'id': 'trecho', 'sha256': 'sha', 'texto': texto,
                        'natureza': 'narrativa', 'recorte': False}, self.fonte)

    def test_colunas_da_auditoria_nao_produzem_sentenca_hibrida(self):
        pares = [('Porque é um PAA', 'Como o assunto foi conduzido'),
                 ('A Companhia mantém empréstimos e', 'Nossos procedimentos de auditoria'),
                 ('financiamentos em moeda estrangeira.', 'incluíram a inspeção da documentação.')]
        texto = '\n'.join(a.ljust(60)+b for a,b in pares)
        documento = {'documento_id': 'sintetico', 'sha256': 'sha',
                     'paginas': [{'pagina_pdf': 1, 'texto': texto}]}
        trechos = segmentar(documento)
        financeiro = next(t for t in trechos if 'empréstimos' in t['texto'])
        self.assertNotIn('Nossos procedimentos', financeiro['texto'])
        self.assertIn('financiamentos em moeda estrangeira.', financeiro['texto'])
        reconstruido = ' '.join(texto[o['inicio']:o['fim']] for o in financeiro['origens'])
        self.assertEqual(' '.join(reconstruido.split()), financeiro['texto'])

    def test_negativa_contabil_pode_ser_recuperada_no_grafo(self):
        _, _, fatos = self.extrair('A Companhia não adota a modalidade de contabilização hedge accounting.')
        self.assertEqual([f['predicado'] for f in fatos], ['NAO_ADOTA_TRATAMENTO'])
        self.assertEqual(fatos[0]['polaridade'], 'negativa')

    def test_programas_de_swaps_com_indexadores_distintos_nao_sao_unidos(self):
        textos = ['A Companhia adota a contabilidade de hedge de taxa de juros mediante swap convertendo SOFR para taxa pré-fixada.',
                  'A Companhia adota a contabilidade de hedge de taxa de juros mediante swap convertendo IPCA para CDI.']
        medidas=[]
        for texto in textos:
            entidades, _, fatos = self.extrair(texto)
            medidas.extend(e for e in entidades if e['tipo']=='MedidaProtecao' and e.get('granularidade')=='programa_documental')
            self.assertTrue(any(f['predicado']=='CONVERTE_DE' for f in fatos))
        self.assertEqual(len({m['id'] for m in medidas}), 2)
        self.assertNotEqual(medidas[0]['nome'], medidas[1]['nome'])

    def test_nome_do_emissor_e_repeticao_nao_substituem_conteudo(self):
        textos=['A educação corporativa Irani estimula o desenvolvimento profissional.',
                'A Companhia não adota hedge accounting.', 'A Companhia não adota hedge accounting.']
        candidatos=[{'id': str(n), 'texto': t, 'empresa': 'Irani', 'periodo': '2025-12-31', 'rrf': 1/(n+1)} for n,t in enumerate(textos)]
        selecionados, rastro=selecionar('A Irani adota hedge accounting?', candidatos)
        self.assertEqual(selecionados[0]['id'], '1')
        self.assertEqual(rastro['duplicatas'], [['1','2']])


if __name__ == '__main__':
    unittest.main()
