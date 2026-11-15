# Fontes e ferramentas

Os relatórios de Suzano, Klabin e Irani são obtidos nos endereços oficiais catalogados em data/manifesto.json. Os documentos e extrações integrais ficam no cache local e não são redistribuídos pelo Git. Identidades cadastrais e protocolos de entrega são conferidos nas fontes da CVM registradas no catálogo.

| Componente | Uso e referência |
|---|---|
| Neo4j Community 5.26.0 | Banco LPG, índices, consultas e caminhos; imagem oficial neo4j. |
| pypdf 6.21.4 | Extração de texto dos PDFs, preservando página. |
| ONNX Runtime, NumPy, tokenizers, huggingface_hub | Inferência local de embeddings e aquisição de arquivos versionados. |
| Multilingual MiniLM | Modelo de embeddings; licença, revisão e checksum em data/modelos.json. |
| Qwen2.5 | Modelo local de instrução; variantes e licenças em data/modelos.json. |
| llama.cpp b7770 | Servidor local de inferência GGUF, licença MIT. |
| Streamlit 1.44.1 | Interface de consulta, licença Apache-2.0. |
| Cytoscape.js 3.31.2 | Renderização interativa; arquivo distribuído com licença MIT em ui/vendor/. |

O desenvolvimento foi assistido por Codex, incluindo propostas de arquitetura, código, testes e documentação. O grupo deverá revisar, compreender e validar esses artefatos antes de atribuir contribuições individuais e apresentar o trabalho. Os resultados automatizados não substituem revisão humana das evidências financeiras nem avaliação independente.
