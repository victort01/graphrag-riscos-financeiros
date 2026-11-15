# Fase 1 — Viabilidade do acervo

Situação concluída em 14 de novembro de 2026. O recorte é viável para construir o mapa de exposição cambial e mecanismos de proteção. A modelagem do grafo será a próxima fase.

## Empresas, fontes e períodos

Foram adquiridos seis documentos anuais completos, em português, com notas explicativas. Cada arquivo foi identificado por SHA-256. O catálogo registra as páginas oficiais de origem, os arquivos publicados pelos emissores, o CNPJ, o código CVM e o protocolo DFP correspondente. Os protocolos são conferência de emissor, exercício e versão declarada. O checksum identifica o PDF efetivamente usado, incluindo material adicional do pacote de divulgação.

| Documento | Páginas PDF | Caracteres extraídos | Páginas com menos de 100 caracteres |
|---|---:|---:|---:|
| Suzano DFP 2024 | 184 | 825.371 | 8 |
| Suzano DFP 2025 | 181 | 810.356 | 8 |
| Klabin DFP 2024 | 153 | 586.054 | 3 |
| Klabin DFP 2025 | 156 | 910.339 | 0 |
| Irani DFP 2024 | 139 | 264.442 | 0 |
| Irani DFP 2025 | 141 | 286.368 | 0 |
| Total | 954 | 3.682.930 | 19 |

A extensão do acervo não equivale à quantidade de evidências relevantes. A exploração identificou dez perguntas e dezesseis localizadores de evidência. As relações serão extraídas automaticamente nas fases seguintes. Os arquivos exploratórios registram uma leitura assistida por IA, usada para validar a viabilidade e desenvolver a extração. A revisão humana independente permanece pendente.

A Suzano e a Klabin estão classificadas na CVM como Papel e Celulose. A Irani está classificada como Embalagens. O grupo foi selecionado pela cadeia produtiva de papel, celulose e embalagens. Essa diferença de subsegmento será preservada nas comparações. O cadastro oficial e seu checksum estão em data/identidades-cvm.json.

## Decisão sobre o corpus inicial

O corpus inicial terá seis demonstrações financeiras completas de 2024 e 2025. Os documentos contêm notas de riscos, obrigações e proteções que permitem responder perguntas comparativas e temporais. A meta de até doze documentos no planejamento era uma referência de escopo. Formulários de Referência poderão complementar uma necessidade documental identificada na modelagem ou na extração.

Os períodos serão tratados por data de referência da afirmação, exercício principal e versão documental. Uma coluna comparativa de 2024 dentro de uma DFP de 2025 deve manter a procedência da publicação de 2025. Dados da controladora e do consolidado também serão distinguidos.

## Relações observadas

- Suzano relaciona receitas de exportação e financiamentos na mesma moeda e descreve limites para derivativos de receita. As notas permitem separar proteção natural e instrumentos financeiros.
- Klabin descreve dívida designada para receitas futuras e derivativos voltados à exposição líquida de caixa. Há condicionantes de cobertura, prazo e conversão de moeda.
- Irani relaciona ACC a recebíveis de exportação e atribui aos swaps mencionados uma finalidade de juros. As declarações permitem verificar a classificação do instrumento pela finalidade.

As afirmações detalhadas e seus localizadores estão em data/evidencias-exploratorias.json. As respostas de desenvolvimento estão em data/perguntas-exploratorias.json. Esses materiais não constituem resultados de um sistema GraphRAG já implementado.

## Perguntas que sustentam o desenvolvimento

| ID | Tipo de consulta | Cruzamento necessário |
|---|---|---|
| P01 | Comparar dívida em dólar e receitas de exportação em 2024 | Suzano e Klabin, com obrigações, moedas, receitas e proteção. |
| P02 | Comparar mecanismos e limites cambiais em 2025 | Suzano e Klabin, com tipo de proteção, exposição e prazo. |
| P03 | Identificar mudança de enquadramento de hedge IPCA | Publicações da Klabin de 2024 e 2025. |
| P04 | Conferir a relação entre ACC e recebíveis em dois exercícios | Publicações da Irani de 2024 e 2025. |
| P05 | Diferenciar o objetivo dos instrumentos de duas empresas | Irani e Klabin em 2025, distinguindo juros e câmbio. |
| P06 | Verificar se a proteção descrita abrange toda a receita | Condições e limites na nota da Suzano de 2025. |
| P07 | Recuperar faixa de proteção e horizonte | Nota de exposição líquida da Klabin de 2025. |
| P08 | Pergunta sem resposta sobre resultado efetivo de 2027 | Detectar o período fora do corpus. |
| P09 | Conferir se uma menção a swap comprova finalidade cambial | Finalidade de juros e contexto de ACC na Irani de 2024. |
| P10 | Verificar condições de designação de dívida como hedge | Partes da dívida, receita provável e moeda na Klabin de 2024. |

