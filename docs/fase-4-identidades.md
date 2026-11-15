# Identidades e avaliação de desenvolvimento

A resolução de entidades utiliza o tipo, o domínio da companhia e a qualificação do instrumento. O CNPJ do cadastro CVM identifica o emissor. Moedas e indexadores podem ser compartilhados por companhias. Instrumentos e fluxos são classes vinculadas à companhia.

## Regras de resolução

USD, US$ e as formas explícitas de dólar americano convergem para uma moeda. NDF e Non-Deliverable Forward, ZCC e Zero Cost Collar e ACC e sua descrição por extenso convergem para seus conceitos dentro da mesma companhia.

Uma menção genérica a dólar permanece ambígua. Uma menção genérica a swap exige finalidade ou objeto. Quando um trecho contém uma única qualificação de swap, suas menções são ligadas a essa classe. Se o trecho contiver finalidades concorrentes, o caso permanece pendente. Swaps de juros e swaps de câmbio mantêm identidades próprias.

A granularidade de um instrumento ainda é classe de instrumento, salvo a companhia, que é pessoa jurídica. Identificadores individuais de contratos exigirão sua extração específica. A existência de constraints será verificada separadamente dessas regras semânticas.

## Amostra anotada

Há oito excertos do material lido na fase 1, com quinze menções e vinte e três relações esperadas. A anotação é assistida, usada para desenvolvimento e sem revisão independente. Ela não integra o teste reservado da fase 9.

Execute python scripts/avaliar_extracao.py. O relatório apresenta precisão, revocação e F1 e identifica itens faltantes e extras. A avaliação inicial encontrou treze das quinze menções e dezenove das vinte e três relações esperadas. Depois das correções, os oito excertos satisfizeram a anotação.

Os resultados inicial e atual foram preservados em data/avaliacao-extracao-inicial.json e data/avaliacao-extracao-desenvolvimento.json. O resultado posterior descreve o ajuste nesses exemplos. A qualidade fora da amostra será medida com novos trechos e documentos na avaliação reservada.

## Estado da fase

A canonicalização, a resolução contextual e seus testes funcionais estão implementados. A preparação da anotação e a medição de desenvolvimento também estão implementadas. A revisão do conjunto pelo grupo, a ampliação de cobertura e a avaliação fora da amostra permanecem necessárias para consolidar a validação de qualidade.
