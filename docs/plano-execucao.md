# Plano de execução do mapa de riscos financeiros

Planejamento elaborado em 14 de novembro de 2026 para o projeto final de Tendências em Ciência da Computação do Centro Universitário de João Pessoa (Unipê). O trabalho será organizado por entregas verificáveis. As semanas sugeridas no enunciado não limitam a execução deste plano.

## Objetivo e pergunta de pesquisa

Construir um sistema GraphRAG/KAG que responda, em português, perguntas sobre exposições financeiras e mecanismos de proteção declarados por companhias brasileiras. Cada afirmação deverá ser verificável em um trecho de documento, com empresa, período, condições e caminho do grafo identificados.

Pergunta de pesquisa proposta: a recuperação híbrida com relações financeiras, restrições de período e evidências documentais melhora a correção e a fundamentação das respostas em comparação com RAG vetorial, especialmente nas perguntas que exigem cruzar documentos?

O objetivo é comparar exposições declaradas e medidas descritas. A classificação financeira seguirá o que cada documento efetivamente afirma. Um exemplo de pergunta é quais empresas relatam dívida em dólar, por quais obrigações e com que proteção declarada para o mesmo período. Este exemplo é uma proposta de consulta, sem afirmar fatos sobre empresas específicas.

## Decisões iniciais e dependências

- Recorte prioritário de exposição cambial, dívida em moeda estrangeira e proteção cambial. Risco de juros pode ser incluído se a amostra demonstrar relações documentadas suficientes.
- Meta inicial de três empresas não financeiras do mesmo setor e dois exercícios anuais fechados comparáveis. A seleção das empresas depende da fase de viabilidade.
- Acervo preferencial de Formulários de Referência completos e notas explicativas das demonstrações financeiras. Para três empresas, dois períodos e dois tipos de documento, a referência inicial é até doze documentos. Essa quantidade é uma proposta de escopo e poderá ser ajustada à qualidade das fontes.
- Documentos oficiais da CVM e de relações com investidores são as fontes principais. CSVs da CVM auxiliam a identificação e a conferência. A extração de entidades e relações deverá partir dos textos e tabelas contextualizadas.
- Banco adotado Neo4j, citado nominalmente no enunciado. Uma alternativa de banco poderá ser avaliada depois da conclusão do projeto, mediante nova decisão do grupo. O escopo atual usa exclusivamente Neo4j.
- Python para aquisição, extração, validação, recuperação e API. Neo4j em Docker com versão fixada. FastAPI para servir perguntas e subgrafos. Streamlit com componente Cytoscape.js para a interface. A fase técnica verificará a integração e o comportamento do componente.
- LLM e embeddings em português serão escolhidos por teste de extração e recuperação, custo e memória disponível. O mesmo LLM será usado na comparação entre métodos. Uma API externa, se necessária, dependerá da disponibilidade de credenciais e da aprovação de eventual custo.
- A política de acesso ao repositório será privada inicialmente. O convite ao professor continuará adiado até autorização do usuário.

As decisões de stack são propostas deste planejamento. A cobertura integral dos requisitos será demonstrada por artefatos e testes ao final de cada fase.

## Fase 1 — Viabilidade dos documentos e fechamento do recorte

### Implementação

1. Localizar documentos completos de empresas candidatas do mesmo setor.
2. Baixar uma amostra, registrar URL, título, tipo, companhia, CNPJ/código CVM, exercício, data de publicação, versão e SHA-256.
3. Extrair texto e tabelas, preservando página e seção. Usar OCR somente quando a qualidade da fonte exigir, com conferência dos trechos usados.
4. Ler as seções pertinentes em sua integridade. A coleta inicial deve permitir descobrir perguntas a partir das evidências disponíveis.
5. Montar uma tabela de relações observáveis e propor perguntas diretas, comparativas, temporais e sem resposta.
6. Verificar se há relações financeiras entre conceitos que sustentam consultas de dois ou mais saltos, além das ligações de procedência com documentos.

### Entregas

Manifesto de fontes, amostra dos documentos, relatório de qualidade de extração, proposta do domínio e primeiras perguntas com evidências.

### Critério de conclusão

