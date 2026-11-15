# GraphRAG de riscos financeiros

Aplicação de consulta a exposições cambiais, obrigações e medidas de proteção descritas em relatórios oficiais de Suzano, Klabin e Irani. Combina busca vetorial e textual, Cypher gerado por um modelo de linguagem e caminhos financeiros no Neo4j. A interface exibe fontes, páginas, consultas e o subgrafo usado como contexto.

O acervo reúne seis relatórios de 2024 e 2025, com 954 páginas. A rodada V1 documentou 3.918 trechos narrativos elegíveis e 85 declarações extraídas; esses totais identificam aquela versão do pipeline. O extrator atual integra as correções de tratamento contábil, programas e leitura em colunas e exige reingestão antes de atualizar os totais. A cobertura é narrativa: tabelas e montantes não estão validados para cálculo de exposição líquida ou classificação de risco entre empresas. A avaliação prospectiva usa perguntas e critérios assistidos sobre corpus conhecido. Os resultados não demonstram superioridade geral nem redução de alucinações em teste independente.

## Materiais

- [Artigo técnico](docs/artigo/artigo-revisao.pdf).
- [Apresentação em PDF](docs/apresentacao/apresentacao-revisao.pdf) e [PowerPoint](docs/apresentacao/apresentacao-revisao.pptx).
- [Arquitetura e modelo de dados](docs/arquitetura.md).
- [Avaliação e reprodução dos experimentos](docs/avaliacao.md).
- [Revisão assistida por IA](docs/revisao-assistida-IA/revisao-assistida-IA.md) e [melhorias propostas](docs/melhorias-propostas.md). Sugestões para conferência; a revisão humana permanece pendente.

