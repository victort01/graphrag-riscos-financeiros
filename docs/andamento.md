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
| 8. Interface | Fluxo salvo verificado; consulta ao vivo em estabilização | Afirmação realça dois saltos, relações mostram evidência e abrem PDF oficial. Desconexão durante nova inferência ainda requer acompanhamento. |
| 9. Avaliação | Infraestrutura inicial implementada | Comparação entre três variantes e protocolo. Rodada smoke interrompida após timeout; resultados insuficientes para comparação. |
| 10. Entrega e defesa | Em preparação | README e atribuições. Artigo SBC/IEEE, slides e falas dos quatro integrantes ainda pendentes. |

## Verificações desta etapa

A rodada completa mais recente executou **46 testes, todos aprovados**, em 41,870 s, no ambiente virtual do repositório, com o banco pronto em modo de ingestão e o corpus real disponível. Ela incluiu unicidade/rollback, índices Fulltext/vetorial, caminhos sobre o corpus, filtros, contexto, fontes, negações, arquivamento e quatro fluxos da interface via AppTest. Os testes da tela substituem o backend; não medem qualidade de geração.

A verificação de inicialização exige consulta Cypher autenticada e índices prontos. Duas tentativas intermediárias de testes foram iniciadas com escrita desabilitada ou antes de a reinicialização terminar; falharam por essas condições e não compõem a rodada aprovada. A rodada válida começou após a prontidão autenticada. O ciclo completo de reprodução em clone limpo continua pendente.

O ambiente isolado usa Python 3.13, dependências transitivas fixadas, pesos fora do Git e scripts para iniciar a interface/modelo. O perfil do Neo4j foi reduzido para heap 128–384 MB e page cache 64 MB. O limite global é 60 s e o Cypher gerado recebe 15 s. O encoder é liberado antes da geração da resposta. A consulta de recuperação sem Cypher gerado foi verificada nesse perfil com oito trechos e caminhos de dois e um saltos; levou 14,541 s, sem incluir resposta.

O primeiro fluxo completo com o modelo de 1,5B levou cerca de 328 segundos sob disputa de recursos e foi bloqueado pela validação de referências. A segunda execução levou cerca de 41 segundos e produziu resposta parcial, com contextualização desnecessária. O pós-processamento foi reavaliado sobre a saída salva, mantendo a afirmação pertinente sobre ACC e preservando o original para auditoria. Essa reavaliação não foi uma nova inferência.

A comparação smoke encontrou um timeout no Neo4j e foi interrompida. O arquivo `data/avaliacao-recuperacao-smoke-resumo.json` preserva a falha. Não há resultado científico demonstrando superioridade sobre RAG vetorial ou mitigação comprovada de alucinações nesta etapa.

A interface foi conferida com uma execução de desenvolvimento salva, preservando sua data e saída original. A seleção de afirmação destacou Irani → ACC → recebíveis de exportações; ambas as relações mostraram a citação da página 124, e o link abriu o PDF oficial nessa página. Foram verificadas as abas de fontes e rastreabilidade. O ajuste do canvas em telas estreitas foi corrigido. Capturas e detalhes estão em [fase-8-interface.md](fase-8-interface.md). Uma nova consulta ao vivo sofreu desconexão WebSocket durante a inferência local; essa estabilidade permanece pendente, mesmo com o arquivamento dos resultados concluídos.

As próximas prioridades são estabilizar a execução ao vivo, tratar tabelas/versões e o documento reservado, concluir a revisão da extração e avaliar perguntas independentes. Esses resultados orientarão o artigo e a apresentação, com a parte técnica mais complexa destinada a Paulo.
