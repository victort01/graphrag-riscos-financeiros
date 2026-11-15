# Respostas e confiança documental

Implementação inicial em `respostas.py`, ainda sujeita à validação de interpretação e abstenção. Fontes e caminhos compactados compartilham um orçamento total de 3.500 caracteres. O orçamento é igual para os métodos comparados. A entrada efetivamente enviada é preservada em `contexto_enviado`.

A saída estruturada contém até três afirmações, IDs de fontes e caminhos, cobertura declarada pelo modelo e sinal de possível divergência. Um filtro conservador de vocabulário remove contextualização que não menciona os conceitos financeiros reconhecidos na pergunta. Essa regra pode remover paráfrases relevantes e deverá ser avaliada quanto à revocação. A partir de um caminho válido, a aplicação resolve deterministicamente as fontes de todas as arestas. Ela mantém a saída original do modelo e registra filtros e complementos.

O pós-processamento verifica a existência das referências, valores numéricos e certas conclusões de proteção absoluta. Perguntas de conexão precisam citar um caminho multi-hop disponível quando a resposta declara cobertura direta. Em caso de falha, remove as afirmações e produz abstenção. Não há uma segunda geração silenciosa que substitua as evidências. Resolver uma referência não demonstra que o texto da afirmação é semanticamente implicado pelo caminho.

| Nível | Regra operacional |
|---|---|
| Sem suporte | Nenhuma afirmação ou erro nas verificações determinísticas. |
| Limitada | Referências verificadas, mas cobertura parcial ou possível divergência sinalizada pelo modelo. |
| Moderada | Cobertura direta declarada e verificações determinísticas aprovadas. Interpretação ainda requer avaliação. |

Não se atribui confiança alta nesta versão. As categorias não são probabilidades calibradas. O modelo pode interpretar incorretamente uma fonte válida ou avaliar incorretamente a cobertura. A avaliação humana e o teste reservado são necessários antes de afirmar mitigação comprovada de alucinações.

Testes unitários cobrem referência inventada, valor inventado, conclusão absoluta, divergência e abstenção. Ainda faltam casos completos de respostas sustentadas/parciais/conflitantes/sem suporte com conferência independente.
