# GraphRAG de riscos financeiros

Projeto final de Tendências em Ciência da Computação do Centro Universitário de João Pessoa (Unipê).

Consulte o [andamento por fase](docs/andamento.md) e a [matriz de requisitos do enunciado](docs/matriz-requisitos.md) para distinguir as entregas verificadas das pendências.

O sistema consulta exposições cambiais, obrigações em moeda estrangeira e mecanismos de proteção declarados em documentos de companhias brasileiras. A implementação e a avaliação ainda estão em andamento.

A fase 1 está concluída. Foram baixadas e extraídas seis demonstrações financeiras completas de Suzano, Klabin e Irani, dos exercícios de 2024 e 2025. O conjunto tem 954 páginas, dez perguntas exploratórias e dezesseis localizadores de evidência. A diferença de subsegmento entre as empresas e os limites das tabelas extraídas estão documentados no [relatório de viabilidade](docs/fase-1-viabilidade.md).

## Reproduzir a validação documental

Com Python 3.11 ou superior, crie um ambiente virtual e instale as dependências.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/validar_fontes.py
.venv/Scripts/python scripts/verificar_corpus.py
```

Em Linux ou macOS, use o executável .venv/bin/python. O primeiro comando de validação baixa os PDFs oficiais e grava o texto por página e os diagnósticos em data/. Se os arquivos já estiverem no cache, pode ser executado com --offline. A opção --id permite selecionar um documento do manifesto.

O ambiente completo verificado no Windows com Python 3.13 tem dependências transitivas fixadas em `requirements-lock-win-py313.txt`. Nesse ambiente, pode-se instalar tudo com `.venv/Scripts/python -m pip install -r requirements-lock-win-py313.txt`. O lock é específico dessa plataforma; os arquivos `requirements*.txt` por função continuam disponíveis para outros ambientes.

O repositório inclui [fontes e checksums](data/manifesto.json), [métricas de extração](data/qualidade-extracao.json), [evidências de exploração](data/evidencias-exploratorias.json) e [perguntas de desenvolvimento](data/perguntas-exploratorias.json). Os PDFs e o texto integral são adquiridos localmente. A fase 3 tratará tabelas embutidas como imagem e a validação de suas unidades e colunas.

## Execução por fases

1. Viabilidade dos documentos e fechamento do recorte.
2. Ontologia e modelagem LPG.
3. Aquisição e Text-to-Graph automatizados.
4. Resolução de entidades e qualidade da extração.
5. Recuperação híbrida e geração de Cypher.
6. Algoritmo de grafo e regras de conhecimento.
7. Respostas, procedência e confiança documental.
8. Interface e subgrafo interativo.
9. Avaliação científica e testes operacionais.
10. Artigo, apresentação e defesa.

O banco adotado é Neo4j. O escopo atual está no planejamento em docs/plano-execucao.md.

## Inicializar o Neo4j

Copie .env.example para .env e defina uma senha local com pelo menos oito caracteres. Execute os comandos no diretório do repositório.

```powershell
./scripts/modo_banco.ps1 -Modo ingestao
docker compose logs neo4j
python scripts/configurar_banco.py
$env:TESTAR_NEO4J='1'
python -m unittest discover -s tests -v
```

Aguarde a mensagem Started. no log antes de configurar. O banco fica disponível em http://127.0.0.1:17474. A [modelagem LPG](docs/fase-2-modelagem.md) documenta declarações, temporalidade e regras de evidência. A fase 2 foi verificada com constraints, índices Range/Fulltext/vetorial e consultas operacionais.

## Ingestão de narrativas

```powershell
python scripts/ingerir.py
python scripts/ingerir.py --id irani-dfp-2025 --somente-preparar
```

A carga publica relações com evidência, empresa e período em uma transação por documento. Ela é retomável e mantém o estado de tabelas como pendente. A [documentação da fase 3](docs/fase-3-ingestao.md) descreve as regras de extração e os limites atuais.

## Modelos, busca e interface

Instale as dependências adicionais no mesmo ambiente virtual usado anteriormente.

```powershell
.venv/Scripts/python -m pip install -r requirements-modelos.txt -r requirements-ui.txt
.venv/Scripts/python scripts/baixar_modelos.py
$env:EMBEDDING_ONNX_PATH=(Resolve-Path data/models/minilm-quint8.onnx).Path
.venv/Scripts/python scripts/indexar.py
./scripts/modo_banco.ps1 -Modo consulta
```

O download dos dois modelos ocupa aproximadamente 1,24 GB, além do cache do tokenizer. Os arquivos grandes ficam fora do Git. Os pesos têm revisão e checksum em [data/modelos.json](data/modelos.json). A primeira indexação pode baixar os arquivos do tokenizer pelo Hugging Face Hub.

Use [llama.cpp b7770](https://github.com/ggml-org/llama.cpp/releases/tag/b7770) para servir o GGUF. No Windows, o binário CPU verificado é `llama-b7770-bin-win-cpu-x64.zip`; seu SHA-256 é `96aaa9fa5db8a3a49dcf42547cf8f131e493902111e28fa6085dccd52e5406c5`. Extraia seus arquivos em `data/models/llama`. O script abaixo usa os caminhos padrão do projeto. Mantenha esse terminal ativo.

```powershell
./scripts/iniciar_modelo.ps1
```

Em outro terminal, usando o mesmo ambiente, execute a consulta ou a interface.

```powershell
$env:EMBEDDING_ONNX_PATH=(Resolve-Path data/models/minilm-quint8.onnx).Path
.venv/Scripts/python scripts/consultar.py "Como a Irani conecta ACC a recebíveis de exportações?" --empresa 92791243000103 --periodo 2025-12-31
.venv/Scripts/python scripts/responder.py "Como a Irani conecta ACC a recebíveis de exportações?" --empresa 92791243000103 --periodo 2025-12-31 --salvar data/reports/exemplo.json
.venv/Scripts/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 18501
```

A interface fica em http://127.0.0.1:18501. Em Linux/macOS, use `.venv/bin/python`, execute `llama-server` com os argumentos do script e alterne o banco com `NEO4J_READ_ONLY=false docker compose up -d` para ingestão e `NEO4J_READ_ONLY=true docker compose up -d` para consulta.

No Windows, `./scripts/iniciar_aplicacao.ps1` também inicia a interface pelo ambiente virtual do projeto. Os parâmetros `-Servidor` e `-Modelo` de `iniciar_modelo.ps1` permitem outros caminhos. Se trocar o artefato, atualize `LLM_ARTIFACT` no `.env` e repita a avaliação.

Cada resposta concluída pela interface ou pelo CLI é arquivada em `data/reports/execucoes/`, fora do Git. A opção **Carregar última execução salva** reabre o resultado com a pergunta, data, modelo e versão originais, sem nova inferência. A execução ainda em andamento não é um checkpoint retomável; uma desconexão pode exigir repetir a consulta. O JSON exportado preserva contexto, candidatos, consultas, caminhos, saída original e validação.

O banco inicia somente leitura por padrão. Antes de alterar esquema, ingerir ou indexar, habilite o modo de ingestão; ao terminar, volte para consulta. Esse fluxo preserva o volume de dados. Não use `docker compose down -v` para trocar modos.

O [módulo de busca](docs/fase-5-recuperacao.md) combina Fulltext, vetor e Cypher gerado pelo modelo. Os [caminhos financeiros](docs/fase-6-caminhos.md) acrescentam relações e evidências antes da resposta. As regras de [confiança documental](docs/fase-7-respostas.md) e o estado da [interface](docs/fase-8-interface.md) documentam o que já foi verificado e o que permanece pendente.

## Testes e limites atuais

```powershell
.venv/Scripts/python -m unittest discover -s tests -v
./scripts/modo_banco.ps1 -Modo ingestao
$env:TESTAR_NEO4J='1'
$env:TESTAR_CORPUS='1'
.venv/Scripts/python -m unittest discover -s tests -v
./scripts/modo_banco.ps1 -Modo consulta
```

Os testes de corpus exigem ingestão prévia dos seis documentos. Os testes unitários não precisam de modelos ou banco. As métricas de NER/RE publicadas são de desenvolvimento, sobre oito excertos usados para corrigir regras; não são resultado de teste independente. A extração de tabelas, a revisão humana das anotações, a avaliação reservada, o artigo e a defesa permanecem pendentes.

Em caso de falha, consulte `docker compose logs neo4j`, confirme os endpoints no `.env` e verifique se o servidor GGUF está ativo. `WriteOnReadOnlyAccessDatabase` durante ingestão indica que é necessário trocar o modo. O modelo local pode ser lento em máquinas com pouca memória disponível; timeouts e rejeições de consulta são falhas de execução, não respostas sem evidência.

O perfil padrão do Neo4j usa heap de 128–384 MB e page cache de 64 MB, ajustáveis no `.env`. O limite global de transação é 60 s; o Cypher gerado recebe limite de 15 s. O encoder é liberado após gerar o vetor da pergunta para reduzir a disputa de RAM com o LLM; a indexação em lotes mantém sua sessão. Esse perfil foi verificado no acervo atual e precisa ser reavaliado ao ampliar o corpus.

## Equipe

- Arysson André Oliveira da Luz.
- Caio Justino de Andrade.
- Luiz Henrique Monteiro dos Santos.
- Paulo Victor Oliveira de Barros Araújo.

O professor terá acesso ao repositório quando o grupo autorizar o convite.
