# Andamento em 15 de novembro de 2026

Este quadro distingue conclusão de implementação, validação científica e entregáveis finais. Os requisitos do enunciado estão detalhados em [matriz-requisitos.md](matriz-requisitos.md).

| Fase interna | Situação | Evidência ou pendência principal |
|---|---|---|
| 1. Viabilidade | Concluída no recorte narrativo | Seis relatórios completos, 954 páginas, fontes e hashes. Revisão humana das anotações ainda necessária. |
| 2. Modelagem LPG | Concluída | Neo4j 5.26, ontologia, constraints e índices verificados. |
| 3. Text-to-Graph | Parcial | Carga narrativa, versionamento explícito, migração auditada e rollback verificados. Tabelas, cobertura ampliada e documento de validação externo pendentes. |
| 4. Identidades e qualidade | Parcial | Canonicalização e testes funcionais; dois formulários e comparador de revisões preparados. Revisão humana e validação independente pendentes. |
| 5. Recuperação híbrida | Implementação e verificação operacional concluídas | Fulltext, 553 vetores, RRF e Cypher gerado/validado; qualidade e desempenho ainda em avaliação. |
| 6. Algoritmo de grafo | Implementação e verificação operacional concluídas | Caminhos financeiros de dois saltos; ablation comprova alteração do contexto antes da geração. Benefício de qualidade ainda não medido. |
| 7. Respostas e confiança | Em validação | Referências, abstenção, filtros, auditoria e qualificação de escopo. Revisão semântica independente pendente. |
| 8. Interface | Implementação e verificação operacional concluídas | Nova consulta sobreviveu à reconexão e exibiu resposta, confiança, subgrafo e fonte. Arraste, pan, zoom e seleção conferidos. Deployment local de um processo. |
| 9. Avaliação | Infraestrutura inicial implementada | Comparação entre três variantes e protocolo. Rodada smoke interrompida após timeout; resultados insuficientes para comparação. |
| 10. Entrega e defesa | Em preparação | README e atribuições. Artigo SBC/IEEE, slides e falas dos quatro integrantes ainda pendentes. |

## Verificações desta etapa

A rodada completa mais recente executou **46 testes, todos aprovados**, em 41,870 s, no ambiente virtual do repositório, com o banco pronto em modo de ingestão e o corpus real disponível. Ela incluiu unicidade/rollback, índices Fulltext/vetorial, caminhos sobre o corpus, filtros, contexto, fontes, negações, arquivamento e quatro fluxos da interface via AppTest. Os testes da tela substituem o backend; não medem qualidade de geração.

Depois das funções de revisão e processamento em segundo plano, a rodada em modo de consulta contou com **54 testes: 51 aprovados e três testes de escrita ignorados**, em 4,282 s. Os três casos de escrita já haviam passado na rodada completa anterior. O ajuste final de não reenviar a pergunta ao concluir foi conferido novamente nos quatro testes da interface. O comparador também recusou os dois formulários reais ainda pendentes, sem gerar métricas humanas.

Após o versionamento documental e a migração dos IDs, a rodada completa com banco em ingestão e corpus real executou **62 testes, todos aprovados, em 10,511 s**. Os novos casos incluem mesmo PDF em registros distintos, exclusão da versão substituída na busca/caminhos, preservação de vetores, reprocessamento da versão antiga sem reativação e rollback da substituição. O acervo real conservou seis documentos, 85 declarações e 553 vetores com hashes por conteúdo idênticos. As versões adicionais usadas nos testes eram sintéticas e foram removidas ao final.

A verificação seguinte de escopo executou **68 testes completos, todos aprovados, em 7,828 s**. Incluiu quatro construções sintéticas de travessia e critérios de confiança comuns aos métodos. A regra adicional de atribuição explícita de controladora/consolidado foi verificada nos testes de resposta. No corpus real, as 85 declarações ficaram sem escopo identificado pela regra; por isso, a travessia limita esses casos ao mesmo trecho e a confiança registra a falta de qualificação. Esse achado é uma limitação da extração, não uma afirmação sobre ausência de informação no relatório inteiro.

A verificação de inicialização exige consulta Cypher autenticada e índices prontos. Duas tentativas intermediárias de testes foram iniciadas com escrita desabilitada ou antes de a reinicialização terminar; falharam por essas condições e não compõem a rodada aprovada. A rodada válida começou após a prontidão autenticada. O ciclo completo de reprodução em clone limpo continua pendente.

O ambiente isolado usa Python 3.13, dependências transitivas fixadas, pesos fora do Git e scripts para iniciar a interface/modelo. O perfil do Neo4j foi reduzido para heap 128–384 MB e page cache 64 MB. O limite global é 60 s e o Cypher gerado recebe 15 s. O encoder é liberado antes da geração da resposta. A consulta de recuperação sem Cypher gerado foi verificada nesse perfil com oito trechos e caminhos de dois e um saltos; levou 14,541 s, sem incluir resposta.

O primeiro fluxo completo com o modelo de 1,5B levou cerca de 328 segundos sob disputa de recursos e foi bloqueado pela validação de referências. A segunda execução levou cerca de 41 segundos e produziu resposta parcial, com contextualização desnecessária. O pós-processamento foi reavaliado sobre a saída salva, mantendo a afirmação pertinente sobre ACC e preservando o original para auditoria. Essa reavaliação não foi uma nova inferência.

A comparação smoke encontrou um timeout no Neo4j e foi interrompida. O arquivo `data/avaliacao-recuperacao-smoke-resumo.json` preserva a falha. Não há resultado científico demonstrando superioridade sobre RAG vetorial ou mitigação comprovada de alucinações nesta etapa.

A interface foi inicialmente conferida com uma execução salva. Uma nova execução isolada do backend terminou em 301,843 s, com resposta parcial validável, registrada em `data/validacao-execucao-isolada.json`. Esses tempos não demonstram causalmente uma melhoria de desempenho.

Após separar o processamento da conexão WebSocket, uma consulta nova iniciada pela tela continuou durante o recarregamento da página e foi retomada sem outra inferência. Terminou em 335,269 s e exibiu a resposta, confiança limitada, caminho de dois saltos e fonte da página 124. A seleção de afirmação, arraste de nó, pan, zoom e inspeção da relação foram conferidos. O teste real sem acervo de 2030 também produziu o motivo correto de abstenção. Capturas e detalhes estão em [fase-8-interface.md](fase-8-interface.md). A fase 8 foi encerrada na implementação/verificação operacional local; qualidade científica e uso em produção não são inferidos desse teste.

As próximas prioridades são tratar tabelas e o documento reservado, concluir a revisão da extração e avaliar perguntas independentes. O [pacote para revisão pelo grupo](revisao-extracao.md) está pronto e continua sem julgamentos humanos preenchidos. Esses resultados orientarão o artigo e a apresentação, com a parte técnica mais complexa destinada a Paulo.
