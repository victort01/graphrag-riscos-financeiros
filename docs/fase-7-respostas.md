# Respostas e confiança documental

Implementação inicial em `respostas.py`, ainda sujeita à validação de interpretação e abstenção. Fontes e caminhos compactados compartilham um orçamento total de 3.500 caracteres. O orçamento é igual para os métodos comparados. A entrada efetivamente enviada é preservada em `contexto_enviado`.

A seleção intercala fontes por identidade canônica da empresa e exercício antes de repetir o grupo. Dentro do grupo, conserva a prioridade das evidências de caminho e a ordem de recuperação. Isso também evita separar aliases da mesma companhia. Não garante cobertura integral quando o orçamento não comporta todas as fontes; essa limitação precisa aparecer na resposta e na avaliação.

No caso de desenvolvimento sobre variação cambial nas três companhias em 2025, a seleção anterior recuperava as três, mas enviava fontes de apenas duas ao modelo. Com os mesmos candidatos, a distribuição por grupo e a retirada de prefixos redundantes passaram a enviar fontes das três, dentro do mesmo orçamento: 3.391 caracteres, contra 3.444 antes. As arestas de evidência foram preservadas. O [registro do caso](../data/validacao-contexto-multiempresa.json) mede cobertura de contexto nesse exemplo, não correção da resposta nem generalização.

A saída estruturada contém até três afirmações, IDs de fontes e caminhos, cobertura declarada pelo modelo e sinal de possível divergência. Um filtro conservador de vocabulário remove contextualização que não menciona os conceitos financeiros reconhecidos na pergunta. Essa regra pode remover paráfrases relevantes e deverá ser avaliada quanto à revocação. A partir de um caminho válido, a aplicação resolve deterministicamente as fontes de todas as arestas. Ela mantém a saída original do modelo e registra filtros e complementos.

O pós-processamento verifica a existência das referências, valores numéricos e certas conclusões de proteção absoluta. Perguntas de conexão precisam citar um caminho multi-hop disponível quando a resposta declara cobertura direta. Em caso de falha, remove as afirmações e produz abstenção. Não há uma segunda geração silenciosa que substitua as evidências. Resolver uma referência não demonstra que o texto da afirmação é semanticamente implicado pelo caminho.

| Nível | Regra operacional |
|---|---|
| Sem suporte | Nenhuma afirmação ou erro nas verificações determinísticas. |
| Limitada | Referências verificadas, mas cobertura parcial, possível divergência ou escopo jurídico sem qualificação unívoca nas fontes citadas. |
| Moderada | Cobertura direta declarada, verificações determinísticas aprovadas e escopo único reconhecido nas fontes citadas. Interpretação ainda requer avaliação. |

Não se atribui confiança alta nesta versão. As categorias não são probabilidades calibradas. O modelo pode interpretar incorretamente uma fonte válida ou avaliar incorretamente a cobertura. A avaliação humana e o teste reservado são necessários antes de afirmar mitigação comprovada de alucinações.

O escopo das declarações associadas a cada trecho acompanha as fontes no contexto, inclusive na variante sem grafo. A mesma regra de confiança vale para todos os métodos. A presença de escopo desconhecido ou de mais de um escopo na fonte citada limita o nível documental. A validação também rejeita atribuições textuais à controladora ou ao consolidado quando essa qualificação não está nos metadados das fontes citadas, inclusive em afirmações negativas. A regra é conservadora e não substitui uma avaliação de entailment: uma qualificação presente não prova a correção de toda a afirmação.

As regras atuais não identificaram escopo nos 85 enunciados publicados. O diagnóstico registra essa limitação do extrator, sem concluir que a informação esteja ausente do PDF completo. A qualificação a partir de cabeçalhos e contexto ampliado permanece pendente. A interface mantém o resultado original das execuções salvas; abrir um registro anterior não recalcula sua confiança com regras novas.

Testes unitários cobrem referência inventada, valor inventado, conclusão absoluta, divergência e abstenção. Ainda faltam casos completos de respostas sustentadas/parciais/conflitantes/sem suporte com conferência independente.

A verificação de certas conclusões absolutas distingue menções positivas e negativas. Por exemplo, a fonte “não assegura proteção total” não sustenta a conclusão “existe proteção total”. Essa regra cobre padrões explícitos de negação; não substitui uma análise semântica geral.

Novas execuções incluem o SHA-256 conjunto do código, catálogos e dependências declaradas, além de Python, plataforma e arquitetura. Segredos, documentos integrais e pesos não entram nesse hash; os pesos e documentos têm checksums próprios nos manifestos. A identificação permite distinguir execuções de versões diferentes, mas não prova a reprodução em outro computador. Arquivos antigos sem esse campo permanecem identificados como registros anteriores.