Comprovar acesso e extração de documentos comparáveis de três empresas, incluindo pelo menos uma pergunta entre documentos por empresa ou comparação entre empresas. Identificar oito perguntas iniciais, das quais pelo menos quatro exijam conectar relações do domínio. Esses números são metas do projeto.

Se uma empresa tiver documentação insuficiente, a seleção será ajustada. A modelagem definitiva começará quando a amostra demonstrar essas relações.

## Fase 2 — Ontologia e modelagem LPG

### Implementação

Modelar Empresa, Documento, Trecho, Exposicao, ObrigacaoFinanceira, Moeda, FatorDeRisco, MedidaDeProtecao e Periodo. Ajustar os nomes finais à amostra.

Exposições e medidas terão identidade própria para preservar condições e procedência. Um documento pode descrever proteção parcial, um limite, um horizonte ou uma obrigação específica. A existência de uma medida na empresa não permite atribuí-la automaticamente a todas as exposições.

Exemplos de relações propostas:

- Empresa TEM_EXPOSICAO Exposicao.
- Exposicao DECORRE_DE ObrigacaoFinanceira.
- ObrigacaoFinanceira DENOMINADA_EM Moeda.
- Exposicao ASSOCIADA_A FatorDeRisco.
- MedidaDeProtecao MITIGA Exposicao, somente quando houver evidência.
- Exposicao ou MedidaDeProtecao DOCUMENTADA_EM Trecho.
- Trecho PERTENCE_A Documento.
- Documento REFERE_SE_A Empresa e identifica o exercício e a versão.

Definir chaves de identidade, cardinalidades esperadas e regras de consistência. Guardar montantes com representação decimal ou em centavos quando compatível, moeda, escala, sinal e período. Valores de tabela manterão cabeçalhos e unidade. Uma moeda de apresentação contábil não será convertida automaticamente em exposição cambial.

Criar constraints de unicidade e índices de propriedades, texto completo e vetor. Em versões atuais do Neo4j, o índice Range atende à busca por propriedades referida como BTree no enunciado. Documentar a correspondência de versão.

### Entregas

Diagrama LPG, dicionário de dados, regras semânticas, migrações do banco e consultas de inspeção de constraints e índices.

### Critério de conclusão

Representar exemplos reais da amostra, com condições, períodos e evidências. Testar os três tipos de índice com consultas que os utilizem e verificar a prevenção de duplicações.

## Fase 3 — Pipeline automatizado de aquisição e Text-to-Graph

### Implementação

Criar uma sequência reproduzível de aquisição, extração, divisão em trechos, NER, RE, validação e carga.

A divisão dos trechos deve preservar sujeito, condição, negação e referência temporal. Tabelas terão ligação com o parágrafo explicativo e com o título da nota. Relações sugeridas pelo modelo devem apontar para evidência textual existente.

Usar saída estruturada validada por esquema para entidades e relações. A extração deverá processar documentos selecionados por configuração, inclusive um documento de validação não utilizado para ajustar os prompts. Valores, páginas e datas terão validações determinísticas.

Implementar carga por documento com estado de processamento, checkpoints e reexecução idempotente. Cada nova versão deverá manter vínculo com a anterior e evitar que o texto antigo seja tratado como declaração atual. Falhas de extração deixam registros pendentes de revisão, sem publicar um documento como integralmente processado.

### Entregas

Comandos de ingestão, catálogo versionado, resultados intermediários auditáveis e relatório de entidades e relações extraídas.

### Critério de conclusão

Adicionar um documento pelo manifesto e executar o pipeline sem alterar o código para valores, empresas ou cláusulas específicos. Reexecutar a carga e simular interrupção, verificando ausência de duplicação e de fatos parcialmente publicados.

## Fase 4 — Resolução de entidades e qualidade da extração

### Implementação

Resolver empresas por identificadores oficiais e aliases documentados. Canonicalizar moedas e termos financeiros com vocabulário explícito. Manter o texto original e o termo canônico.

Separar companhia, subsidiária e grupo econômico. Preservar instrumentos diferentes e versões temporais. Similaridade textual pode sugerir uma correspondência. Casos ambíguos ficam para revisão.

