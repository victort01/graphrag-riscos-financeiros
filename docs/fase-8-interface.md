# Interface: verificação operacional concluída

O protótipo usa Streamlit 1.44.1 e Cytoscape.js 3.31.2, incluído localmente com sua licença MIT. O formulário chama diretamente o serviço Python; a API FastAPI prevista como possibilidade no plano não foi necessária para esta integração inicial.

O formulário recebe pergunta, empresas e exercício. A resposta mostra afirmações e nível documental. As abas apresentam subgrafo, fontes e rastreabilidade. No grafo, é possível mover nós, aplicar zoom, escolher um caminho ou uma afirmação e clicar em relações para inspecionar a citação e abrir a página oficial. O subgrafo usa os IDs e relações retornados pelo Neo4j.

O painel de rastreabilidade distingue candidatos por método, nós financeiros recuperados, enviados e citados, trechos enviados/citados, algoritmo e contexto recebido pelo modelo. O download JSON permite guardar a execução para a defesa. Cada resultado concluído é arquivado localmente; o botão de retomada mostra a pergunta e a data originais e não faz uma nova inferência.

Em 15/11/2026, a verificação visual utilizou a execução de desenvolvimento sobre ACC da Irani, gerada anteriormente e reavaliada no pós-processamento. Foram observados: resposta parcial com confiança limitada; realce do caminho de dois saltos por seleção da afirmação; inspeção de `TEM_OBRIGACAO` e `COMPENSA_VARIACOES_DE`; citação da página 124; abertura do PDF oficial com `#page=124`; fonte E1 marcada como citada; abas de fontes e rastreabilidade. As capturas [do grafo](assets/interface-verificacao.jpg) e [da evidência](assets/interface-evidencia.jpg) registram a inspeção em tela estreita. Não representam uma nova inferência nem avaliação independente da resposta.

A inspeção revelou o ajuste inicial incorreto do canvas, sobretudo ao alternar abas. O componente passou a ajustar tamanho/zoom ao tornar-se visível, evitando recalcular o enquadramento com dimensão zero. O botão Ajustar zoom continua disponível. Quatro testes com o AppTest do Streamlit verificam pergunta vazia sem backend, falha explícita de infraestrutura, filtros incompatíveis e abstenção sem evidências; os serviços são substituídos nesses testes. A correspondência entre payload e subgrafo é verificada separadamente nos testes de contexto.

A desconexão WebSocket observada motivou a separação do processamento da sessão do navegador. `trabalhos.py` executa uma consulta por vez em uma thread, registra sua etapa em arquivo e arquiva o resultado concluído. O fragmento da interface acompanha a etapa. Depois de recarregar a página, o botão Retomar última consulta reconecta à tarefa original; não solicita outra inferência. Novas solicitações são recusadas enquanto a consulta anterior estiver ativa, evitando disputar os recursos do modelo local.

Uma nova consulta real sobre ACC, iniciada pela tela, foi recarregada durante a inferência e retomada. A resposta apareceu ao concluir, com confiança limitada e fontes/caminhos preservados. A execução levou **335,269 s**; esse valor descreve uma rodada na máquina de desenvolvimento, sem controle de aquecimento ou carga. Foram observados o realce por afirmação, arraste de nó, pan, zoom, ajuste de enquadramento e inspeção da relação com a fonte da página 124. O [registro dessa execução](../data/validacao-interface.json) e a [captura da consulta retomada](assets/interface-consulta-retomada.jpg) preservam as evidências. O caso real sem documentos de 2030 também exibiu abstenção e o motivo correto.

Quatro testes do gerenciador verificam conclusão/arquivo sem cliente conectado, recusa de concorrência, falha operacional sem resposta factual e detecção de tarefa perdida após reinicialização. Os testes da interface verificam também que a conclusão não reenvia a pergunta. A implementação atual pressupõe um único processo Streamlit local; não há teste de carga ou garantia de disponibilidade de produção. A parada do servidor interrompe a inferência e exige repeti-la; a tolerância demonstrada cobre a desconexão do navegador.

A fase 8 está concluída quanto à implementação e à verificação operacional no recorte atual. A correção semântica das respostas, a revisão independente e o benefício científico da recuperação continuam nas fases 7 e 9.

Executar com `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 18501`. A implantação atual é local. Fontes, banco e modelo precisam estar preparados conforme o README.

Referências: [componentes Streamlit](https://docs.streamlit.io/1.44.0/develop/api-reference/custom-components/st.components.v1.html) e [Cytoscape.js](https://js.cytoscape.org/).
