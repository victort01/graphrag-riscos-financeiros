# Implantação no Streamlit Community Cloud

A aplicação usa uma instância **AuraDB Free** e executa o mesmo Qwen GGUF em CPU no host da interface. O aplicativo não depende do computador de desenvolvimento. A [aplicação publicada](https://graphrag-riscos-financeiros.streamlit.app/) concluiu uma consulta real no provedor. O [registro operacional](../../data/validacao-implantacao.json) documenta versões, latência e limites da checagem.

1. Crie uma instância AuraDB Free, preservando as credenciais fora do Git. Não selecione o trial de um plano pago.
2. Em um ambiente de preparação, instale `requirements-nuvem.txt` e configure `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` e `NEO4J_ACCESS_MODE=WRITE`. Execute aquisição, configuração, ingestão e indexação conforme o README principal. Faça uma auditoria do corpus antes da publicação da interface.
3. O catálogo `data/runtime-linux.json` identifica o runtime CPU publicado, seu SHA-256 e a execução do GitHub Actions que o compilou e verificou. O pacote não inclui pesos ou credenciais. Uma nova compilação pode ser feita pela execução manual `Reproducao completa`.
4. No Community Cloud, selecione este repositório, a branch `main`, a entrada `deploy/streamlit/app.py` e Python 3.13.
5. Cadastre os valores abaixo nos **Secrets** da aplicação. Use as credenciais reais da instância.

```toml
NEO4J_URI = "neo4j+s://<instancia>.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "<senha-da-instancia>"
NEO4J_ACCESS_MODE = "READ"
LLM_MODEL = "qwen-riscos-local"
LLM_ARTIFACT = "Qwen2.5-1.5B-Instruct-GGUF@91cad51170dc346986eccefdc2dd33a9da36ead9:Q4_K_M"
```

O primeiro acesso baixa os modelos e verifica seus checksums. O servidor do modelo escuta apenas em localhost. O histórico compartilhado de consultas fica oculto na interface pública; o usuário acompanha sua tarefa por um identificador aleatório na URL, inclusive após recarregar a página. Quem receber essa URL poderá consultar o mesmo resultado enquanto os arquivos existirem no host; use o endereço raiz para divulgar a aplicação. Apenas uma consulta é processada por vez.

`READ` é uma configuração de roteamento do driver, **não uma permissão de segurança**. Mantenha as guardas de Cypher e use credencial restrita quando a modalidade do banco permitir. Credenciais de administração nunca entram no navegador ou no repositório.

Na verificação registrada, a pergunta sobre ACC da Irani recuperou a página PDF 124, enviou um caminho de dois saltos ao modelo e gerou uma afirmação por citação direta, com confiança limitada. A retomada da mesma tarefa após recarregar, o download do JSON e a abertura do PDF na página citada foram conferidos. Em janela privada, a interface abriu sem login e recusou uma pergunta sobre 2029 por ausência de acervo. Não houve teste de carga ou de hibernação prolongada. Ao reproduzir, verifique também uma pergunta nova, abertura das fontes e abstenção sem acervo. Confira também memória e tempo de inicialização. Se os limites gratuitos não comportarem o modelo, essa implantação não pode ser considerada concluída nem substituída silenciosamente por respostas salvas.

Os serviços gratuitos têm limites e podem hibernar; endereço fixo não significa disponibilidade contínua garantida. Referências: [Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud), [recursos](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), [limites do AuraDB](https://neo4j.com/docs/aura/quotas-and-limits/).