Preparar uma amostra anotada de entidades e relações, cobrindo todas as empresas. Dois integrantes revisam uma parte comum e resolvem divergências. Reservar documentos ou trechos para conferência posterior ao ajuste.

### Entregas

Vocabulário de aliases, registro de decisões de união/separação, amostra anotada e relatório de precisão, revocação e F1 de entidades e relações.

### Critério de conclusão

Demonstrar variações de nome que convergem para a mesma entidade, entidades parecidas que permanecem distintas e tratamento de termos ambíguos. Medir os erros de extração e corrigir causas que comprometam o gabarito. A unicidade técnica será avaliada separadamente da resolução semântica.

## Fase 5 — Recuperação híbrida e geração de Cypher

### Implementação

1. Identificar intenção, empresas, períodos e conceitos da pergunta.
2. Recuperar candidatos por texto completo e por embeddings, com cosseno.
3. Combinar candidatos por uma estratégia documentada, como Reciprocal Rank Fusion, com deduplicação e filtros de metadados.
4. Fornecer ao LLM o esquema permitido e os parâmetros necessários para gerar uma consulta Cypher de leitura.
5. Validar estrutura e operações da consulta, rótulos, relações, parâmetros, limites e tempo de execução. Executar com permissões de leitura. Usar validação estrutural compatível com o dialeto escolhido e uma lista de operações permitidas.
6. Permitir uma tentativa de reparo controlada quando houver erro de sintaxe, registrando a consulta inicial, o erro e a correção.
7. Percorrer o grafo e recuperar relações e trechos que respondam à pergunta.

O Cypher efetivamente proposto pelo LLM e executado será registrado. Perguntas recorrentes podem ter exemplos de referência, mantendo o teste com perguntas novas.

### Entregas

Serviço de recuperação, índices em uso, consultas geradas e registro de candidatos recuperados.

### Critério de conclusão

Demonstrar pesquisa textual, vetorial e estruturada na mesma aplicação, com consultas multi-hop entre relações financeiras. Consultas inválidas ou de escrita devem ser rejeitadas antes de executar. Perguntas sem evidência devem produzir uma resposta que explique a limitação do contexto recuperado.

## Fase 6 — Algoritmo de grafo e regras de conhecimento

### Implementação

Usar caminho mínimo ou caminhos mínimos limitados entre entidades relevantes à pergunta, restringindo os tipos de relação, a empresa, o escopo e o período. Executar o algoritmo antes da geração da resposta. As entidades de entrada virão da pergunta e dos candidatos recuperados.

Os caminhos financeiros válidos fornecerão relações e trechos para o contexto do LLM. O ranking semântico e o caminho estrutural terão papéis identificáveis no registro da consulta. Limitar tamanho e quantidade de caminhos para conter contexto excessivo.

Aplicar regras de conhecimento, por exemplo:

- Menção a risco potencial preserva seu caráter condicional.
- Proteção declarada mantém escopo, instrumento, período e eventual cobertura parcial.
- Ausência de evidência recuperada não estabelece ausência de exposição.
- Afirmações de exercícios diferentes mantêm suas datas.
- Dívida, receita, caixa e moeda contábil têm significados distintos.
- O efeito líquido entre exposições exige dados e abrangência que sustentem a operação.
- Declarações com aparente conflito permanecem ligadas a suas fontes e versões.

A designação GraphRAG/KAG no artigo será explicada por esses mecanismos implementados. O trabalho não pressupõe reprodução integral de um framework de terceiros.

### Entregas

Módulo de seleção de caminhos, regras executáveis, contextos antes/depois do algoritmo e casos de regressão semântica.

### Critério de conclusão

Mostrar que o algoritmo muda o contexto recebido pelo LLM em uma pergunta pertinente. Incluir uma comparação controlada com recuperação híbrida sem esse algoritmo.

## Fase 7 — Respostas, procedência e nível de confiança

### Implementação

Gerar respostas em português a partir dos caminhos e trechos recuperados. Cada afirmação verificável recebe um identificador de evidência e as relações que a sustentam.

Validar referências, valores, moeda, escala, empresa, período e negações. Para cálculos eventualmente necessários, executar uma operação determinística com valores de origem identificados. Respostas parciais indicarão qual parte da pergunta ficou sem suporte.

