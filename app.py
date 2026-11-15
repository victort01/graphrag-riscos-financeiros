import json
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as componentes
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from riscos.respostas import responder
from riscos.visualizacao import pagina_grafo
from riscos.intencao import EMPRESAS, FiltrosIncompativeis

st.set_page_config(page_title="GraphRAG | Riscos financeiros", page_icon="◈", layout="wide")
st.title("Mapa de exposições financeiras")
st.caption("GraphRAG • Demonstrações financeiras de 2024 e 2025 • Unipê")
st.info("Consulte exposições e proteções declaradas por Suzano, Klabin e Irani. A cobertura atual é narrativa; tabelas e montantes ainda estão em validação.")
empresas = EMPRESAS
with st.form("pergunta"):
    pergunta = st.text_input("Sua pergunta", placeholder="Como a Irani conecta ACC a recebíveis de exportações?", max_chars=1500)
    col1, col2 = st.columns(2)
    escolhidas = col1.multiselect("Empresas", list(empresas), default=["Irani"])
    ano = col2.selectbox("Exercício", ["2025", "2024", "Comparar exercícios"])
    consultar = st.form_submit_button("Consultar documentos", type="primary")
if consultar:
    if not pergunta.strip():
        st.warning("Escreva uma pergunta para consultar.")
    else:
        with st.spinner("Buscando fontes, validando Cypher e percorrendo o grafo…"):
            try:
                st.session_state.resultado = responder(pergunta, [empresas[e] for e in escolhidas], "" if ano.startswith("Comparar") else ano+"-12-31")
            except FiltrosIncompativeis as erro:
                st.session_state.pop("resultado", None)
                st.warning(str(erro))
            except Exception as erro:
                st.session_state.pop("resultado", None)
                st.error("A consulta não foi concluída. Verifique se o Neo4j e o modelo local estão disponíveis.")
                with st.expander("Detalhes da falha"):
                    st.code(str(erro))
if "resultado" in st.session_state:
    resultado = st.session_state.resultado
    resposta = resultado["resposta"]
    st.subheader("Resposta documental")
    st.write("**Confiança documental: " + resposta["confianca"]["nivel"] + ".** " + resposta["confianca"]["motivo"])
    if resposta["possivel_conflito"]:
        st.warning("A seleção sinalizou possível divergência entre fontes. Confira as evidências.")
    if not resposta["afirmacoes"]:
        st.write("Não foi possível sustentar uma resposta com as fontes consultadas.")
    for afirmacao in resposta["afirmacoes"]:
        st.write(afirmacao["texto"] + " " + " ".join("["+f+"]" for f in afirmacao["fontes"] + afirmacao.get("caminhos", [])))
    abas = st.tabs(["Caminhos financeiros", "Fontes", "Rastreabilidade"])
    with abas[0]:
        componentes.html(pagina_grafo(resultado), height=620, scrolling=True)
    with abas[1]:
        citadas = {f for a in resposta["afirmacoes"] for f in a["fontes"]}
        for id_, fonte in resultado["contexto_enviado"]["fontes"].items():
            with st.expander(f"{id_} · {fonte['empresa']} · {fonte['periodo']} · p. {fonte['pagina_inicio']}" + (" · citada" if id_ in citadas else " · contexto")):
                st.write(fonte["texto"])
                st.link_button("Abrir documento oficial", fonte["url"]+"#page="+str(fonte["pagina_inicio"]))
                st.code(fonte["trecho_id"])
    with abas[2]:
        st.caption("O JSON de contexto abaixo corresponde à entrada enviada ao modelo de resposta. A busca pode recuperar fontes que não cabem nesse contexto.")
        st.json({"busca": resultado["recuperacao"]["rastreio"], "algoritmo": resultado["grafo"]["rastreio"], "validacao": resposta["validacao"]}, expanded=False)
        st.json(resultado["contexto_enviado"], expanded=False)
        st.download_button("Baixar execução auditável", json.dumps(resultado, ensure_ascii=False, indent=2), file_name="consulta-graphrag.json", mime="application/json")
