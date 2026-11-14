# Modelagem LPG e contratos de conhecimento

Fase 2 concluída em 14 de novembro de 2026. A inicialização foi repetida sem duplicar o esquema. Três testes operacionais passaram, incluindo rollback, consultas Fulltext/vetoriais e caminhos de múltiplos saltos. Os exemplos de teste são identificados e removidos ao final.

Cada entidade financeira representa um conceito identificável. Cada declaração representa uma relação observada em uma fonte e em um período. Os caminhos financeiros são acompanhados por declarações com evidências.

## Nós

| Rótulo | Identidade e propriedades principais |
|---|---|
| Empresa | CNPJ normalizado, nome oficial, código CVM, aliases e setor declarado. |
| Documento | ID do manifesto, SHA-256, URL, exercício, protocolo e versão publicada. |
| Trecho | Hash do documento e posição no texto, páginas inicial/final, texto e vetor. |
| Declaracao | ID estável, sujeito, predicado, objeto, empresa, período, escopo, condição, polaridade, método e evidência. |
| Periodo | Data de referência da observação. |
| ObrigacaoFinanceira | Conceito de dívida ou financiamento atribuído à companhia. |
| FluxoFinanceiro | Receita, recebível ou fluxo de caixa identificado no texto. |
| MedidaProtecao | Estratégia ou instrumento com finalidade e condições declaradas. |
| Exposicao | Exposição financeira identificada, com seu escopo de declaração. |
| FatorRisco | Fator canônico, como variação cambial ou juros. |
| Moeda | Código ISO da moeda explicitamente identificada. |
| Indexador | Indexador canônico, como CDI, IPCA ou SOFR. |
| CategoriaHedge | Categoria contábil explicitamente declarada. |

Conceitos monetários e fatores compartilháveis são globais. Dívidas, receitas e medidas são vinculadas à companhia. A resolução de entidades manterá conceitos parecidos separados quando sua finalidade, objeto ou abrangência diferirem. Uma identificação de companhia no cabeçalho não atribui automaticamente operações de controladas à controladora.

## Relações e evidências

O contrato executável dos tipos permitidos está em src/riscos/esquema.py. Um exemplo é Empresa → TEM_OBRIGACAO → ObrigacaoFinanceira → DENOMINADO_EM → Moeda.

Cada relação financeira tem declaracao_id. A declaração aponta por SUJEITO e OBJETO para as entidades e por EVIDENCIADA_POR para o trecho. A companhia liga-se por TEM_DECLARACAO à declaração, e a data é representada por NO_PERIODO. Os trechos PERTENCEM_A documentos.

As relações possuem identificação de declaração para preservar duas observações independentes da mesma relação em publicações diferentes. Uma reexecução deve manter os IDs. A carga de cada documento será transacional.

Uma declaração deve registrar seu escopo como controladora, consolidado ou não especificado e sua natureza como posição, política, cenário ou negação. Condições de cobertura, prazos e referências a receitas altamente prováveis permanecem ligadas à afirmação.

## Temporalidade e grandezas financeiras

A data de publicação e o exercício do documento são distintos da data de referência da observação. Uma coluna de 2024 em um documento de 2025 continua ligada à versão de 2025. O extrator deverá marcar para revisão datas ou escopos ambíguos.

A proteção de um fluxo ou obrigação será registrada para o objeto explicitado. A presença de um swap não implica finalidade cambial. Empréstimos designados como hedge podem continuar representados como obrigações financeiras.

Os números extraídos de tabelas só poderão ser publicados após validação da coluna, moeda, escala, sinal e contexto. O esquema permite guardar valores como representação decimal textual e unidade, evitando arredondamento por ponto flutuante no banco.

## Constraints e índices

Há unicidade por ID em cada classe, inclusive no rótulo-base Entidade. Há índices Range para documento e declarações por companhia/período, Fulltext para trechos e nomes e vetor de 384 dimensões para trechos. Essa dimensão corresponde ao candidato inicial de embeddings MiniLM multilíngue e deverá ser alterada por migração caso a avaliação escolha outra representação.

A inicialização usa Neo4j 5.26.0 Community em Docker. Os serviços ficam vinculados ao endereço local e usam senha definida no ambiente. Os índices são aguardados até ONLINE antes dos testes.

## Verificações operacionais

Os testes do esquema usam nós rotulados TesteEsquema e removem esses nós após cada caso. Verificam unicidade, rollback atômico, consulta Fulltext, consulta vetorial e navegação de múltiplos saltos.

O exemplo operacional usa o vínculo documentado entre financiamento de exportação e moeda da Suzano 2024, página PDF 40, com identificadores próprios de teste. O vetor desse teste é sintético e serve para verificar a configuração do índice. A ingestão de produção virá do pipeline da fase 3.
