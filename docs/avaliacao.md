# Avaliação

Os conjuntos e resultados publicados são de desenvolvimento. Nenhuma métrica apresentada deve ser interpretada como avaliação reservada, revisão humana concluída ou prova de generalização.

## Extração e identidades

`data/anotacoes-desenvolvimento-extracao.json` contém oito excertos, quinze menções e vinte e três relações esperadas, anotados com assistência de IA e usados para ajustar regras. Os resultados correspondentes avaliam esse conjunto conhecido.

```powershell
.venv/Scripts/python scripts/avaliar_extracao.py
.venv/Scripts/python scripts/preparar_revisao.py --saida data/reports/revisao-extracao
.venv/Scripts/python scripts/comparar_revisoes.py data/reports/revisao-extracao/revisor-1.json data/reports/revisao-extracao/revisor-2.json
```

Os formulários gerados têm campos vazios e exigem identificação e conclusão da revisão. Cada pessoa confere os PDFs, anota menções e relações e registra defeitos ou ambiguidades. O comparador recusa formulários pendentes. F1 simétrico e Jaccard medem concordância entre anotações; não são acurácia do extrator. Divergências precisam de adjudicação antes de produzir um gabarito consolidado.

## Recuperação

Compara-se vetor, híbrido e híbrido com caminhos. Modelo, filtros e orçamento de 3.500 caracteres são mantidos. A variante com caminhos reutiliza os candidatos híbridos para isolar o efeito do algoritmo.

```powershell
.venv/Scripts/python scripts/avaliar_recuperacao.py --conjunto data/perguntas-smoke-recuperacao.json --saida data/reports/recuperacao.json
```

Uma evidência esperada é localizada quando há correspondência de documento, página e termo normalizado. O avaliador mede recall nos candidatos e nas fontes enviadas. Essa métrica não mede interpretação nem correção de resposta. A execução é recusada se o índice vetorial não cobrir todos os trechos elegíveis.

| Pergunta do smoke | Vetor | Híbrido | Híbrido com caminhos |
|---|---|---|---|
| S01 — Proteção de juros da Irani | 0/1 | 1/1 | 1/1 |
| S02 — ACC e recebíveis da Irani | 1/1 | 1/1 | 1/1 |

As seis execuções concluíram sem falhas e as duas consultas Cypher foram aprovadas na primeira tentativa. O algoritmo acrescentou um caminho por pergunta, sem ganho de recall sobre o híbrido. Cada pergunta tem apenas um localizador esperado; ele não representa todas as evidências possíveis. [Resumo da rodada](../data/avaliacao-recuperacao-smoke-completa-resumo.json).

Uma tentativa anterior com timeout foi preservada separadamente e é inválida para comparação. Tempos são descritivos: aquecimento, cache e disputa de recursos variam. O tempo adicional do algoritmo não corresponde à latência total da variante.

## Respostas

A geração reutiliza contextos congelados e confere o hash do conjunto de perguntas. Mantém saída original, transformações, referências, validação, modelo, código e latência. Falhas técnicas não viram abstenção factual.

```powershell
.venv/Scripts/python scripts/avaliar_respostas.py --recuperacao data/reports/recuperacao.json --conjunto data/perguntas-smoke-recuperacao.json --saida data/reports/respostas.json
.venv/Scripts/python scripts/revisar_respostas.py preparar data/reports/respostas.json data/reports/revisao-respostas --mapa data/reports/mapa-revisao.json
```

A rodada inicial rejeitou quatro respostas por referências de caminhos inexistentes nas variantes sem grafo. Após restringir os IDs no contrato de saída, outra rodada concluiu seis inferências sem esse erro; cinco respostas mantiveram afirmações parciais e uma foi rejeitada por inconsistência entre cobertura insuficiente e presença de afirmações. Isso descreve o contrato, não a correção semântica. [Resumo contextual](../data/avaliacao-respostas-smoke-contextual-resumo.json).

Na revisão documental, abrir as páginas citadas e classificar apoio, pertinência, empresa/exercício, cobertura e adequação da abstenção. O rótulo da variante é omitido, mas a presença de caminhos pode permitir inferi-lo. Não alterar o conteúdo avaliado. O comparador exige formulários concluídos por pessoas distintas e lista divergências:

```powershell
.venv/Scripts/python scripts/revisar_respostas.py comparar data/reports/revisao-respostas/lote.json data/reports/revisao-respostas/revisor-1.json data/reports/revisao-respostas/revisor-2.json
```

## Validade e rastreabilidade

Os relatórios registram hashes dos conjuntos, manifesto, código e arquivos integrais locais. Esses registros distinguem configurações e preservam falhas. Revisão posterior dos exemplos usados no desenvolvimento não os transforma em teste independente.

Para medir suporte e mitigação de erros, reservar exemplos e respostas esperadas antes das execuções finais, manter os mesmos critérios entre variantes e separar falha de execução, abstenção e afirmação sem apoio. A avaliação independente ainda não foi concluída.
