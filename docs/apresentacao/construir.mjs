import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const ink = '#10243B', teal = '#087D83', paper = '#F7F7F2', muted = '#526273';
const names = ['Arysson André Oliveira da Luz','Caio Justino de Andrade','Luiz Henrique Monteiro dos Santos','Paulo Victor Oliveira de Barros Araújo'];

export async function construir(p) {
  p.slides.delete(p.slides.items.map(s => s.id));
  function text(s, str, x, y, w, h, size=28, color=ink, bold=false) {
    const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    t.text=str; t.text.style={fontFamily:'Arial',fontSize:size,color,bold}; return t;
  }
  function slide(title, speaker, source='') {
    const s=p.slides.add({width:1280,height:720}); s.background.fill=paper;
    text(s,'GRAPHRAG · EXPOSIÇÕES FINANCEIRAS',64,30,1070,26,18,teal,true);
    text(s,title,64,93,1152,112,46,ink,true);
    const n=p.slides.items.length;
    text(s,`${speaker}  ·  Versão de trabalho · 15/11/2026`,64,667,1040,25,17,muted);
    text(s,String(n).padStart(2,'0'),1154,663,70,30,20,muted);
    s.speakerNotes.text=`Apresentador: ${speaker}.\n${source}`; return s;
  }
  function line(s, title, body, y) {
    text(s,title,66,y,345,100,30,teal,true); text(s,body,430,y,775,100,27);
  }
  function table(s, values, y, heights, widths) {
    const t=s.tables.add({rows:values.length,columns:values[0].length,left:64,top:y,width:1152,height:heights.reduce((a,b)=>a+b,0),columnWidths:widths,values});
    t.borders.assign({fill:'#D5DED9',width:1,style:'solid'});
    for(let r=0;r<values.length;r++) {
      t.rows[r].height=heights[r];
      for(let c=0;c<values[r].length;c++) {
        const cell=t.getCell(r,c); cell.fill=r===0?ink:(r%2?'#FFFFFF':'#ECF1ED');
        cell.text.style={fontFamily:'Arial',fontSize:27,color:r===0?'#FFFFFF':ink,bold:r===0};
      }
    } return t;
  }
  function node(s,label,x,y,w=270) {
    const n=s.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:88},fill:'#E5F0EC',line:{fill:teal,width:2}});
    n.text=label; n.text.style={fontFamily:'Arial',fontSize:26,bold:true,color:ink,alignment:'center'};return n;
  }
  function edge(s,a,b,label,x,y,w=290) {
    s.shapes.connect(a,b,{kind:'straight',fromSide:'right',toSide:'left',line:{fill:teal,width:2},tail:{type:'arrow'}});
    text(s,label,x,y,w,40,21,teal,true);
  }

  let s=slide('','Arysson');
  for (const sh of [...s.shapes.items]) sh.delete();
  s.background.fill='#0B182A';
  const cover=await fs.readFile(path.join(dir,'assets/capa-abstrata.png'));
  s.images.add({dataUrl:'data:image/png;base64,'+cover.toString('base64'),alt:'Metáfora abstrata de documentos conectados; imagem ilustrativa',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
  text(s,'UNIPÊ · TENDÊNCIAS EM CIÊNCIA DA COMPUTAÇÃO',64,45,1080,34,20,'#9DE0D2',true);
  text(s,'Exposições financeiras\nem grafos',64,159,810,155,60,'#FFFFFF',true);
  text(s,'GraphRAG com fontes verificáveis\nSuzano · Klabin · Irani | 2024–2025',67,339,770,90,29,'#E0ECEF');
  text(s,names.join('\n'),67,478,840,118,21,'#FFFFFF');
  text(s,'Centro Universitário de João Pessoa · Versão para revisão',67,662,1080,29,19,'#C5D4DB');
  s.speakerNotes.text='Arysson · 30 s. Professor: Ricardo Roberto de Lima. Arte abstrata gerada via ImageGen, sem dados representados; procedência e prompt em assets/README.md. O deck registra o estágio de desenvolvimento; as avaliações independentes ainda não foram concluídas.';

  s=slide('Que evidência sustenta uma resposta financeira?','Arysson','Fontes: docs/fase-1-viabilidade.md; docs/fase-7-respostas.md.');
  text(s,'Uma resposta precisa preservar empresa, exercício,\nobjeto da declaração e página da fonte.',67,220,1125,100,37,ink,true);
  line(s,'Pergunta do projeto','Como combinar texto e relações financeiras para responder com evidências rastreáveis?',362);
  line(s,'Recorte','Exposições, obrigações e medidas de proteção nas notas narrativas de relatórios oficiais.',490);
  s.speakerNotes.append('\nDuração: 60 s. O protótipo não estima probabilidade de falência nem classifica empresas por risco. Estuda relações explicitadas nas fontes e como elas entram na resposta.');

  s=slide('Seis relatórios oficiais, dois exercícios','Arysson','Fontes: data/manifesto.json; data/qualidade-extracao.json; data/validacao-indexacao-completa.json. URLs dos PDFs e hashes completos no manifesto.');
  table(s,[['Empresa','2024 (páginas)','2025 (páginas)','Total'],['Suzano','184','181','365'],['Klabin','153','156','309'],['Irani','139','141','280'],['Acervo','476','478','954']],215,[62,62,62,62,62],[370,270,270,242]);
  text(s,'3.918 trechos narrativos indexados · 85 declarações extraídas',67,555,1135,52,29,teal,true);
  text(s,'Tabelas e imagens ainda exigem validação de unidade, coluna e escopo.',67,610,1135,38,25,muted);
  s.speakerNotes.append('\nDuração: 65 s. São relatórios completos coletados, mas a cobertura validada do sistema é narrativa. Irani é de embalagens; as três pertencem à mesma cadeia produtiva, não ao mesmo subsetor. Os totais não medem precisão da extração. Transição: Caio explica a transformação do texto em grafo.');

  s=slide('Do PDF à declaração com evidência','Caio','Fontes: src/riscos/ingestao.py; src/riscos/extracao.py; docs/fase-3-ingestao.md; docs/fase-4-identidades.md.');
  line(s,'1 · Coletar e segmentar','URL oficial, SHA-256, páginas e trechos com posição no texto.',220);
  line(s,'2 · Reconhecer e relacionar','Regras de domínio identificam menções e relações financeiras.',349);
  line(s,'3 · Publicar com origem','Entidade + declaração + trecho + documento, em transação no Neo4j.',478);
  s.speakerNotes.append('\nDuração: 70 s. NER/RE são automáticos e baseados em regras, com vocabulário financeiro explícito. A avaliação de oito excertos foi usada para desenvolvimento; seu resultado não vale como teste reservado. As regras preservam negação e condição quando reconhecidas.');

  s=slide('O grafo preserva relação e procedência','Caio','Diagrama conceitual editável do esquema implementado. Fonte: docs/fase-2-modelagem.md; src/riscos/esquema.py.');
  const a=node(s,'Empresa',65,272,240),b=node(s,'Obrigação financeira',505,272,300),c=node(s,'Moeda',1005,272,210);
  edge(s,a,b,'TEM_OBRIGACAO',311,231,280);edge(s,b,c,'DENOMINADO_EM',812,231,270);
  const d=node(s,'Declaração',65,490,240),e=node(s,'Trecho',505,490,300),f=node(s,'Documento',1005,490,210);
  edge(s,d,e,'EVIDENCIADA_POR',311,449,290);edge(s,e,f,'PERTENCE_A',832,449,220);
  text(s,'Cada aresta financeira identifica sua declaração de origem.',67,605,1135,44,27,teal,true);
  s.speakerNotes.append('\nDuração: 70 s. A fileira superior ilustra dois saltos financeiros. A inferior mostra a cadeia de evidência; as declarações também apontam para sujeito e objeto. Há labels, propriedades, constraints e índices Range, Fulltext e vetorial. O Range é o índice de propriedades usado na versão atual do Neo4j. O desenho explica a ontologia; não é captura de um resultado.');

  s=slide('Identidade, tempo e versão são regras de domínio','Caio','Fontes: src/riscos/identidades.py; src/riscos/versoes.py; tests/test_ingestao_versoes.py; data/validacao-migracao-versionamento.json.');
  line(s,'Canonicalização','CNPJ para empresas; conceitos globais para moeda e fator; obrigações vinculadas à companhia.',215);
  line(s,'Revisões documentais','Nova versão substitui a anterior de forma atômica, preservando o histórico.',349);
  line(s,'Escopo incerto','Sem qualificador reconhecido, a travessia fica restrita às declarações do mesmo trecho.',483);
  s.speakerNotes.append('\nDuração: 75 s. Unicidade de IDs não comprova resolução semântica. Revisões adicionais foram testadas com casos sintéticos; as seis fontes reais estão na versão 1. A ausência de escopo reconhecido pelo extrator não significa que o relatório omita o escopo. Transição: Paulo detalha recuperação e algoritmo.');

  s=slide('A busca combina três sinais','Paulo','Fontes: src/riscos/recuperacao.py; src/riscos/embeddings.py; docs/fase-5-recuperacao.md. Embeddings e LLM fixados em data/modelos.json.');
  line(s,'Semelhança semântica','MiniLM multilíngue · vetores de 384 dimensões · cosseno.',218);
  line(s,'Texto e Cypher','Fulltext e consulta gerada pelo LLM, com validação e filtros de empresa, período e vigência.',343);
  line(s,'Fusão de posições','RRF com constante 60; até 12 candidatos por sinal e oito trechos na seleção inicial.',482);
  s.speakerNotes.append('\nDuração: 90 s. RRF soma 1/(60+posição) por sinal; não soma diretamente scores de escalas diferentes. A busca vetorial e a textual usam os mesmos 3.918 trechos elegíveis. Cypher é gerado integralmente pelo modelo, validado por contrato de leitura, parâmetros, EXPLAIN e limites. O banco fica em modo de consulta. Há uma tentativa de reparo registrada; falhas aparecem no rastreio.');

  s=slide('O algoritmo modifica o contexto\nantes da resposta','Paulo','Fontes: src/riscos/caminhos.py; src/riscos/respostas.py; docs/fase-6-caminhos.md.');
  line(s,'Caminhos dirigidos','shortestPath em relações financeiras permitidas, com até quatro saltos.',218);
  line(s,'Restrições financeiras','Mesma empresa e exercício; controle de escopo, vigência e declarações que sustentam cada aresta.',343);
  line(s,'Contexto de 3.500 caracteres','Evidências dos caminhos entram antes da geração; prefixos redundantes são compactados.',480);
  s.speakerNotes.append('\nDuração: 90 s. Não é apenas desenhar o grafo após gerar o texto. O algoritmo escolhe caminhos e evidências que compõem o contexto enviado ao modelo. Caminhos de dois saltos estão verificados. Compartilhar o nó de um fator entre empresas permite observar um conceito comum, sem provar contágio, equivalência de exposição ou correlação.');

  s=slide('Demonstração: ACC e recebíveis da Irani','Paulo','Fonte: data/validacao-interface.json; docs/assets/interface-consulta-retomada.jpg. Execução local anterior à expansão do índice. PDF oficial: data/manifesto.json, irani-dfp-2025, página PDF 124.');
  text(s,'Pergunta',67,223,680,45,28,teal,true);
  text(s,'“Como a Irani conecta ACC a\nrecebíveis de exportações?”',67,280,680,120,37,ink,true);
  text(s,'A interface permite inspecionar a afirmação,\no caminho e a página usada como evidência.',67,435,680,95,28);
  text(s,'Resposta parcial · confiança limitada\nConsulta retomada após recarregar a página',67,566,680,68,25,muted);
  const shot=await fs.readFile(path.join(dir,'../assets/interface-consulta-retomada.jpg'));
  s.images.add({dataUrl:'data:image/jpeg;base64,'+shot.toString('base64'),alt:'Captura real da interface com resposta parcial e subgrafo após reconexão',fit:'contain',position:{left:841,top:169,width:330,height:468}});
  s.speakerNotes.append('\nDuração: 75 s. Para a defesa, usar também a aplicação ou o arquivo arquivado; esta captura é evidência de uma execução real, não uma interface ilustrada. A execução levou 335,269 segundos no computador local; não é benchmark controlado. A tolerância é à desconexão do navegador; reiniciar o servidor interrompe a tarefa.');

  s=slide('A seleção do contexto precisa cobrir as empresas','Paulo','Fonte: data/validacao-contexto-multiempresa.json. Estudo de desenvolvimento com o índice piloto de 553 passagens, mesmos candidatos e mesmas arestas; não compara métodos de RAG.');
  table(s,[['Caso de desenvolvimento','Antes','Depois'],['Empresas no contexto','2','3'],['Caracteres usados','3.444','3.391'],['Orçamento disponível','3.500','3.500']],219,[68,73,73,73],[650,250,252]);
  text(s,'Intercalar por empresa/exercício e remover prefixos repetidos\npreservou espaço para evidências das três companhias.',67,548,1130,85,29,teal,true);
  s.speakerNotes.append('\nDuração: 80 s. Este é um diagnóstico controlado de seleção de contexto. O conjunto de candidatos foi mantido na mesma ordem e as arestas foram preservadas. O achado levou a uma correção de implementação; não demonstra que GraphRAG responda melhor nem que reduza alucinações. A nova indexação exige nova medição. Transição: Luiz apresenta resposta e avaliação.');

  s=slide('Cada afirmação carrega suas referências','Luiz Henrique','Fontes: src/riscos/respostas.py; docs/fase-7-respostas.md.');
  line(s,'Evidências e caminhos','IDs citados devem existir; caminhos citados precisam levar às suas fontes reais.',219);
  line(s,'Guardas de resposta','Filtros de suporte numérico, negação, relevância e qualificação de escopo.',346);
  line(s,'Confiança descritiva','Sem suporte, limitada ou moderada; categorias de regras, sem probabilidade calibrada.',482);
  s.speakerNotes.append('\nDuração: 75 s. Guardas ajudam a detectar alguns erros; não verificam toda implicação semântica. Há respostas parciais e abstenção. O modelo bruto e o rastreio ficam arquivados para auditoria. Como tabelas ainda não estão validadas, o sistema não deve calcular risco líquido nem classificar empresas por valores.');

  s=slide('Avaliar recuperação e resposta separadamente','Luiz Henrique','Fontes: docs/fase-9-protocolo.md; scripts/avaliar_recuperacao.py; data/perguntas-smoke-recuperacao.json; docs/revisao-extracao.md.');
  table(s,[['Variante','O que entra na comparação'],['Vetorial','Mesmo corpus e mesmo orçamento de contexto'],['Híbrida','Vetor + Fulltext + Cypher gerado'],['Com grafo','Mesmos candidatos híbridos + caminhos']],219,[65,77,77,77],[340,812]);
  text(s,'Smoke (2 perguntas): evidência no contexto — 1/2 · 2/2 · 2/2.',67,553,1130,45,27,teal,true);
  text(s,'Teste reservado e revisão humana continuam necessários.',67,607,1130,38,26,muted);
  s.speakerNotes.append('\nDuração: 80 s. Smoke em data/avaliacao-recuperacao-smoke-completa-resumo.json: seis execuções sem falha. Vetor localizou a evidência esperada em uma de duas perguntas; híbrido e grafo, em duas. O grafo acrescentou um caminho em cada pergunta sem ganho de recall sobre o híbrido. Recall por documento, página e termo não mede correção de resposta. A avaliação final deve reservar perguntas antes de executar, conferir suporte por afirmação, abstenção, resolução de entidades e extração. Os dois revisores ainda não preencheram os formulários; nenhuma métrica humana foi inventada.');

  s=slide('O que está demonstrado e o que falta medir','Luiz Henrique','Fontes: docs/andamento.md; docs/matriz-requisitos.md; data/validacao-indexacao-completa.json; data/validacao-interface.json.');
  text(s,'Implementado e verificado localmente',67,220,1120,48,32,teal,true);
  text(s,'Neo4j · extração narrativa · busca híbrida · caminhos multi-hop\nVersionamento · fontes por afirmação · subgrafo interativo',67,292,1130,105,28);
  text(s,'Para concluir a avaliação científica',67,439,1120,48,32,teal,true);
  text(s,'Revisão independente · perguntas reservadas · tabelas e unidades\nComparação de respostas · mitigação de erros comprovada',67,514,1130,104,28);
  s.speakerNotes.append('\nDuração: 65 s. O trabalho já permite reproduzir componentes e inspecionar respostas reais. Não está demonstrada superioridade do GraphRAG nem mitigação geral de alucinação. A conclusão final dependerá dos resultados medidos, mesmo que sejam negativos. Repositório privado: https://github.com/victort01/graphrag-riscos-financeiros.');

  s=slide('Referências e materiais do projeto','Luiz Henrique','Edge et al. (2024): https://arxiv.org/abs/2404.16130. Liang et al. (2024): https://arxiv.org/abs/2409.13731. Fontes primárias dos seis PDFs, protocolos CVM e checksums: data/manifesto.json. Implementação e atribuições: README.md.');
  text(s,'Edge et al. (2024)\nFrom Local to Global: A Graph RAG Approach\nto Query-Focused Summarization',67,217,1130,110,28);
  text(s,'Liang et al. (2024)\nKAG: Boosting LLMs in Professional Domains\nvia Knowledge Augmented Generation',67,362,1130,110,28);
  text(s,'Fontes oficiais · manifesto · código · protocolo de avaliação\ngithub.com/victort01/graphrag-riscos-financeiros',67,534,1130,92,27,teal,true);
  s.speakerNotes.append('\nDuração: 25 s. A implementação usa grafo e recuperação com evidências; não reproduz o pipeline de comunidades do artigo GraphRAG nem o framework KAG completo. Regras financeiras e alinhamento de conceitos se inspiram nesses princípios. Acesso ao repositório depende de autorização do proprietário; convite ao professor foi adiado pelo grupo.');
  return {slides:p.slides.items.length,font:'Arial',size:[1280,720],status:'rascunho para revisao; avaliacao cientifica pendente'};
}