Exibir um nível de confiança documental em categorias, com justificativa. Usar cobertura das partes da pergunta, suporte das afirmações, compatibilidade temporal e conflitos. Os critérios serão publicados. A nota de similaridade vetorial ficará identificada como similaridade.

Uma resposta com citações válidas pode conter erro de interpretação. A validação deve confrontar a afirmação com a evidência e incorporar esse resultado ao nível documental. Os limiares serão definidos no desenvolvimento e congelados para o teste reservado.

### Entregas

Contrato JSON de resposta, lista de afirmações e evidências, validação pós-geração e regra de confiança documental.

### Critério de conclusão

Demonstrar resposta sustentada, parcial, conflitante e sem suporte, com critérios reproduzíveis. As citações devem abrir no trecho ou na página correspondente. O usuário consegue identificar como o nível foi atribuído.

## Fase 8 — Interface e subgrafo interativo

### Implementação

Exibir pergunta, filtros de empresa/período, resposta, confiança documental e fontes. Renderizar o subgrafo retornado pelo serviço, com IDs persistentes e relações reais do banco.

Permitir zoom, pan, seleção de nós e relações, realce do caminho de cada afirmação e abertura do trecho de origem. Incluir painel com os nós e relações recuperados, os efetivamente enviados ao LLM e os citados na resposta.

Exibir consulta Cypher, parâmetros, algoritmo utilizado e metadados de execução em uma área de rastreabilidade. Salvar uma execução demonstrável para a defesa, com identificação de sua versão e data.

### Entregas

Interface funcional, componente Cytoscape integrado e roteiro de teste de uso.

### Critério de conclusão

A partir de uma afirmação, selecionar seu caminho, inspecionar a relação e abrir a evidência. A lista de contexto deve corresponder ao payload enviado ao modelo. Verificar também perguntas vazias, indisponibilidade do banco/modelo e consultas sem resultados.

## Fase 9 — Avaliação científica e testes operacionais

### Implementação

Separar perguntas de desenvolvimento e teste reservado. Proposta inicial de quinze perguntas de desenvolvimento e trinta de teste, distribuídas entre consulta direta, multi-hop, comparação entre empresas, comparação temporal, condições/negações e ausência de evidência. Os números são metas internas de escopo.

O gabarito será preparado a partir das fontes, com evidências e caminhos esperados, antes das execuções finais. Um integrante revisará perguntas preparadas por outro. O conjunto reservado ficará congelado e registrado no Git. Ajustes posteriores gerarão uma nova rodada identificada como desenvolvimento ou exigirão outro conjunto reservado.

Comparar:

- RAG vetorial sobre os trechos do mesmo acervo.
- Recuperação híbrida com Cypher.
- Recuperação híbrida com Cypher e algoritmo de grafo.

Usar o mesmo modelo de resposta, filtros de empresa/período, corpus, limite de contexto e critérios de correção. Medir a recuperação de evidências, correção da resposta, suporte das afirmações, citações corretas, reconhecimento de informação insuficiente, latência e recursos utilizados.

A diferença entre índices, filtros e algoritmo será discutida. O desempenho será reportado por categoria e com os erros observados. A comparação medirá mitigação de afirmações sem suporte, além de acerto de seleção.

Testes operacionais devem cobrir ingestão repetida/interrompida, aliases, versões de documentos, validade das citações, valores/unidades, consultas indevidas e fluxo da interface. Um clone limpo deverá iniciar a solução e reproduzir uma consulta e a avaliação.

### Entregas

Gabarito, relatórios por pergunta, resultados de extração, comparação de métodos, análise de erros e evidência de reprodução.

### Critério de conclusão

Relatar todos os resultados, inclusive falhas, com método reproduzível. Se os erros impedirem responder às perguntas centrais, o desenvolvimento volta à etapa responsável e o teste final será renovado ou identificado como já utilizado.

## Fase 10 — GitHub, artigo e defesa de quatro pessoas

### Implementação

Criar um novo repositório para o projeto após o fechamento do domínio. Registrar decisões, tarefas e contribuições reais de cada integrante. Incluir README com instalação, versões, credenciais por exemplo de ambiente, ingestão, execução, avaliação e solução de falhas conhecidas.

