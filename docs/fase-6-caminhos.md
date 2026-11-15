# Caminhos financeiros e contexto

O módulo `caminhos.py` executa `shortestPath` dirigido no Neo4j, antes da chamada que gera a resposta. Para cada empresa/exercício presente nos candidatos da busca, seleciona entidades cujos nomes ou aliases compartilham termos com a pergunta. Busca um caminho mínimo por par empresa/entidade, limitado a quatro saltos e aos tipos financeiros da ontologia.

Todas as arestas do caminho devem pertencer à mesma empresa e ao mesmo exercício. A consulta não usa relações de Documento/Trecho para contar saltos financeiros. Ela retorna nós persistentes, relações, IDs de declaração e número de saltos. As declarações fornecem a evidência de cada aresta. O rastreio guarda a consulta, parâmetros e trechos antes/depois do enriquecimento.

## Caso verificado

No corpus da Irani de 2025 há o caminho Empresa → ADOTA_PROTECAO → swap para troca de indexador de juros → PROTEGE → exposição a taxas de juros. Ele contém dois saltos financeiros, apoiados na página 124 do relatório. Há também Empresa → TEM_OBRIGACAO → ACC → COMPENSA_VARIACOES_DE → recebíveis de exportações.

O teste de integração inicia com um trecho de ACC e pergunta pela proteção de juros. O algoritmo acrescenta a fonte pertinente ao segundo tema, mantém 2025 e a identidade da Irani, e confere a presença literal das citações. Esse é um teste controlado de funcionamento. A avaliação de benefício sobre recuperação híbrida em perguntas independentes continua pendente.

A ablation em `data/validacao-caminhos-desenvolvimento.json` usa os mesmos candidatos híbridos com e sem o algoritmo e o mesmo orçamento total de contexto. O contexto com grafo inclui dois caminhos financeiros. O teste confirma alteração do contexto antes da geração, sem atribuir melhoria de qualidade. As verificações de implementação da fase 6 estão concluídas no recorte atual.

Na resposta, as evidências dos caminhos têm prioridade dentro do orçamento de contexto. Um caminho só é enviado se as fontes de todas as arestas também forem enviadas. O contexto enviado ao modelo contém nomes, tipos e período; os IDs e fontes completos permanecem no rastreio e na visualização.

## Regras de interpretação

A geração recebe regras explícitas para preservar negação, condição, empresa e exercício; distinguir dívida, receita e moeda contábil; não inferir proteção total ou ausência de risco; e não calcular exposição líquida sem dados completos. O pós-processamento rejeita referências inexistentes, valores ausentes das fontes e certas conclusões absolutas sem apoio literal. Essas verificações não constituem prova de entailment semântico.

O mecanismo implementa um sistema GraphRAG com restrições de conhecimento do domínio. Ele não reproduz integralmente um framework KAG externo. A seleção lexical de entidades e a preferência por caminhos curtos podem omitir conexões relevantes; os caminhos precisam ser avaliados contra o gabarito.

Referência: [caminhos mínimos no Cypher 5](https://neo4j.com/docs/cypher-manual/5/patterns/shortest-paths/).
