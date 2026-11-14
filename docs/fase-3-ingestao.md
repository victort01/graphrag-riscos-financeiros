# Ingestão e extração de documentos

A fase 3 está em execução. O processamento narrativo e a publicação transacional já funcionam nos seis documentos do acervo. A extração de tabelas em imagem e a validação de suas colunas e unidades continuam pendentes.

## Comandos

Depois da aquisição e da configuração do Neo4j, execute python scripts/ingerir.py. A opção --id seleciona documentos, --somente-preparar gera artefatos locais e --reprocessar permite repetir uma carga já publicada.

O pipeline não consulta as anotações exploratórias para produzir os fatos. As regras identificam construções financeiras no texto de cada documento. Os resultados intermediários ficam em data/extracted, fora do Git, com entidades, menções, declarações, evidências e páginas.

## Texto e relações

A segmentação preserva trechos originais e normalizados, offsets por página e continuidade de parágrafos. Um teste de regressão cobre condições que continuam após uma quebra de bloco. Trechos cortados no limite de tamanho e tabelas não geram declarações narrativas.

O baseline NER utiliza padrões de moedas, indexadores e instrumentos financeiros. A RE utiliza construções que relacionam obrigações, receitas, exposições e proteção. Os nomes e valores específicos das empresas não estão embutidos nas regras.

As construções negativas e os cenários são preservados no texto, mas o baseline conservador não publica relações financeiras afirmativas a partir deles. A cobertura de negações e relações complexas deve ser ampliada por extração estruturada e avaliação. Toda declaração publicada precisa conter evidência literal do trecho e respeitar os tipos da ontologia.

## Carga consistente

A carga de cada documento é uma única transação. Ela substitui suas declarações e trechos sem apagar entidades compartilhadas. Um documento com o mesmo checksum e a mesma versão do pipeline é reconhecido como já processado. Uma versão com outro checksum exige outro ID de documento.

O banco registra estados separados para conteúdo narrativo e tabular. A extração atual pode sustentar perguntas qualitativas documentadas. Os valores das tabelas pendentes ainda exigem validação antes de uso em respostas quantitativas.

## Verificações

Os testes cobrem negação, relação entre ACC e recebíveis, continuidade de frases, identidade entre companhias, aliases, constraints, rollback e consultas de índice. O comando de ingestão foi repetido nos seis documentos e reconheceu as cargas existentes.

A próxima entrega desta fase é ampliar a extração estruturada e tratar imagens/tabelas, mantendo o registro dos campos sem comprovação e das falhas encontradas.
