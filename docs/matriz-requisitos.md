# Rastreio do enunciado

Referência: documento “Projeto Final — GraphRAG e KAG em Ciência da Computação”, fornecido pelo grupo, incluindo as tabelas de entregáveis e da rubrica. Revisão em 15 de novembro de 2026. Os dez passos do planejamento interno detalham as quatro fases do enunciado.

| Pedido do enunciado | Implementação/evidência | Situação |
|---|---|---|
| Definir domínio e dataset | Três empresas, dois exercícios, seis relatórios completos; manifesto, hashes e diagnóstico em data/. | Verificado no recorte narrativo. |
| Configurar mentor com o prompt oficial | AGENTS.md adapta o prompt para implementação incremental, explicação das decisões e validação. Refinamento autorizado pelo usuário. | Aplicado. |
| NER e RE automáticos em documentos não estruturados | Segmentação e regras financeiras em src/riscos; ingestão sem preencher manualmente as relações de cada PDF. | Implementado para narrativas; tabelas e cobertura independente pendentes. |
| Resolução/canonicalização | Identificadores CVM, aliases tipados e escopo por empresa; ambiguidade sem união automática. | Testes e métricas de desenvolvimento; revisão independente pendente. |
| Esquema orientado ao domínio | Empresa, exposição, obrigação, fluxo, medida de proteção, moeda, indexador, declaração, documento e trecho. | Verificado. |
| LPG no Neo4j | Ontologia em esquema.py, diagramas e dicionário na fase 2. | Verificado. |
| Constraints de unicidade | Migrações idempotentes; teste de duplicação e rollback. | Verificado no Neo4j 5.26. |
| Índices de propriedades/BTrees | Índices Range, correspondentes atuais da família de índices de propriedades; chaves e filtros documentados. | Criados e inspecionados. |
| Fulltext e Vector Index | Consultas reais sobre o corpus; 3.918 vetores de 384 dimensões, cobrindo todos os trechos narrativos elegíveis. | Verificado. |
| Busca híbrida com cosseno e Cypher | RRF entre vetor, Fulltext e IDs de trechos retornados pelo Cypher gerado. | Implementado e testado no desenvolvimento; avaliação de qualidade pendente. |
| Geração de Cypher via LLM | Modelo gera a string completa; validação, EXPLAIN, reparo e banco somente leitura. | Execuções válidas e rejeições verificadas. |
| Travessia de dois ou mais saltos | Empresa → ACC → recebíveis; Empresa → swap de juros → exposição a juros. | Verificado com relações financeiras reais. |
| Algoritmo enriquecendo contexto do LLM | Caminhos mínimos limitados, evidências por aresta e seleção antes da geração. | Módulo e integração de corpus testados; comparação de benefício pendente. |
| Mitigação comprovada de alucinações | Fontes por afirmação, regras semânticas, verificações determinísticas e abstenção. | Implementação inicial; comprovação científica pendente. |
| Interface funcional | Streamlit com pergunta, filtros, resposta e fontes; processamento separado da conexão. | Consulta real concluída após reconexão, abstenção sem acervo e fluxos de erro verificados; deployment local. |
| Subgrafo interativo de contexto | Cytoscape com IDs reais, caminhos, seleção e fonte de aresta. | Realce por afirmação, arraste, pan, zoom, duas relações, citação e abertura de PDF oficial verificados visualmente. |
| Nós consultados, Cypher e confiança | Rastreio separa candidatos, caminhos, contexto enviado e fontes citadas; nível documental explicado. | Implementado; interpretação e usabilidade em validação. |
| Código completo no GitHub | Repositório privado graphrag-riscos-financeiros, commits por entrega. | Em desenvolvimento. |
| Acesso do docente | Convite adiado por instrução expressa do usuário. | Pendente de autorização futura. |
| README com reprodução e deployment | Aquisição, banco, ingestão, modelos, consulta e implantação local. | Documentado; clone limpo de toda a solução ainda pendente. |
| Testes operacionais | Unicidade, rollback, índices, extração, aliases, consultas indevidas, caminhos e respostas. | Executados por módulo; ampliar com avaliação final. |
| Artigo SBC/IEEE | Será escrito com método, resultados medidos e erros observados. | Pendente. |
| Apresentação presencial em grupo | Quatro integrantes identificados; conteúdo mais complexo destinado a Paulo. | Slides e roteiro final pendentes dos resultados. |
| Atribuição de bibliotecas e originalidade | Manifesto de modelos, licença Cytoscape e registro de assistência no desenvolvimento. | Em consolidação; revisar antes da entrega. |

O prazo sugerido de quatro semanas foi substituído por entregas verificáveis a pedido do usuário. Não se considera uma fase concluída apenas porque o código correspondente existe.
