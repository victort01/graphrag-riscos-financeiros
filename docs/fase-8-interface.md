# Interface em validação

O protótipo usa Streamlit 1.44.1 e Cytoscape.js 3.31.2, incluído localmente com sua licença MIT. O formulário chama diretamente o serviço Python; a API FastAPI prevista como possibilidade no plano não foi necessária para esta integração inicial.

O formulário recebe pergunta, empresas e exercício. A resposta mostra afirmações e nível documental. As abas apresentam subgrafo, fontes e rastreabilidade. No grafo, é possível mover nós, aplicar zoom, escolher um caminho ou uma afirmação e clicar em relações para inspecionar a citação e abrir a página oficial. O subgrafo usa os IDs e relações retornados pelo Neo4j.

O painel de rastreabilidade distingue candidatos por método, nós financeiros recuperados, enviados e citados, trechos enviados/citados, algoritmo e contexto recebido pelo modelo. O download JSON permite guardar a execução para a defesa. Cada resultado concluído é arquivado localmente; o botão de retomada mostra a pergunta e a data originais e não faz uma nova inferência.

Em 15/11/2026, a verificação visual utilizou a execução de desenvolvimento sobre ACC da Irani, gerada anteriormente e reavaliada no pós-processamento. Foram observados: resposta parcial com confiança limitada; realce do caminho de dois saltos por seleção da afirmação; inspeção de `TEM_OBRIGACAO` e `COMPENSA_VARIACOES_DE`; citação da página 124; abertura do PDF oficial com `#page=124`; fonte E1 marcada como citada; abas de fontes e rastreabilidade. As capturas [do grafo](assets/interface-verificacao.jpg) e [da evidência](assets/interface-evidencia.jpg) registram a inspeção em tela estreita. Não representam uma nova inferência nem avaliação independente da resposta.

A inspeção revelou o ajuste inicial incorreto do canvas, sobretudo ao alternar abas. O componente passou a ajustar tamanho/zoom ao tornar-se visível, evitando recalcular o enquadramento com dimensão zero. O botão Ajustar zoom continua disponível. Quatro testes com o AppTest do Streamlit verificam pergunta vazia sem backend, falha explícita de infraestrutura, filtros incompatíveis e abstenção sem evidências; os serviços são substituídos nesses testes. A correspondência entre payload e subgrafo é verificada separadamente nos testes de contexto.

A consulta ao vivo teve desconexão WebSocket durante a inferência local. O fluxo salvo foi verificado, mas a estabilidade de uma nova execução completa pelo navegador ainda é pendência desta fase. O arquivamento não torna uma inferência interrompida retomável. A versão atual não deve ser apresentada como interface integralmente validada em execução ao vivo.

Executar com `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 18501`. A implantação atual é local. Fontes, banco e modelo precisam estar preparados conforme o README.

Referências: [componentes Streamlit](https://docs.streamlit.io/1.44.0/develop/api-reference/custom-components/st.components.v1.html) e [Cytoscape.js](https://js.cytoscape.org/).
