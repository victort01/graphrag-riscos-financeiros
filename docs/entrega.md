# Links e materiais de entrega

Situação em 15/11/2026. Os materiais científicos continuam em revisão; a visibilidade pública não altera o estado de validação do projeto.

| Entrega | Link ou situação |
|---|---|
| Código público no GitHub | https://github.com/victort01/graphrag-riscos-financeiros |
| Aplicação em nuvem | Endereço público ainda pendente de implantação e verificação. |
| Apresentação editável | [PowerPoint](apresentacao/apresentacao-revisao.pptx) |
| Apresentação para exibição | [PDF](apresentacao/apresentacao-revisao.pdf) |
| Artigo IEEE | [PDF](artigo/artigo-revisao.pdf) e [fonte LaTeX](artigo/artigo-revisao.tex) |

## Requisito de hospedagem

O usuário escolheu hospedagem permanente e gratuita. A aplicação deverá ter endereço fixo e funcionar fora deste computador, mantendo o Neo4j e a geração real de respostas. Um endereço local não constitui a entrega em nuvem.

Ainda é necessário selecionar e configurar contas de serviços compatíveis, verificar seus limites gratuitos, preparar a conexão e medir o consumo de memória do modelo em nuvem. Não foram contratados planos pagos. A disponibilidade contínua e o comportamento após inatividade precisam ser conferidos no provedor escolhido antes de anunciar o endereço como pronto.

Streamlit Community Cloud e Neo4j Aura Free são candidatos a avaliar, com o modelo local sujeito ao limite de memória da aplicação. Não há implantação concluída nesses serviços. A documentação atual do Hugging Face informa exigência de plano pago para criar novos Spaces com computação; essa opção não foi escolhida para o requisito de custo zero.

Fontes consultadas em 15/11/2026:

- Streamlit Community Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Limites de recursos: https://docs.streamlit.io/knowledge-base/deploy/resource-limits
- Neo4j Aura: https://neo4j.com/pricing/
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces-overview

O convite individual ao professor não foi enviado. O acesso de leitura ao código já está disponível pela visibilidade pública autorizada pelo usuário.
