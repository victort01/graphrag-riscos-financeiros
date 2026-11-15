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

## Rodada científica pendente

Preparar quinze perguntas de desenvolvimento e trinta reservadas, cobrindo consulta direta, multi-hop, comparação entre empresas, comparação temporal, condição/negação e ausência de suporte. Registrar fontes e respostas esperadas antes de executar os métodos no reservado. Dois integrantes devem conferir uma parte comum das anotações e resolver divergências. Congelar conjunto, corpus, versões, regras e configuração no Git antes da rodada final.

Para as respostas, revisar correção de empresa/exercício, cobertura da pergunta, apoio de cada afirmação, referências de caminho e fonte, conclusões indevidas de cobertura e abstenção. Reportar divergências e falhas de infraestrutura separadamente. Aplicar a mesma regra de avaliação às três variantes, mantendo modelo, filtros e orçamento de contexto. Somente depois dessa rodada será possível discutir mitigação comprovada de alucinações e benefício do algoritmo.

Executar o smoke com `python scripts/avaliar_recuperacao.py`. As saídas ficam em data/reports/, fora do Git. Um resumo com as falhas e condições da execução deverá ser revisado antes de incorporar resultados ao artigo.