Cinco perguntas exigem cruzar documentos. Os caminhos conceituais conectam entidades financeiras. Os nomes finais de rótulos e relações dependerão da fase 2.

## Revisão visual e limites de extração

Foram renderizadas e conferidas integralmente as páginas PDF 40 da Suzano 2024, 124 da Klabin 2025 e 124 da Irani 2025, confrontando o texto extraído com narrativa e tabelas. As páginas de risco usadas nos dezesseis localizadores foram lidas integralmente. Os testes automáticos verificam a existência dos termos de conferência nas páginas correspondentes.

A Suzano apresenta numeração interna diferente da posição no PDF. A página PDF 40, por exemplo, é a página impressa 38. Os localizadores usam pagina_pdf explicitamente.

A tabela de exposição cambial da Irani aparece como imagem no PDF e fica ausente do texto extraído. O texto narrativo e a explicação de ACC permanecem legíveis. Essa é uma pendência da extração de tabelas na fase 3. A tabela precisa passar por OCR/extração visual e revisão de colunas, sinais, moeda, unidade e escopo antes de gerar valores quantitativos.

Algumas tabelas extensas da Klabin apresentam valores concatenados na extração por disposição de página. Um caso está na página PDF 135 de 2025. A modelagem não deverá transformar esse texto diretamente em montantes sem uma validação da estrutura da tabela.

Há dezenove páginas com pouco texto, o que exige triagem de imagens e páginas de apresentação. Zero caracteres de substituição Unicode não demonstra integridade tabular. As métricas de qualidade são sinais de diagnóstico e vêm acompanhadas destas verificações visuais.

Os valores comparativos de uma rubrica podem variar entre publicações de exercícios diferentes. A recuperação deverá manter documento e data de referência, e a análise precisará conferir notas e escopo antes de explicar a diferença.

## Reprodutibilidade e procedência

O comando scripts/validar_fontes.py baixa PDFs do manifesto, verifica seus checksums e grava texto por página e métricas de qualidade. O modo offline exige os documentos no cache e confere novamente a integridade.

scripts/verificar_corpus.py verifica os seis checksums, a vinculação de cada extração ao PDF, a sequência de páginas, os dezesseis localizadores e as metas de perguntas entre documentos.

Os PDFs e o texto integral extraído ficam fora do Git. O repositório conserva fontes, hashes, identificadores e instruções para aquisição. Os relatórios de métrica e as anotações exploratórias estão versionados. Nenhum benchmark reservado foi executado nesta fase.

## Critérios de aceitação

| Critério da fase | Resultado |
|---|---|
| Três companhias com fontes comparáveis | Atendido, com diferença de subsegmento explicitada. |
| Documentos completos acessíveis e texto extraível | Atendido para narrativa. A extração das tabelas possui pendências identificadas para a fase 3. |
| Períodos e versões identificáveis | Atendido, com exercício, protocolo CVM e checksum do PDF. |
| Pelo menos oito perguntas exploratórias | Atendido, com dez perguntas. |
| Pelo menos quatro perguntas de cruzamento | Atendido, com cinco perguntas entre documentos. |
| Localização verificável de evidências | Atendido, com dezesseis referências conferidas. |
| Relatório de qualidade e limitações | Atendido, incluindo imagens, tabelas e paginação. |

O acervo permite avançar à ontologia. A conclusão desta fase comprova a viabilidade documental e mantém as pendências de extração explicitamente vinculadas à fase responsável.

## Fontes oficiais

- Cadastro de companhias abertas da CVM em https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv
- Protocolos DFP em https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/
- Suzano em https://ir.suzano.com.br/Portuguese/informacoes-financeiras/central-de-resultados/default.aspx
- Klabin em https://ri.klabin.com.br/divulgacoes-e-resultados/central-de-resultados/
- Irani em https://ri.irani.com.br/servicos-aos-investidores/central-de-resultados/

Os endereços específicos dos seis PDFs estão em data/manifesto.json.
