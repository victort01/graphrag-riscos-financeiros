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

O cache também verifica um hash dos metadados relevantes da fonte. O ID de um documento publicado não pode ser reutilizado para outro checksum ou número de versão. Uma nova versão da mesma empresa/tipo/exercício exige outro ID e o campo `substitui`, apontando para a versão vigente. A revisão pode ter bytes idênticos aos da submissão anterior; por isso, os trechos incluem o ID documental em sua identidade, além do checksum e dos offsets. A associação de um trecho a outro registro é rejeitada.

O histórico fica ligado por `SUBSTITUI`. A recuperação textual/vetorial, o pós-filtro do Cypher gerado e os caminhos financeiros excluem documentos e relações substituídos. A versão da fonte entra no contexto e aparece na aba Fontes. A vigência é relativa à série documental do exercício; ela não representa um histórico de tudo que era público em uma data passada.

A publicação e a retirada da versão anterior são atômicas. As chaves únicas impedem duas versões vigentes da mesma série. Reprocessar a versão antiga conserva seu estado arquivado. Uma tentativa de criar outra revisão a partir de um antecessor já substituído é recusada, mantendo uma cadeia explícita.

O versionamento foi verificado com documentos **sintéticos de teste**, incluindo duas versões com o mesmo checksum. Isso não indica que as seis fontes reais tenham sido reapresentadas: elas continuam na versão 1 registrada no manifesto. Ainda falta um documento real não usado no desenvolvimento para a validação externa da extração.

O banco registra estados separados para conteúdo narrativo e tabular. A extração atual pode sustentar perguntas qualitativas documentadas. Os valores das tabelas pendentes ainda exigem validação antes de uso em respostas quantitativas.

## Verificações

Os testes cobrem negação, relação entre ACC e recebíveis, continuidade de frases, identidade entre companhias, aliases, constraints, rollback e consultas de índice. O comando de ingestão foi repetido nos seis documentos e reconheceu as cargas existentes.

Na migração para `paragrafos-v4`/`versoes-v1`, os seis documentos foram reprocessados. A auditoria por conteúdo confirmou as mesmas 85 declarações e os mesmos 553 vetores, sem mudança em seus hashes e sem trechos ligados a outro documento. Os vetores foram herdados somente com o mesmo modelo e a mesma entrada de texto/empresa/exercício. A segunda execução retornou cache para os seis documentos. O [registro da migração](../data/validacao-migracao-versionamento.json) preserva os totais e hashes; ele não mede a precisão semântica da extração.

```powershell
.venv/Scripts/python scripts/auditar_corpus.py --saida data/reports/corpus-antes.json
.venv/Scripts/python scripts/ingerir.py
.venv/Scripts/python scripts/auditar_corpus.py --comparar data/reports/corpus-antes.json --saida data/reports/corpus-depois.json
```

O comparador acusa alteração dos fatos ou vetores por conteúdo, admitindo a mudança planejada dos IDs técnicos. Nesta migração, os IDs dos trechos/declarações mudaram. As execuções de desenvolvimento anteriores mantêm os IDs, citações e subgrafos originais em seus arquivos; não devem ser confundidas com uma nova consulta ao banco migrado.

A fase permanece parcial: a próxima entrega deve tratar imagens/tabelas, unidades, cobertura da extração e documento de validação externo, mantendo o registro dos campos sem comprovação e das falhas encontradas.
