# Artigo para revisão

`artigo-revisao.tex` é a fonte editável e `artigo-revisao.pdf` é o rascunho compilado. O artigo usa a classe IEEEtran 1.8b no modo `conference`, em duas colunas, com quatro páginas. Está em português e descreve os resultados de desenvolvimento disponíveis em 15/11/2026. Não é uma submissão nem um artigo final com revisão independente.

O texto diferencia dados coletados de cobertura validada, resultados de recuperação de suporte semântico e operação local de avaliação científica. A segunda rodada de geração usa IDs restritos ao contexto. As rodadas anteriores permanecem registradas. A ausência de um erro de referência não demonstra que uma afirmação esteja correta.

## Compilar

No Windows, executar `./docs/artigo/compilar.ps1` a partir da raiz. O script adquire o Tectonic 0.17.0 oficial para Windows somente quando necessário, verifica o SHA-256 publicado no release e compila para `.build/`. A primeira compilação também baixa pacotes TeX pelo mecanismo do Tectonic. Binários e caches não são versionados. Para outro compilador Tectonic existente, usar `-Compilador caminho`.

Com uma distribuição LaTeX compatível, também é possível compilar a fonte com a classe local e os pacotes declarados. Essa alternativa não foi testada neste computador. A revisão final foi compilada com Tectonic, renderizada com Poppler e inspecionada por página. Logs de compilação e previews ficam em `.build/`, fora do Git. O PDF do artigo contém texto selecionável.

## Origem do formato e licenças

- Orientação de formatos da IEEE: https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/
- Pacote IEEEtran: https://ctan.org/pkg/ieeetran
- Classe original, sem modificações: https://ctan.math.illinois.edu/macros/latex/contrib/IEEEtran/IEEEtran.cls
- SHA-256 da classe: `da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7`.
- Licença da classe: LPPL 1.3, autoria e avisos preservados no arquivo. Esta classe é uma dependência de formatação, não código escrito pelo grupo.
- Tectonic 0.17.0: https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0
- SHA-256 do ZIP Windows MSVC: `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`.

## Antes da entrega final

Concluir as revisões, preparar e congelar o conjunto reservado, executar os métodos e incorporar a análise dos resultados. Atualizar os totais e as limitações se o corpus ou o pipeline mudar. Conferir as referências com os autores e validar que todos compreendem as escolhas metodológicas. O enunciado aceita SBC ou IEEE; o formato escolhido aqui é IEEE conference, sem pressupor publicação ou aprovação da IEEE.
