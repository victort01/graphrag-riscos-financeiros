# Recuperação híbrida e Cypher

O módulo `recuperacao.py` consulta o índice vetorial com cosseno e o índice Fulltext, filtra empresa/exercício e combina os candidatos por Reciprocal Rank Fusion, com constante 60. Cada método retorna até 12 candidatos e a fusão mantém até oito trechos. O índice vetorial contém 553 passagens narrativas selecionadas por vocabulário financeiro. Outros trechos continuam disponíveis no Fulltext. Essa seleção limita a cobertura semântica e deve ser considerada na avaliação.

Somente trechos narrativos sem recorte entram na recuperação atual. `intencao.py` reconhece as três empresas do recorte e anos explícitos, distinguindo marcas monetárias simples. Quando a pergunta contradiz os filtros, a interface solicita o ajuste da seleção. Sem filtros explícitos, usa as menções reconhecidas. Essa heurística de âmbito não é um interpretador financeiro geral.

Os embeddings usam o modelo e a revisão registrados em `data/modelos.json`, variante ONNX quantizada, mean pooling com máscara, normalização L2 e truncamento em 256 tokens. O identificador inclui a variante e o processamento. A indexação incremental evita misturar vetores de configurações diferentes na consulta. A versão anterior em PyTorch foi substituída por consumo de memória; todos os 553 vetores foram recalculados.

O LLM recebe a pergunta, o esquema de declarações e sugestões de predicados por vocabulário. Ele produz a consulta Cypher completa em JSON. A aplicação não substitui uma consulta rejeitada por um template. O contrato deliberadamente restringe a geração a localizar declarações e seus trechos. A travessia entre entidades financeiras ocorre no módulo de caminhos, separadamente das ligações de procedência.

## Validação e execução

Antes da execução, a aplicação verifica tamanho, início da consulta, parâmetros, retorno de IDs de trechos, limite, nomes do esquema e tipos de relações reconhecidas. Bloqueia operações de escrita, procedimentos, comentários, consultas múltiplas e caminhos variáveis na consulta gerada. O Neo4j compila a consulta com EXPLAIN; operadores fora da lista permitida causam rejeição. Há uma tentativa de reparo com a consulta anterior e seu erro. Tentativas aceitas e rejeitadas ficam no rastreio.

Essa validação é um contrato restritivo, não um parser universal de Cypher. A proteção adicional de escrita é feita pelo próprio banco. No modo de consulta, `server.databases.default_to_read_only=true`; no modo de ingestão, a escrita é habilitada explicitamente. O teste de uma operação CREATE no modo de consulta retornou `WriteOnReadOnlyAccessDatabase`. O Neo4j Community usado não oferece a separação de papéis adotada em instalações Enterprise. O banco é local e não recebe consultas arbitrárias pela interface.

O limite global de transações é 60 segundos. O cliente envia um limite de 15 segundos para compilar e executar a consulta gerada. O perfil foi ajustado após timeouts sob paginação de memória. Os resultados passam novamente pelos filtros de empresa e exercício antes de entrar na fusão. Similaridade e pontuação RRF não são probabilidades de correção.

## Verificações e limitações

Foi executada a pergunta de desenvolvimento sobre ACC e recebíveis da Irani em 2025. Os três métodos contribuíram para o trecho da página 124. Com sugestões de predicados, o modelo de 3B gerou filtro `TEM_OBRIGACAO`/`COMPENSA_VARIACOES_DE`. Sem essas sugestões, uma rodada selecionou predicados pouco pertinentes. Outras tentativas produziram relações de tipos incompatíveis e foram rejeitadas. Esses erros fazem parte do desenvolvimento e não demonstram generalização.

A geração de resposta com o modelo de 3B e contexto maior ultrapassou 180 segundos na máquina de desenvolvimento. A variante de 1,5B executou o fluxo completo, incluindo Cypher, caminhos e resposta. A primeira execução levou aproximadamente 328 segundos sob forte disputa de recursos e terminou em abstenção por referências incompletas. O caso permanece documentado. Uma execução posterior produziu resposta parcial e expôs contextualização desnecessária, motivando a revisão do pós-processamento. A qualidade semântica continua em avaliação.

O endpoint é configurável; trocar o backend exige registrar modelo/revisão e repetir a avaliação. A consulta usa exclusivamente o cache local do tokenizer e dos pesos, preparado pelo comando de aquisição. Um filtro de exercício sem documentos produz abstenção sem chamar modelos. Ainda faltam o conjunto reservado e a comparação científica de métodos.

O encoder ONNX é liberado depois de codificar a pergunta; a indexação mantém a sessão entre lotes. A alteração reduz a coexistência de modelos na RAM sem mudar os vetores. No ambiente virtual isolado e com o perfil reduzido do banco, uma consulta de desenvolvimento sem a etapa de Cypher gerado recuperou oito trechos, com doze candidatos vetoriais e doze textuais, e caminhos de dois e um saltos. A recuperação levou 14,541 s nessa execução; esse tempo não inclui a geração da resposta e não é um benchmark.

As verificações operacionais da fase 5 foram concluídas no recorte narrativo. Isso não equivale à validação científica da qualidade da recuperação e das respostas, prevista nas fases 7 e 9.

Referências de implementação: [índices vetoriais Neo4j 5](https://neo4j.com/docs/cypher-manual/5/indexes/semantic-indexes/vector-indexes/), [configuração de bancos somente leitura](https://neo4j.com/docs/operations-manual/current/database-administration/standard-databases/configuration-parameters/), [ONNX Runtime](https://onnxruntime.ai/docs/api/python/api_summary.html) e [modelo de embeddings](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
