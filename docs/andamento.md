# Andamento em 15 de novembro de 2026

Este quadro distingue conclusão de implementação, validação científica e entregáveis finais. Os requisitos do enunciado estão detalhados em [matriz-requisitos.md](matriz-requisitos.md).

| Fase interna | Situação | Evidência ou pendência principal |
|---|---|---|
| 1. Viabilidade | Concluída no recorte narrativo | Seis relatórios completos, 954 páginas, fontes e hashes. Revisão humana das anotações ainda necessária. |
| 2. Modelagem LPG | Concluída | Neo4j 5.26, ontologia, constraints e índices verificados. |
| 3. Text-to-Graph | Parcial | Carga narrativa automatizada e 85 declarações; tabelas, versões e validações ampliadas pendentes. |
| 4. Identidades e qualidade | Parcial | Canonicalização e testes funcionais; anotação assistida por IA, revisão independente pendente. |
| 5. Recuperação híbrida | Implementação e verificação operacional concluídas | Fulltext, 553 vetores, RRF e Cypher gerado/validado; qualidade e desempenho ainda em avaliação. |
| 6. Algoritmo de grafo | Implementação e verificação operacional concluídas | Caminhos financeiros de dois saltos; ablation comprova alteração do contexto antes da geração. Benefício de qualidade ainda não medido. |
| 7. Respostas e confiança | Em validação | Referências de fontes/caminhos, abstenção, filtros e auditoria. Erros de pertinência observados no modelo local. |
| 8. Interface | Protótipo implementado | Streamlit e Cytoscape; formulário observado, serializer testado. Verificação visual completa bloqueada por timeouts da ferramenta. |
| 9. Avaliação | Infraestrutura inicial implementada | Comparação entre três variantes e protocolo. Rodada smoke interrompida após timeout; resultados insuficientes para comparação. |
| 10. Entrega e defesa | Em preparação | README e atribuições. Artigo SBC/IEEE, slides e falas dos quatro integrantes ainda pendentes. |

## Verificações desta etapa

A rodada de corpus contou com 34 testes, dos quais 31 passaram e três testes de escrita do esquema foram ignorados porque o banco estava em modo de consulta. Após acrescentar a reconciliação de filtros, uma rodada sem banco verificou 32 testes unitários e ignorou seis testes de integração. O caso monetário adicional é verificado separadamente. Os testes de escrita foram verificados na fase 2; a nova tentativa de alternância de modos encontrou falhas de espera e não chegou a reexecutá-los.

A verificação de inicialização passou a exigir uma consulta Cypher autenticada, com espera maior, em lugar da simples abertura da página HTTP. O modo de consulta voltou a responder após esse ajuste. O ciclo completo de reprodução em clone limpo continua pendente. Houve também um timeout transitório em uma rodada de integração de corpus anterior; a repetição posterior passou.

O primeiro fluxo completo com o modelo de 1,5B levou cerca de 328 segundos sob disputa de recursos e foi bloqueado pela validação de referências. A segunda execução levou cerca de 41 segundos e produziu resposta parcial, com contextualização desnecessária. O pós-processamento foi reavaliado sobre a saída salva, mantendo a afirmação pertinente sobre ACC e preservando o original para auditoria. Essa reavaliação não foi uma nova inferência.

A comparação smoke encontrou um timeout no Neo4j e foi interrompida. O arquivo `data/avaliacao-recuperacao-smoke-resumo.json` preserva a falha. Não há resultado científico demonstrando superioridade sobre RAG vetorial ou mitigação comprovada de alucinações nesta etapa.

As próximas prioridades são estabilizar os testes sob recursos adequados, concluir a revisão da extração, avaliar perguntas independentes e verificar o fluxo visual completo. Esses resultados orientarão o artigo e a apresentação, com a parte técnica mais complexa destinada a Paulo.
