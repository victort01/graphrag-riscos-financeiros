# Melhorias propostas a partir da revisão assistida por IA

Base: [revisão assistida por IA](revisao-assistida-IA/revisao-assistida-IA.md) dos 33 excertos de extração e das 34 respostas da rodada prospectiva, conferidos nas páginas dos seis PDFs oficiais (SHA‑256 conferidos). A revisão é uma sugestão para a conferência humana, que continua pendente. Nada aqui mede acurácia nem redução de alucinações.

## Resumo dos achados que motivam as mudanças

- 5 das 11 afirmações geradas são contraditas pelos documentos. A mais grave diz que a Suzano adota hedge accounting em 2024, embora a nota 4.1.1 declare que “não adota a modalidade de contabilização hedge accounting” (DFP 2024, p. 35 do PDF; DFP 2025, p. 100).
- O grafo não distinguia proteção econômica (hedge natural), hedge accounting designado e swaps de otimização: todos viravam `ADOTA_PROTECAO`/`PROTEGE`.
- O extrator descartava toda frase com negação, por isso a negativa de hedge accounting nunca entrava no grafo.
- Swaps de juros diferentes (IPCA→CDI e SOFR→pré) caíam no mesmo nó genérico, e objetivos de política (“designar ZCC e/ou NDF … 25% a 50% … até 24 meses”) viravam fatos contratados.
- 13 das 26 abstenções ocorreram com a página da resposta entre as fontes recuperadas. Várias foram forçadas pelo validador por números incidentais, como o dia de “31 de dezembro”.

## Implementado neste PR

| Mudança | Arquivo | Efeito esperado |
|---|---|---|
| `regras-financeiras-v6`: negativa explícita de hedge accounting gera `DECLARA_CONTABILIDADE_HEDGE → “sem hedge accounting”` com `polaridade: negativa`. As demais negativas continuam sem relação positiva. | `src/riscos/extracao.py`, `src/riscos/esquema.py` | Perguntas sobre adoção de hedge accounting passam a ter evidência no grafo, inclusive negativa. |
| Adoção explícita gera `DECLARA_CONTABILIDADE_HEDGE` com categoria (fluxo de caixa, valor justo ou não especificada). A categoria só é atribuída quando qualifica o próprio hedge. | `extracao.py` | Separa tratamento contábil de proteção econômica. |
| Atributo `tratamento_contabil` (`hedge_accounting`, `protecao_economica`, `nao_identificado`, `nao_aplicavel`) nas declarações de proteção. | `extracao.py` | O hedge natural fica marcado como econômico. |
| Atributo `natureza` (`declaracao`, `politica`, `possibilidade`) em instrumentos e obrigações. Exposições factuais continuam `declaracao`. | `extracao.py` | Objetivos e possibilidades deixam de parecer contratação. |
| Swaps de juros qualificados pelos indexadores (`swap de juros IPCA→CDI`, `swap de juros SOFR→pré-fixado`), com `CONVERTE_DE`/`CONVERTE_PARA` e exposição ao indexador de origem. `PROTEGE` só quando a frase fala em proteção ou hedge. | `extracao.py` | Instrumentos diferentes deixam de compartilhar identidade. “Troca de indexador para otimizar” deixa de virar proteção literal. |
| Evidências e caminhos enviados ao gerador levam `qualificadores` (natureza, polaridade, tratamento contábil) quando diferem do padrão. | `src/riscos/caminhos.py`, `src/riscos/respostas.py` | O modelo vê que uma aresta é política, negativa ou econômica. |
| Validador: dia de data (“31 de dezembro”, “31/12/2025”) e número de nota explicativa não contam como montante. Data ausente das fontes continua rejeitada. Um escopo citado literalmente na fonte é aceito. | `respostas.py` | Menos abstenções forçadas por falso positivo, sem liberar montantes. |
| 13 testes novos. | `tests/test_qualificadores.py` | Suíte: 107 testes, 20 pulados por exigirem banco ou corpus. |

### O que este PR não verificou

- **Reingestão:** o grafo publicado e os artefatos em `data/` continuam gerados pela v5. A mudança de versão do extrator exige reingestão (`scripts/ingerir.py`) e nova execução de `scripts/avaliar_extracao.py`, `auditar_extracao.py` e da rodada de respostas.
- **Testes de integração:** os testes com `TESTAR_NEO4J=1` e `TESTAR_CORPUS=1` não foram executados.
- **Avaliação de desenvolvimento:** as métricas podem mudar, porque os swaps qualificados alteram as triplas esperadas em `data/anotacoes-desenvolvimento-extracao.json`. A anotação deve ser revista, não ajustada para acomodar a regra.
- **O que foi conferido:** a v6 rodou sobre o texto dos 33 excertos do formulário. Saídas conferidas: negativa da Suzano registrada; Klabin com swaps IPCA→CDI e SOFR→pré distintos; objetivos de política marcados como `politica`; swaps da Irani sem `PROTEGE`.

## Propostas ainda não implementadas (por prioridade)

1. **Recuperação de seções de política.** Páginas decisivas não chegaram ao contexto: Suzano 4.1.1 (p. 35), exposição cambial da Suzano em 2025 (p. 105), indexadores da Klabin em 2024 (p. 122), notas 28.2/28.4 da Klabin em 2025 (p. 137/139). Sugestões:
   - expandir a recuperação para a página vizinha quando um trecho de nota de riscos é recuperado;
   - dar peso a títulos de seção (“Gerenciamento de riscos financeiros”, “Contabilidade de hedge”).
2. **Extração tabular com escopo e data.** As exposições líquidas (quadros “Consolidado”/“Controladora”) não entram no grafo, e a pergunta de comparação entre empresas faz o gerador inventar números. Uma etapa tabular deveria registrar valor, unidade, data, escopo e composição, porque as bases diferem entre empresas.
3. **Escopo a partir do cabeçalho do quadro ou da página.** Hoje o escopo vem só da frase, e as 85 declarações ficaram `nao_especificado`, embora as páginas indiquem Consolidado/Controladora em pelo menos 12 excertos.
4. **Seção documental e deduplicação.** Registrar se o trecho vem de notas explicativas, Relatório da Administração, release ou relatório do auditor. O mesmo texto da Suzano aparece no relatório e no release. Corrigir a extração em colunas do relatório do auditor (texto intercalado na Klabin 2025, p. 37).
5. **Versão dos comparativos.** A DFP 2025 da Klabin reapresenta a exposição de 2024: (32.958.188) mil contra (31.923.194) mil na DFP 2024. Declarações sobre um exercício precisam indicar de qual documento vêm.
6. **Mensagens de abstenção.** Diferenciar “exercício fora do acervo”, “nenhuma fonte recuperada” e “fontes recuperadas não sustentam”. Hoje todas viram “Não foi possível formar uma resposta validável”.
7. **Formulários de revisão.**
   - Incluir o texto exato dos trechos enviados ao modelo, além dos localizadores.
   - Registrar a versão do validador aplicada à saída arquivada. Exemplo: a regra atual de hedge accounting em `validar_resposta` parece capaz de bloquear a afirmação contraditada sobre a Suzano, mas o formulário mostra validação vazia.
8. **Avaliação.**
   - Manter um conjunto de referência reservado e anotado de forma independente antes de calcular precisão e recall.
   - Adjudicar as divergências entre os dois revisores.
   - Não usar o recall de localizadores como substituto de suporte: houve página presente com abstenção e com contradição.