Catalogar fontes e licenças. Quando a redistribuição de um documento exigir cuidado, o repositório terá manifesto, checksum e instrução de aquisição compatível. Modelos grandes e segredos ficam fora do Git. Dependências, ferramentas e contribuições assistidas serão documentadas com atribuição pertinente.

Produzir artigo em modelo SBC ou IEEE com pergunta de pesquisa, trabalhos relacionados, corpus, ontologia, extração, arquitetura, regras, avaliação e limitações. Elaborar slides com evidências reais e uma demonstração que atravesse mais de um documento. As falas serão derivadas do sistema final.

Distribuição proposta:

- Arysson André Oliveira da Luz — problema, corpus, procedência e seleção das fontes.
- Caio Justino de Andrade — extração, resolução de entidades e modelagem LPG.
- Paulo Victor Oliveira de Barros Araújo — recuperação, geração de Cypher, algoritmo, regras e demonstração técnica.
- Luiz Henrique Monteiro dos Santos — avaliação, análise de erros, reprodutibilidade e conclusão.

As contribuições de implementação serão acompanhadas por tarefas e revisões. A distribuição das falas não substitui a participação prática dos integrantes. Paulo terá a exposição técnica mais complexa, conforme solicitado.

### Entregas

Repositório, README, artigo PDF e editável, apresentação editável e PDF, roteiro individual, perguntas de preparação para a defesa e demonstração reproduzível.

### Critério de conclusão

Executar a demonstração em clone limpo, conferir correspondência entre resultados e materiais, ensaiar com os quatro integrantes e compartilhar acesso ao professor quando autorizado. A data final depende do calendário oficial da AV2 e da defesa. A apresentação presencial será uma atividade do grupo.

## Matriz de cobertura do enunciado

| Exigência | Fases | Evidência de atendimento |
|---|---|---|
| Domínio, dataset e proposta | 1 | Manifesto, qualidade dos textos, perguntas e aprovação do recorte pela equipe. |
| NER automatizado | 3 e 4 | Entidades extraídas de documento novo e métricas na amostra anotada. |
| RE automatizado | 3 e 4 | Relações extraídas com trechos de origem e precisão/recall/F1. |
| Resolução e canonicalização de entidades | 4 | Aliases, identificadores e decisões auditadas de união e separação. |
| Esquema orientado ao domínio | 2 | Diagrama, dicionário, regras e exemplos reais. |
| LPG no Neo4j | 2 | Nós, relações e propriedades consultáveis. |
| Constraints e índices de propriedade | 2 | Inspeção do banco e consultas que comprovam sua aplicação. |
| Fulltext | 2 e 5 | Busca textual efetivamente utilizada na recuperação. |
| Índice vetorial e cosseno | 2 e 5 | Vetores versionados e consulta do índice na aplicação. |
| Ingestão automatizada | 3 | Documento do manifesto processado sem mudança específica de código. |
| Busca híbrida | 5 | Recuperação textual/vetorial com travessia e filtros Cypher. |
| Cypher via LLM | 5 | Texto da consulta gerada, validação, parâmetros e resultado. |
| Multi-hop com dois ou mais saltos | 5 e 6 | Perguntas que exigem relações financeiras conectadas e evidências correspondentes. |
| Algoritmo enriquecendo o contexto | 6 | Caminhos selecionados antes do LLM e avaliação de sua contribuição. |
| Mitigação de alucinações | 6, 7 e 9 | Regras, validação de afirmações e comparação em teste reservado. |
| UI funcional | 8 | Aplicação navegável e teste de ponta a ponta. |
| Subgrafo interativo | 8 | Seleção de nós/relações, navegação e realce de evidências. |
| Nós consultados e Cypher visíveis | 7 e 8 | Registro do contexto recuperado, enviado e citado. |
| Nível de confiança | 7 e 8 | Critério documental publicado e casos demonstráveis. |
| Procedência e caminhos explícitos | 3, 7 e 8 | Documento, trecho, página, versão e caminho por afirmação. |
| Artigo SBC/IEEE | 10 | Fonte editável, PDF e resultados reproduzíveis. |
| GitHub e README | 10 | Código, ambiente, instalação e reprodução em clone limpo. |
| Testes operacionais | 3 a 9 | Relatórios de testes de falhas e fluxo normal. |
| Bibliotecas e fontes creditadas | 10 | Dependências, referências e licenças. |
| Trabalho de quatro integrantes e defesa | 1 a 10 | Contribuições, revisão cruzada, ensaio e participação presencial. |
| Acesso do professor ao repositório | 10 | Convite ou visibilidade aplicável quando autorizado. |
| Uso do prompt de mentoria | Todas | Prompt abaixo aplicado como diretriz de execução e revisão. |