[Abrir a aplicação](https://graphrag-riscos-financeiros.streamlit.app/). Hospedagem gratuita no Streamlit Community Cloud com Neo4j AuraDB Free e inferência no próprio host. Uma consulta real com fontes, caminho no contexto e retomada após recarregar foi verificada. A geração em CPU pode levar minutos e os serviços podem hibernar. Consulte o [registro da implantação](data/validacao-implantacao.json) e a [configuração para reprodução](deploy/streamlit/README.md).

O artigo e a apresentação registram os resultados disponíveis e os limites da avaliação. A revisão humana independente de extração e respostas permanece pendente.

## Requisitos

Python 3.11 ou superior, Docker com Neo4j 5.26 Community e um servidor llama.cpp compatível com o modelo GGUF do catálogo. O ambiente completo verificado usa Windows e Python 3.13. Os pesos ocupam aproximadamente 1,24 GB, além do cache do tokenizer.

## Instalação e dados

Execute a partir da raiz do repositório. No Windows:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt -r requirements-modelos.txt -r requirements-ui.txt
Copy-Item .env.example .env
```

Defina `NEO4J_PASSWORD` no `.env`. Para reproduzir as dependências transitivas do ambiente Windows com Python 3.13, use `requirements-lock-win-py313.txt` em lugar dos três arquivos de requisitos por função.

```powershell
.venv/Scripts/python scripts/validar_fontes.py
.venv/Scripts/python scripts/verificar_corpus.py
.venv/Scripts/python scripts/baixar_modelos.py
```

Os scripts baixam os PDFs e modelos dos endereços catalogados e conferem os checksums. `validar_fontes.py --offline` usa o cache existente; `--id` seleciona um documento. [Fontes](data/manifesto.json), [identidades CVM](data/identidades-cvm.json) e [modelos](data/modelos.json) são versionados. PDFs, extrações integrais, pesos, credenciais e execuções ficam fora do Git.

## Banco, ingestão e indexação

```powershell
./scripts/modo_banco.ps1 -Modo ingestao
.venv/Scripts/python scripts/configurar_banco.py
.venv/Scripts/python scripts/ingerir.py
.venv/Scripts/python scripts/indexar.py
./scripts/modo_banco.ps1 -Modo consulta
```

O banco HTTP fica em `http://127.0.0.1:17474`. A carga é transacional por documento e pode ser reexecutada. `ingerir.py --id irani-dfp-2025 --somente-preparar` prepara a extração sem publicá-la. `indexar.py --reindexar` recalcula os vetores. Habilite ingestão para escrever e retorne a consulta antes de usar o LLM. A troca de modo preserva o volume de dados.

## Modelo e interface

Use [llama.cpp b7770](https://github.com/ggml-org/llama.cpp/releases/tag/b7770) para servir o GGUF. O binário Windows CPU verificado é `llama-b7770-bin-win-cpu-x64.zip`, SHA-256 `96aaa9fa5db8a3a49dcf42547cf8f131e493902111e28fa6085dccd52e5406c5`. Extraia em `data/models/llama`.

Em um terminal:

```powershell
./scripts/iniciar_modelo.ps1
```

Em outro terminal:

```powershell
./scripts/iniciar_aplicacao.ps1
```

A interface abre em `http://127.0.0.1:18501`. Exemplo de pergunta: **Como a Irani conecta ACC a recebíveis de exportações?** Selecione Irani e o exercício 2025.

Para executar pelo terminal:

```powershell
.venv/Scripts/python scripts/responder.py "Como a Irani conecta ACC a recebíveis de exportações?" --empresa 92791243000103 --periodo 2025-12-31 --salvar data/reports/exemplo.json
```

As respostas preservam contexto, candidatos, fontes, caminhos, consultas, saída original e validação. A interface permite carregar uma execução arquivada ou retomar uma tarefa após desconexão do navegador. Reiniciar o servidor interrompe a inferência. O deployment atual usa um único processo e uma consulta em andamento por vez.

Em Linux/macOS, use `.venv/bin/python`, inicie o servidor GGUF com os argumentos de `scripts/iniciar_modelo.ps1` e execute `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 18501`. Para alternar o banco, use `NEO4J_READ_ONLY=false docker compose up -d` na ingestão e `NEO4J_READ_ONLY=true docker compose up -d` na consulta, aguardando `scripts/aguardar_banco.py` após cada troca. Esses comandos substituem os scripts PowerShell.

## Testes e avaliação

```powershell
.venv/Scripts/python -m unittest discover -s tests -v
```

Os testes unitários não exigem modelos ou banco. As verificações opcionais usam `TESTAR_NEO4J=1` para escrita no banco de teste e `TESTAR_CORPUS=1` para o corpus já ingerido. Execute testes de escrita com o banco em modo de ingestão e retorne a consulta ao terminar.

O [protocolo de avaliação](docs/avaliacao.md) descreve extração, recuperação, respostas e revisão documental. Uma rodada de 12 perguntas fixadas antes da execução concluiu 36 recuperações e 34 gerações; dois timeouts foram preservados. O recall médio dos localizadores no contexto, em dez perguntas com evidência esperada, foi de 30% no vetor, 70% no híbrido e 65% na primeira política com caminhos. A correção posterior preserva as fontes híbridas e atingiu 70% na reanálise conhecida. Esses números não medem correção semântica das respostas.

## Comparação de modelos

A rodada V2 usa [perguntas diferentes de V1](data/perguntas-validacao-v2.json) e [dois modelos fixados](data/modelos-comparacao-v2.json): Qwen2.5 de 1.5B e 3B, ambos Q4_K_M. A recuperação é executada uma vez; os modelos recebem os mesmos contextos, conferidos por hash. O experimento compara geração, sem atribuir ao modelo maior uma melhoria ainda não medida.

```bash
python scripts/comparar_modelos.py --saida data/reports/nova-comparacao
```

O comando exige corpus reingerido/indexado e o runtime Linux catalogado em `data/models/llama-linux/llama-server`; `--servidor` permite outro caminho. A porta 18081 deve estar livre. Pesos são adquiridos pelos hashes oficiais, um modelo é carregado por vez e os resultados brutos ficam fora do Git. A revisão semântica permanece separada das métricas técnicas.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `app.py` e `ui/` | Interface Streamlit e visualização do grafo. |
| `src/riscos/` | Extração, identidades, ingestão, busca, caminhos, resposta e auditoria. |
| `scripts/` | Aquisição, configuração, execução e avaliação. |
| `tests/` | Testes unitários e de integração. |
| `data/` | Catálogos, conjuntos de desenvolvimento e resultados auditáveis. |
| `docs/` | Artigo, apresentação e documentação técnica. |

Projeto de Tendências em Ciência da Computação do Centro Universitário de João Pessoa (Unipê). Fontes, bibliotecas, modelos e assistência de IA estão registrados em [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
