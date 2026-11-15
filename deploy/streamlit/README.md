# Implantação no Streamlit Community Cloud

A aplicação usa uma instância **AuraDB Free** e executa o mesmo Qwen GGUF em CPU no host da interface. O aplicativo não depende do computador de desenvolvimento. Esta configuração precisa ser verificada no provedor antes de anunciar um endereço público.

1. Crie uma instância AuraDB Free, preservando as credenciais fora do Git. Não selecione o trial de um plano pago.
2. Em um ambiente de preparação, instale `requirements-nuvem.txt` e configure `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` e `NEO4J_ACCESS_MODE=WRITE`. Execute aquisição, configuração, ingestão e indexação conforme o README principal. Faça uma auditoria do corpus antes da publicação da interface.
3. A execução manual `Reproducao completa` do GitHub Actions compila llama.cpp b7770 para Linux x86-64 e produz um pacote com SHA-256. Publique o pacote verificado como asset de uma release deste repositório. O pacote não inclui pesos ou credenciais.
4. No Community Cloud, selecione este repositório, a branch `main`, a entrada `deploy/streamlit/app.py` e Python 3.13.
5. Cadastre os valores abaixo nos **Secrets** da aplicação. A URL e o hash do runtime precisam corresponder ao asset compilado e verificado, não a valores de exemplo.

```toml
NEO4J_URI = "neo4j+s://<instancia>.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "<senha-da-instancia>"
NEO4J_ACCESS_MODE = "READ"
LLAMA_RUNTIME_URL = "https://github.com/victort01/graphrag-riscos-financeiros/releases/download/<tag>/llama-b7770-linux-x64.tar.gz"
LLAMA_RUNTIME_SHA256 = "<sha256-do-pacote>"
LLM_MODEL = "qwen-riscos-local"
LLM_ARTIFACT = "Qwen2.5-1.5B-Instruct-GGUF@91cad51170dc346986eccefdc2dd33a9da36ead9:Q4_K_M"
```

O primeiro acesso baixa os modelos e verifica seus checksums. O servidor do modelo escuta apenas em localhost. O histórico compartilhado de consultas fica oculto na interface pública; o usuário acompanha a tarefa da própria sessão. Apenas uma consulta é processada por vez.

`READ` é uma configuração de roteamento do driver, **não uma permissão de segurança**. Mantenha as guardas de Cypher e use credencial restrita quando a modalidade do banco permitir. Credenciais de administração nunca entram no navegador ou no repositório.

Verifique uma pergunta nova, uma resposta com caminho, abertura das fontes, abstenção sem acervo, reconexão e retomada após hibernação. Confira também memória e tempo de inicialização. Se os limites gratuitos não comportarem o modelo, essa implantação não pode ser considerada concluída nem substituída silenciosamente por respostas salvas.

Os serviços gratuitos têm limites e podem hibernar; endereço fixo não significa disponibilidade contínua garantida. Referências: [Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud), [recursos](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), [limites do AuraDB](https://neo4j.com/docs/aura/quotas-and-limits/).
