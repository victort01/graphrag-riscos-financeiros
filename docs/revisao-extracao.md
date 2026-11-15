# Revisão da extração pelo grupo

Os formulários em `data/revisao-extracao/` contêm os mesmos oito excertos já usados no desenvolvimento, com texto, página, URL e checksum. Nenhuma previsão do extrator ou anotação anterior foi copiada para os campos de julgamento. Os campos vazios significam **pendência**, e não ausência de entidade/relação.

Esta atividade revisa a qualidade do gabarito de desenvolvimento. Os excertos já foram usados para corrigir regras; uma revisão posterior não os transforma em teste independente. A avaliação reservada precisa de outros exemplos e perguntas congelados antes de sua execução.

## Preenchimento independente

1. Dois integrantes usam arquivos separados (`revisor-1.json` e `revisor-2.json`) e preenchem `revisor` com seus nomes. A escolha das pessoas cabe ao grupo; o arquivo não registra uma participação ainda não realizada.
2. Para cada excerto, abrir a página oficial e conferir o parágrafo anterior, o seguinte e o título da nota. Manter o texto extraído; registrar eventual defeito em `observacoes`. Um excerto incompleto ou incorreto deve receber `estado: "rejeitado"` e motivo.
3. Em `mencoes`, registrar pares `["tipo", "superfície exata no texto"]`, seguindo o [dicionário LPG](fase-2-modelagem.md). Registrar todas as menções pertinentes aos tipos do escopo, inclusive as que o extrator possa perder. Diferenciar pessoa jurídica, classe de instrumento, moeda, indexador e fluxo de receita.
4. Em `relacoes`, registrar triplas `["sujeito canônico", "PREDICADO", "objeto canônico"]`. `@empresa` representa a companhia do documento. Cada tripla precisa ser sustentada pelo excerto. Preservar finalidade, negação, condição e exercício; não inferir proteção integral ou vincular uma medida a toda a dívida da companhia.
5. Usar `estado: "revisado"` somente após terminar um excerto. Um excerto revisado pode ter listas vazias, caso o revisor conclua que não há itens pertinentes. Não consultar a saída do modelo ou o gabarito assistido antes de terminar a própria anotação.
6. Ao terminar todos os excertos, marcar o estado do arquivo como `revisado`. Manter as duas versões independentes e suas divergências; não substituir uma pela outra para produzir concordância aparente.

## Consolidação

Depois das duas anotações, comparar os rótulos e discutir as divergências com o PDF aberto. O grupo deve registrar a decisão e a justificativa por item antes de gerar um gabarito consolidado. Se uma divergência exigir mudar a ontologia ou o critério de anotação, registrar a mudança e reaplicar o critério aos demais excertos.

O relatório deve apresentar a concordância observada, o número de rejeições e o método de consolidação. O script de comparação recusa arquivos pendentes; a ausência de revisão não poderá ser publicada como resultado humano.

```powershell
.venv/Scripts/python scripts/comparar_revisoes.py data/revisao-extracao/revisor-1.json data/revisao-extracao/revisor-2.json
```

O relatório calcula F1 simétrico e Jaccard sobre os rótulos positivos de NER e RE. Eles medem concordância entre os dois arquivos, sem assumir que um revisor é gabarito. Não são kappa nem precisão do extrator. Casos rejeitados por algum revisor ficam destacados fora desses denominadores; conjuntos sem itens positivos recebem `null`.

Para preparar outro pacote sem sobrescrever os formulários existentes:

```powershell
.venv/Scripts/python scripts/preparar_revisao.py --saida data/reports/revisao-extra
```