## Prompt de mentoria adotado

Você atua como mentor técnico de GraphRAG e KAG para o projeto de Tendências em Ciência da Computação do Unipê. Oriente e revise o trabalho com base no enunciado e nas instruções do grupo.

Priorize a compreensão e a participação dos quatro integrantes. Explique as decisões de modelagem e recuperação com exemplos das fontes, pseudocódigo quando útil e componentes incrementais acompanhados de verificação. Cada entrega deve permitir que a equipe entenda, reproduza e defenda o que foi implementado.

Antes de definir o esquema ou implementar o pipeline, valide o acesso aos documentos e a existência de relações que sustentem perguntas multi-hop. Mantenha separadas a hipótese inicial de tema e a viabilidade confirmada do corpus.

Exija uma modelagem LPG clara, identificação de entidades, canonicalização, controle de versões, constraints e uso demonstrável de índices de propriedades, texto completo e vetor. Use o banco escolhido de acordo com sua documentação e com o atendimento acadêmico ao enunciado.

A extração de entidades e relações deve partir dos documentos e preservar evidência, período, escopo, negação e condições. Toda afirmação financeira na resposta deve apontar para trechos verificáveis e relações do grafo. Uma inferência precisa ser reconhecida como tal e sustentada pelos caminhos disponíveis.

Implemente recuperação híbrida, consultas Cypher de leitura geradas pelo modelo e validadas, travessia de múltiplos saltos e algoritmo que selecione contexto antes da geração. Demonstre a contribuição de cada componente.

Avalie correção, suporte documental e abstenção em perguntas reservadas. Congele o gabarito antes das rodadas finais. Registre erros e limitações, preservando o resultado original de cada experimento.

A interface deve permitir explorar o subgrafo real, os documentos, as consultas e o nível de confiança documental. O usuário deve poder verificar cada resposta.

Escreva código legível, com responsabilidades claras e comentários que expliquem decisões, regras de domínio, limitações ou comportamentos pouco evidentes. Preserve a relação entre requisitos, implementação, testes, artigo e defesa.

O prompt original orienta a mentoria por conceitos, pseudocódigo e revisão, e restringe a entrega de uma solução completa de uma só vez. Este refinamento mantém o acompanhamento pedagógico e organiza o desenvolvimento solicitado em etapas compreensíveis, com verificações e revisão pelo grupo.

## Padrão de comentários e qualidade de código

Comentários devem explicar por que uma decisão existe ou registrar uma condição que seria fácil interpretar incorretamente. Bons usos incluem a diferença entre moeda de apresentação e moeda da obrigação, a precedência entre versões de um documento e a razão de preservar uma proteção como parcial.

Docstrings devem registrar contratos de funções públicas, entradas, saídas e falhas relevantes. Nomes de variáveis e funções devem tornar o fluxo evidente. Comentários que apenas repetem a instrução seguinte serão removidos na revisão. Regras financeiras merecem uma justificativa vinculada a um requisito ou exemplo de fonte.

Manter migrações versionadas, configuração externa, tratamento explícito de erros e registros de execução suficientes para depurar. O conjunto de testes será dirigido a riscos e requisitos observáveis. Refatorações e abstrações deverão resolver necessidades reais do código.

## Fontes consultadas para o planejamento

- Enunciado fornecido pelo grupo, Projeto Final GraphRAG e KAG em Ciência da Computação.
- CVM — Formulários de Referência e arquivos estruturados: https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre
- Neo4j — criação e uso de índices Range: https://neo4j.com/docs/cypher-manual/current/indexes/performance-indexes/create-indexes/

