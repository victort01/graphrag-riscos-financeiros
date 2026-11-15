# Revisão documental das respostas

O lote em `data/revisao-respostas-smoke/` contém seis respostas finais de duas perguntas de desenvolvimento, após o contrato de IDs contextuais. Não é o conjunto reservado. Dois integrantes podem revisar os formulários separadamente, sem consultar a anotação do colega.

O rótulo da variante foi removido dos itens e sua ordem foi embaralhada. O mapa fica separado em `data/reports/mapa-revisao-respostas-smoke-v2.json`. Isso reduz a exposição direta ao método, mas não constitui cegamento completo: a presença de caminhos pode permitir identificar a variante.

## Como preencher

1. Abrir `revisor-1.json` ou `revisor-2.json` e identificar a pessoa no campo `revisor`.
2. Em cada item, abrir as URLs e as páginas PDF citadas em `fontes`. Elas são localizadores com hashes do texto do contexto. O texto integral da recuperação fica no relatório local; o julgamento deve conferir o documento e seu escopo, não presumir que a extração seja correta.
3. Para cada afirmação, preencher `apoio` com `integral`, `parcial`, `sem_apoio` ou `indeterminavel`. Preencher `pertinente` e `empresa_periodo_corretos` com `true` ou `false`. Justificar apoio incompleto, imprecisão ou falta de pertinência e indicar fonte/página na justificativa.
4. Preencher `cobertura_pergunta` com `completa`, `parcial`, `nenhuma` ou `indeterminavel`. Se não houver afirmações finais, qualificar `abstencao_adequada` como `adequada`, `indevida` ou `indeterminavel`. Em respostas com afirmações, manter esse campo como `null`.
5. Registrar dúvidas em `observacoes` e alterar `estado` para `concluida` somente depois de julgar o item. Não modificar perguntas, respostas, fontes, caminhos, IDs ou hashes.

Uma referência válida não comprova que a fonte sustenta a frase. Uma frase relacionada ao assunto pode não responder à pergunta. A ausência de resposta do modelo não demonstra que o relatório não contenha a informação. Revisar essas dimensões separadamente.

## Comparar

```powershell
.venv/Scripts/python scripts/revisar_respostas.py comparar data/revisao-respostas-smoke/lote.json data/revisao-respostas-smoke/revisor-1.json data/revisao-respostas-smoke/revisor-2.json
```

O comparador recusa pessoas não identificadas, formulários pendentes, alterações no conteúdo avaliado, rótulos inválidos ou revisão atribuída à mesma pessoa. Compara os rótulos e lista divergências para adjudicação. Concordância não equivale a acurácia. As divergências precisam ser discutidas e resolvidas com a evidência antes de calcular métricas de qualidade.

As falhas de infraestrutura ficam no relatório de geração e não recebem o rótulo de abstenção. O lote registra quantas execuções foram excluídas por falha. As respostas originais e o pós-processamento estão preservados localmente para análise de erros, mas os formulários avaliam a resposta final apresentada ao usuário.
