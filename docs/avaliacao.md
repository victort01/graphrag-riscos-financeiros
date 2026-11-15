# Avaliação

Os experimentos distinguem integridade dos dados, localização de evidência, validade do contrato de resposta e suporte semântico. Os critérios assistidos sobre corpus conhecido não equivalem a gabarito humano independente.

## Extração e identidades

O conjunto `data/anotacoes-desenvolvimento-extracao.json` contém oito excertos, quinze menções e vinte e três relações esperadas, anotados com assistência de IA e usados para ajustar regras. Os resultados avaliam esse conjunto conhecido.

```powershell
.venv/Scripts/python scripts/avaliar_extracao.py
.venv/Scripts/python scripts/auditar_extracao.py --saida data/reports/auditoria-extracao.json
.venv/Scripts/python scripts/preparar_revisao.py --saida data/reports/revisao-extracao
```

A auditoria automatizada verificou a integridade das 85 declarações em 33 excertos: checksum, tipos, identidade do emissor e ligação com o trecho. Não foram encontradas inconsistências nesses critérios. Isso não mede precisão, recall semântico ou cobertura do relatório. As 85 declarações continuam sem qualificação jurídica reconhecida pelas regras.

A revisão documental deve conferir menções equivalentes, relações, qualificadores e omissões nos PDFs. O comparador recusa formulários pendentes e exige revisores distintos. F1 simétrico e Jaccard medem concordância, não acurácia; divergências exigem adjudicação. Essa revisão não foi registrada como concluída.

## Protocolo prospectivo

`data/perguntas-validacao-v1.json` fixa doze perguntas e critérios antes da execução. O SHA-256 é `a8c51c2f3319b98dff278d9c4a21ecfc19e595a475a0581c2f8843528ac3addd`. Há dez perguntas com evidências esperadas e duas que exigem abstenção: exercício fora do acervo e cálculo/ranking fora do recorte narrativo. V08–V10 são controles próximos ao desenvolvimento. O corpus e a seleção assistida limitam a independência do experimento.

Comparam-se vetor, híbrido e híbrido com caminhos, mantendo filtros, modelo e 3.500 caracteres. A variante com caminhos reutiliza os candidatos híbridos. A geração usa contextos congelados, ordem embaralhada com seed fixa, temperatura zero e as mesmas guardas por rodada.

```powershell
.venv/Scripts/python scripts/avaliar_recuperacao.py --conjunto data/perguntas-validacao-v1.json --saida data/reports/recuperacao-v1.json
.venv/Scripts/python scripts/avaliar_respostas.py --recuperacao data/reports/recuperacao-v1.json --conjunto data/perguntas-validacao-v1.json --saida data/reports/respostas-v1.json
.venv/Scripts/python scripts/resumir_avaliacao.py --conjunto data/perguntas-validacao-v1.json --recuperacao data/reports/recuperacao-v1.json --respostas data/reports/respostas-v1.json --saida data/reports/resumo-v1.json
```

Os comandos executados com o código atual usam a política corrigida. Os resultados originais V1 antecedem as correções identificadas abaixo; código e hashes de cada execução estão no [resumo versionado](../data/avaliacao-validacao-v1-resumo.json). Não se espera que uma reexecução da versão atual reproduza a política anterior ou a mesma latência.

## Recuperação

As 36 recuperações concluíram sem falhas. Uma evidência é localizada por documento, página e termo normalizado. A média é calculada por pergunta; não representa todas as fontes possíveis nem a correção das respostas. As duas perguntas sem evidência esperada ficam fora desse recall.

| Variante V1 | Recall nos candidatos (10 perguntas) | Recall no contexto (10) | Contexto sem os três controles (7) |
|---|---:|---:|---:|
| Vetorial | 40% | 30% | 28,6% |
| Híbrida | 95% | 70% | 64,3% |
| Com caminhos | 95% | 65% | 50% |

Em V01, fontes sobre hedge natural expulsaram a negativa explícita sobre hedge accounting localizada pelo híbrido na página PDF 35 da Suzano 2024. A correção mantém as fontes híbridas e acrescenta caminhos e suas evidências apenas quando cabem no orçamento. Na reanálise dos mesmos contextos congelados, o recall com caminhos foi 70%, com nove caminhos em sete perguntas. Essa é uma análise posterior ao diagnóstico; não é novo teste independente nem ganho sobre o híbrido.

## Geração e abstenção

Das 36 execuções, 34 concluíram a inferência e duas tiveram timeout. As falhas foram preservadas e não viraram abstenção factual.

| Variante V1 | Falhas técnicas | Saídas com afirmações | Abstenções | Abstenções nos dois casos obrigatórios |
|---|---:|---:|---:|---:|
| Vetorial | 0 | 1 | 11 | 2/2 |
| Híbrida | 1 | 2 | 9 | 2/2 |
| Com caminhos | 1 | 5 | 6 | 2/2 |

Mais saídas com afirmações não significam mais respostas corretas. A inspeção assistida encontrou atribuição de tratamento contábil à empresa errada e confusão entre proteção econômica e hedge accounting. Guardas posteriores exigem documento da empresa citada, declaração contábil específica e preservação da negativa de adoção. O filtro de pertinência também foi corrigido para não excluir explicações de liquidez em perguntas sobre financiamento.

A reaplicação às saídas arquivadas manteve uma saída com afirmações no vetor, uma no híbrido e três no grafo. Houve apenas revalidação determinística, sem nova inferência ou revisão humana. Os textos e resultados originais continuam preservados. Bloquear erros conhecidos não comprova mitigação geral de alucinações.

```powershell
.venv/Scripts/python scripts/revalidar_respostas.py data/reports/respostas-v1.json data/reports/respostas-revalidadas.json
.venv/Scripts/python scripts/revisar_respostas.py preparar data/reports/respostas-v1.json data/reports/revisao-respostas --mapa data/reports/mapa-revisao.json
.venv/Scripts/python scripts/revisar_respostas.py comparar data/reports/revisao-respostas/lote.json data/reports/revisao-respostas/revisor-1.json data/reports/revisao-respostas/revisor-2.json
```

Os 34 itens sem falha técnica foram preparados para revisão. Cada pessoa deve abrir as páginas citadas e classificar apoio por afirmação, pertinência, empresa/exercício, cobertura e adequação da abstenção. O método é omitido, embora caminhos possam permitir inferi-lo. Formulários pendentes e conteúdo alterado são recusados pelo comparador. Nenhuma taxa de alucinação é publicada como validada por pessoas.

## Reprodução e limites

A [reprodução em Linux](../data/reproducao-linux.json) partiu de checkout limpo e banco vazio, conferiu os seis PDFs, ingeriu o corpus, indexou 3.918 trechos, executou testes por HTTP e Bolt e concluiu uma consulta real. O checksum de conteúdo das 85 declarações coincidiu com o Windows. Os workflows identificam os commits efetivamente verificados; alterações posteriores possuem registros próprios.

Os testes operacionais não comprovam correção semântica. A amostra pequena, o corpus conhecido, os controles próximos ao desenvolvimento e os critérios assistidos limitam conclusões. Latências são descritivas e sofreram disputa de memória; não se atribui causalmente uma diferença ao método. A avaliação humana e um novo conjunto externo à correção seguem necessários para medir suporte e generalização.

O [smoke anterior](../data/avaliacao-recuperacao-smoke-completa-resumo.json), com duas perguntas conhecidas da Irani, permanece como registro de desenvolvimento. Seus resultados não substituem a rodada prospectiva nem a revisão documental.
