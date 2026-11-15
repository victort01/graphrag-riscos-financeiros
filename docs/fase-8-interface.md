# Interface em validação

O protótipo usa Streamlit 1.44.1 e Cytoscape.js 3.31.2, incluído localmente com sua licença MIT. O formulário chama diretamente o serviço Python; a API FastAPI prevista como possibilidade no plano não foi necessária para esta integração inicial.

O formulário recebe pergunta, empresas e exercício. A resposta mostra afirmações e nível documental. As abas apresentam subgrafo, fontes e rastreabilidade. No grafo, é possível mover nós, aplicar zoom, escolher um caminho ou uma afirmação e clicar em relações para inspecionar a citação e abrir a página oficial. O subgrafo usa os IDs e relações retornados pelo Neo4j.

O painel de rastreabilidade distingue a busca, o algoritmo e o contexto enviado ao modelo. O download JSON permite guardar a execução para a defesa. O protótipo inclui tratamento de pergunta vazia e falhas de infraestrutura. A verificação visual completa e a conferência da correspondência entre afirmação/caminho/fonte ainda estão em andamento.

Executar com `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 18501`. A implantação atual é local. Fontes, banco e modelo precisam estar preparados conforme o README.

Referências: [componentes Streamlit](https://docs.streamlit.io/1.44.0/develop/api-reference/custom-components/st.components.v1.html) e [Cytoscape.js](https://js.cytoscape.org/).
