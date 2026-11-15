# Arquitetura

A aplicação transforma descrições narrativas de relatórios financeiros em declarações com origem verificável. A recuperação seleciona texto e relações antes de gerar a resposta.

```text
PDF oficial → texto por página → entidades e relações → Neo4j
                                                        ↓
Pergunta → vetor + Fulltext + Cypher gerado → fusão → caminhos
                                                        ↓
                                       contexto → resposta → interface
```

## Documentos e declarações

O manifesto registra URL, SHA-256, empresa, exercício e versão de cada PDF. A segmentação preserva páginas e posições. Regras financeiras automatizam NER e RE, mantendo a evidência de cada relação, além de condição, polaridade e escopo quando reconhecidos. Desde `regras-financeiras-v6`, cada declaração de proteção registra o tratamento contábil (hedge accounting, proteção econômica ou não identificado) e a natureza (declaração, política ou possibilidade); a negativa explícita de hedge accounting é registrada como `DECLARA_CONTABILIDADE_HEDGE`, e swaps de juros são qualificados pelos indexadores.

| Classe | Responsabilidade |
|---|---|
| `Empresa` | Identidade por CNPJ normalizado. |
| `Documento` | Fonte, checksum, exercício, versão e vigência. |
| `Trecho` | Texto, localização no documento e embedding. |
| `Declaracao` | Sujeito, predicado, objeto, empresa, período, condição, escopo e evidência. |
| Classes financeiras | Obrigações, fluxos, exposições, proteções, moedas, indexadores e fatores de risco. |

Cada relação financeira identifica sua declaração. A declaração liga-se ao trecho por `EVIDENCIADA_POR`; o trecho liga-se ao documento por `PERTENCE_A`. Um caminho financeiro pode conectar empresa, obrigação e moeda em dois saltos. Relações de procedência não contam como saltos financeiros.

Moedas, indexadores e fatores podem ser compartilhados entre documentos. Obrigações e medidas são vinculadas à companhia. Constraints de unicidade não substituem a validação semântica da canonicalização.

Uma nova revisão documental recebe outro ID, versão maior e `substitui` apontando para a versão vigente da mesma empresa, tipo e exercício. A troca de vigência é atômica e preserva o histórico. Reprocessar uma versão antiga não a reativa. O acervo atual tem seis documentos na versão declarada 1; revisões adicionais foram testadas com dados sintéticos.

## Recuperação e caminhos

O Neo4j usa constraints, índices Range, Fulltext e vetorial. O vetor tem 384 dimensões, cosseno, mean pooling com máscara e normalização L2. O modelo, a revisão e o truncamento em 256 tokens constam do catálogo.

Vetor e Fulltext consultam o mesmo universo narrativo elegível. V1 tinha 3.918 trechos; mudanças de segmentação exigem nova ingestão e contagem. Uma consulta Cypher completa é gerada pelo LLM e validada por contrato de leitura, tipos permitidos, parâmetros, limite de resultados e plano `EXPLAIN`. Existe uma tentativa de reparo registrada. Consultas geradas recebem limite de 15 segundos. A implantação local desabilita escrita durante o uso. No Aura, o driver usa roteamento `READ`, que não substitui permissões de banco; as mesmas guardas de consultas permanecem ativas.

A fusão RRF soma `1 / (60 + posição)` por sinal. Vetor e Fulltext retornam até 24 candidatos cada; o Cypher gerado retorna até 16. No híbrido, os candidatos são reordenados pela sobreposição lexical ponderada pela frequência nos candidatos, com RRF como desempate. Repetições de texto por empresa/exercício são agrupadas, preservando seus IDs no rastreio. A seleção mantém até oito trechos. O controle vetorial preserva a ordem do vetor, sem essa reordenação. O algoritmo usa `shortestPath` dirigido em relações financeiras permitidas, com até quatro saltos. Duplicatas e prefixos com as mesmas arestas são compactados, e as fontes são distribuídas por empresa/exercício.

O pipeline separa as colunas dos quadros de assuntos de auditoria reconhecidos pelo cabeçalho, preservando posições do texto. Isso não implementa um detector universal de layout. Medidas de proteção representam programas documentais qualificados; a relação `DO_TIPO` os associa ao tipo de instrumento, sem confundir tipos compartilhados com contratos idênticos.

As fontes selecionadas pelo híbrido formam a base do contexto. Há uma reserva de até 500 caracteres para caminhos, aplicada também ao controle híbrido e dispensada quando reduzir a cobertura de empresas/exercícios. Caminhos, priorizados por número de saltos, e suas evidências só entram juntos quando cabem no orçamento total de 3.500 caracteres. Um caminho não pode expulsar uma fonte dessa base. Se não houver espaço, a resposta pode usar apenas texto; a seleção não garante ganho de recuperação.

As travessias respeitam empresa, exercício e vigência. Sem escopo reconhecido, as declarações do caminho precisam estar evidenciadas no mesmo trecho. Um fator compartilhado entre empresas não demonstra risco equivalente, correlação ou contágio.

## Resposta e interface

A saída estruturada admite até três afirmações. A decodificação restringe fontes e caminhos aos IDs existentes no contexto. Guardas verificam referências, atribuição de empresa, números, algumas conclusões absolutas, pertinência por vocabulário e qualificação de escopo. Valores quantitativos são recusados mesmo quando aparecem na narrativa; o recorte não valida unidades ou cálculos financeiros. Alegações sobre hedge accounting exigem declaração contábil específica para cada empresa, e uma negativa explícita de adoção não pode virar afirmação positiva. Essas regras cobrem classes delimitadas de erro, não toda implicação semântica. A saída original e as transformações ficam preservadas.

A confiança é documental: sem suporte, limitada ou moderada. Não equivale a probabilidade calibrada de acerto. Referências válidas não comprovam suporte semântico.

A interface usa Streamlit e Cytoscape.js. Mostra afirmações, fontes, páginas, consultas, nós e caminhos efetivamente consultados. Uma tarefa em segundo plano sobrevive à desconexão do navegador; a reinicialização do servidor interrompe a inferência. Os arquivos em `data/reports/` registram resultados e estados localmente.

## Limites

O escopo implementado é narrativo. Tabelas, imagens e montantes não estão validados para cálculos financeiros. O extrator pode omitir relações e qualificadores distantes da sentença. As 85 declarações da rodada V1 tinham escopo não identificado pelas regras; isso não significa que os relatórios omitam essa informação. O modelo pode gerar afirmações inadequadas mesmo com referências válidas. A validação independente permanece necessária para medir esse comportamento.
