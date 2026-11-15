# Apresentação para revisão

- `apresentacao-revisao.pptx`: 14 slides, textos, tabelas e diagrama editáveis, com notas e referências.
- `apresentacao-revisao.pdf`: cópia de exibição dos previews revisados. O PDF é rasterizado; a edição é feita no PowerPoint ou na apresentação vinculada.
- `falas.md`: roteiro dos quatro integrantes, transições, demonstração e preparação para perguntas. Paulo ficou com a parte técnica mais complexa.

Este material registra o desenvolvimento em 15/11/2026. Não é a defesa final: a revisão independente, o teste reservado e a validação ampliada dos dados ainda precisam ser concluídos. O caso de comparação entre três empresas e a captura da interface são históricos, anteriores à expansão do índice. O smoke usa o índice completo e duas perguntas já conhecidas de desenvolvimento.

## Reprodução dos materiais

`construir.mjs` exporta `construir(presentation)` para o runtime oficial `@oai/artifact-tool`. A apresentação vinculada foi criada e revisada em Artifact Session, com Arial disponível no runtime e canvas 1280 × 720. Identificador: `artifact_E0SKeXL6yymUf5Hp0UGmTUUgyJVTDx08`.

Para uma atualização, importar o módulo e executar `construir` dentro da transação da sessão, revisar os slides e solicitar exportação `pptx` ao host. Copiar a saída para `.build/candidate.pptx` e executar `validar-exportacao.mjs` com a raiz do runtime, o diretório da skill de apresentações e a raiz do repositório. A validação não sobrescreve o arquivo final: usar um novo nome para uma revisão posterior.

`exportar_pdf.py` usa ReportLab e os 14 previews finais `.build/slides/slide-NN.png`, em ordem. A exportação PDF direta da biblioteca falhou no ambiente, então esta cópia mantém a aparência dos previews. As notas completas e as referências permanecem no PPTX. Os arquivos em `.build/` e os recibos de validação em `data/reports/` são intermediários locais ignorados pelo Git.

O PowerPoint passou nas verificações de pacote, geometria, fontes declaradas e reimportação. Os 14 slides foram renderizados e inspecionados. Isso não equivale a testar a apresentação em uma instalação do Microsoft PowerPoint ou Google Slides.

Os ativos e suas origens estão em `assets/README.md`.
