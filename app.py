import json
import os
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as componentes
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from riscos.visualizacao import pagina_grafo, rastrear_nos
from riscos.intencao import EMPRESAS, FiltrosIncompativeis, reconciliar
from riscos.execucoes import carregar_ultima
from riscos.trabalhos import gerenciador, ConsultaEmAndamento, FORMATO_ID

st.set_page_config(page_title="GraphRAG | Riscos financeiros", page_icon="◈", layout="wide")
st.title("Mapa de exposições financeiras")
st.caption("GraphRAG • Demonstrações financeiras de 2024 e 2025 • Unipê")
st.info("Consulte exposições e proteções declaradas por Suzano, Klabin e Irani. A cobertura atual é narrativa; tabelas e montantes ainda estão em validação.")
empresas = EMPRESAS

# O identificador aleatório retoma a tarefa sem publicar uma lista global de consultas.
vinculo = st.query_params.get("consulta", "")
if vinculo and "trabalho_id" not in st.session_state and "resultado" not in st.session_state:
    if FORMATO_ID.fullmatch(vinculo):
        st.session_state.trabalho_id = vinculo
    else:
        st.warning("O link de consulta é inválido. Inicie uma nova consulta.")


def solicitar_consulta():
    st.session_state.enviar_consulta = True


with st.form("pergunta"):
    pergunta = st.text_input("Sua pergunta", placeholder="Como a Irani conecta ACC a recebíveis de exportações?", max_chars=1500)
    col1, col2 = st.columns(2)
    escolhidas = col1.multiselect("Empresas", list(empresas), default=["Irani"])
    ano = col2.selectbox("Exercício", ["2025", "2024", "Comparar exercícios"])
    st.form_submit_button("Consultar documentos", type="primary", on_click=solicitar_consulta)
# A conclusão da tarefa refaz a tela; o evento consumido evita um segundo envio.
if st.session_state.pop("enviar_consulta", False):
    if not pergunta.strip():
        st.session_state.pop("resultado", None)
        st.warning("Escreva uma pergunta para consultar.")
    else:
        try:
            filtros, periodo = reconciliar(pergunta, [empresas[e] for e in escolhidas], "" if ano.startswith("Comparar") else ano+"-12-31")
            st.session_state.trabalho_id = gerenciador().iniciar(pergunta, filtros, periodo)
            st.query_params["consulta"] = st.session_state.trabalho_id
            st.session_state.pop("resultado", None)
        except (FiltrosIncompativeis, ConsultaEmAndamento) as erro:
            st.session_state.pop("resultado", None)
            st.warning(str(erro))
        except (OSError, ValueError) as erro:
            st.error("Não foi possível iniciar a consulta: " + str(erro))
if os.getenv("PUBLIC_DEPLOYMENT") != "1":
    with st.expander("Execuções salvas neste computador"):
        st.caption("Reabre um resultado arquivado, sem executar uma nova consulta. A pergunta, a data e a versão originais são preservadas.")
        if st.button("Carregar última execução salva"):
            try:
                anterior = carregar_ultima()
                if anterior is None:
                    st.info("Ainda não há uma execução salva.")
                else:
                    st.session_state.resultado = anterior
            except (OSError, ValueError) as erro:
                st.error("Não foi possível ler a execução salva: " + str(erro))
        if st.button("Retomar última consulta"):
            ultima = gerenciador().ultima()
            if ultima:
                st.session_state.trabalho_id = ultima["id"]
                st.session_state.pop("resultado", None)
            else:
                st.info("Ainda não há uma consulta iniciada nesta interface.")


@st.fragment(run_every="2s")
def acompanhar_consulta():
    try:
        servico = gerenciador()
        estado = servico.consultar(st.session_state.trabalho_id)
        if estado["estado"] == "concluida":
            st.session_state.resultado = servico.carregar_resultado(estado)
            st.session_state.pop("trabalho_id", None)
            st.rerun()
        st.caption("Consulta em acompanhamento: " + estado["pergunta"])
        if estado["estado"] in {"falhou", "interrompida"}:
            st.error("A consulta não foi concluída. Verifique se o Neo4j e o modelo local estão disponíveis.")
            with st.expander("Detalhes da falha"):
                st.code(estado["erro"])
        else:
            st.info(estado["etapa"] + ". O processamento continua se esta página for desconectada.")
    except (OSError, ValueError, KeyError) as erro:
        st.error("A consulta não está mais disponível neste servidor. Inicie uma nova consulta.")


if "trabalho_id" in st.session_state:
    acompanhar_consulta()
if "resultado" in st.session_state:
    resultado = st.session_state.resultado
    resposta = resultado["resposta"]
    st.subheader("Resposta documental")
    st.caption("Pergunta desta execução: " + resultado["pergunta"] + " · " + resultado["data_utc"])
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
            versao = str(fonte.get("versao") or "não registrada")
            with st.expander(f"{id_} · {fonte['empresa']} · {fonte['periodo']} · v. {versao} · p. {fonte['pagina_inicio']}" + (" · citada" if id_ in citadas else " · contexto")):
                st.write(fonte["texto"])
                st.link_button("Abrir documento oficial", fonte["url"]+"#page="+str(fonte["pagina_inicio"]))
                st.code(fonte["trecho_id"])
    with abas[2]:
        st.caption("O JSON de contexto abaixo corresponde à entrada enviada ao modelo de resposta. A busca pode recuperar fontes que não cabem nesse contexto.")
        st.json({"versao": resultado.get("versao_execucao"), "data_utc": resultado["data_utc"], "modelo": resultado["modelo_resposta"]}, expanded=False)
        st.json(rastrear_nos(resultado), expanded=False)
        st.json({"busca": resultado["recuperacao"]["rastreio"], "algoritmo": resultado["grafo"]["rastreio"], "validacao": resposta["validacao"]}, expanded=False)
        st.json(resultado["contexto_enviado"], expanded=False)
        st.download_button("Baixar execução auditável", json.dumps(resultado, ensure_ascii=False, indent=2), file_name="consulta-graphrag.json", mime="application/json")
