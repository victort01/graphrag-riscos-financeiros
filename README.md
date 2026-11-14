# GraphRAG de riscos financeiros

Projeto final de Tendências em Ciência da Computação do Centro Universitário de João Pessoa (Unipê).

O sistema investigará exposições cambiais, obrigações em moeda estrangeira e mecanismos de proteção declarados em documentos de companhias brasileiras.

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

## Equipe

- Arysson André Oliveira da Luz.
- Caio Justino de Andrade.
- Luiz Henrique Monteiro dos Santos.
- Paulo Victor Oliveira de Barros Araújo.

O professor terá acesso ao repositório quando o grupo autorizar o convite.
