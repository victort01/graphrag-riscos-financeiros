# Protocolo de avaliação

O script `avaliar_recuperacao.py` implementa uma comparação entre vetor, híbrido e híbrido com caminhos. O pequeno conjunto smoke tem duas perguntas já utilizadas no desenvolvimento; ele verifica a operação do avaliador e não substitui o conjunto científico reservado.

O avaliador mede localização de evidência por documento, página e termo, tanto nos candidatos quanto no contexto efetivamente enviado. Essa métrica não mede a correção de uma resposta ou a interpretação do trecho. O contexto inteiro, incluindo caminhos, tem orçamento de 3.500 caracteres para as três variantes. A variante com grafo reutiliza os candidatos híbridos para isolar o efeito do algoritmo. Erros são gravados por execução e não convertidos em abstenção factual. Há checkpoints a cada variante.

Os tempos registrados são descritivos. Aquecimento, disputa de recursos e caches afetam o resultado. Na variante grafo, o tempo da etapa corresponde ao enriquecimento adicional; não deve ser apresentado como latência total menor que a do híbrido.

A primeira tentativa smoke foi interrompida após um timeout do Neo4j na variante vetorial. O resumo preservado em `data/avaliacao-recuperacao-smoke-resumo.json` identifica a rodada como inválida para comparação. Esse erro operacional não é evidência de inferioridade do método vetorial.

## Smoke com indexação completa

Em 15/11/2026, uma nova rodada terminou sem falhas nas seis execuções, com os 3.918 trechos elegíveis indexados pelo mesmo modelo. O [resumo auditável](../data/avaliacao-recuperacao-smoke-completa-resumo.json) registra commit limpo, hashes de código, conjunto, manifesto e relatório integral, versões documentais e tentativas de Cypher. Ambas as consultas geradas passaram na primeira tentativa.

| Pergunta de desenvolvimento | Vetor: evidência no contexto | Híbrido | Híbrido + caminhos |
|---|---|---|---|
| S01 — Proteção de juros da Irani | 0/1 | 1/1 | 1/1 |
| S02 — ACC e recebíveis da Irani | 1/1 | 1/1 | 1/1 |

O algoritmo acrescentou um caminho ao contexto de cada pergunta, sem ganho de recall sobre o híbrido. Todos os contextos ficaram abaixo de 3.500 caracteres. O denominador é uma evidência esperada por pergunta; não é a integralidade de todas as fontes possíveis. Duas perguntas conhecidas de uma única companhia não permitem generalizar o resultado. A rodada não gerou respostas nem mediu alucinação. O diagnóstico anterior de seleção entre três empresas utilizou o índice piloto de 553 passagens e permanece identificado como histórico de desenvolvimento.

## Geração sobre contextos congelados

O avaliador de respostas reutiliza os contextos salvos e confere o hash do conjunto de perguntas. Não repete a recuperação. Registra separadamente a versão da recuperação e a da geração, modelo, contrato, ordem determinística embaralhada e hash de cada contexto. Checkpoints podem ser retomados sem duplicar pares já registrados; uma falha técnica não vira abstenção.

```powershell
.venv/Scripts/python scripts/avaliar_recuperacao.py --conjunto data/perguntas-smoke-recuperacao.json --saida data/reports/recuperacao-nova.json
.venv/Scripts/python scripts/avaliar_respostas.py --recuperacao data/reports/recuperacao-nova.json --conjunto data/perguntas-smoke-recuperacao.json --saida data/reports/respostas-novas.json
```

A [primeira rodada de geração](../data/avaliacao-respostas-smoke-inicial.json) concluiu seis inferências, mas quatro respostas sem grafo foram rejeitadas por confundir IDs de fontes/trechos com caminhos. O contrato foi corrigido para restringir fontes e caminhos aos IDs disponíveis, mantendo os mesmos critérios nas três variantes. A saída original continua no arquivo integral local identificado por hash.

A [rodada contextual](../data/avaliacao-respostas-smoke-contextual-resumo.json) também concluiu seis inferências. Nenhuma gerou referência de caminho inexistente; cinco mantiveram afirmações parciais. A variante com grafo em S01 foi rejeitada por declarar cobertura insuficiente junto de afirmações. Isso é diagnóstico de contrato e operação, não medida de correção semântica. Validade de referência não demonstra suporte da fonte e não permite concluir superioridade do grafo.

Os [formulários de revisão](revisao-respostas.md) omitem o rótulo da variante e preservam os localizadores das fontes. A presença de caminhos pode revelar o método; essa limitação de cegamento está declarada. Os formulários ainda estão pendentes, e nenhuma concordância ou taxa de alucinação humana foi calculada.

## Rodada científica pendente

Preparar quinze perguntas de desenvolvimento e trinta reservadas, cobrindo consulta direta, multi-hop, comparação entre empresas, comparação temporal, condição/negação e ausência de suporte. Registrar fontes e respostas esperadas antes de executar os métodos no reservado. Dois integrantes devem conferir uma parte comum das anotações e resolver divergências. Congelar conjunto, corpus, versões, regras e configuração no Git antes da rodada final.

Para as respostas, revisar correção de empresa/exercício, cobertura da pergunta, apoio de cada afirmação, referências de caminho e fonte, conclusões indevidas de cobertura e abstenção. Reportar divergências e falhas de infraestrutura separadamente. Aplicar a mesma regra de avaliação às três variantes, mantendo modelo, filtros e orçamento de contexto. Somente depois dessa rodada será possível discutir mitigação comprovada de alucinações e benefício do algoritmo.

Executar o smoke com `python scripts/avaliar_recuperacao.py`. As saídas ficam em data/reports/, fora do Git. Um resumo com as falhas e condições da execução deverá ser revisado antes de incorporar resultados ao artigo.
