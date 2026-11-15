"""Entrada do Community Cloud; o aplicativo principal continua executável localmente."""
import os
import runpy
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from riscos.runtime_nuvem import iniciar, pronto

os.environ["PUBLIC_DEPLOYMENT"] = "1"


@st.cache_resource
def preparar():
    executor = ThreadPoolExecutor(max_workers=1)
    return executor, executor.submit(iniciar)


if pronto():
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
else:
    st.set_page_config(page_title="GraphRAG | Riscos financeiros", layout="wide")
    st.title("Mapa de exposições financeiras")

    @st.fragment(run_every="2s")
    def acompanhar():
        _, tarefa = preparar()
        if not tarefa.done():
            st.info("Preparando os modelos para consulta. A primeira abertura pode levar alguns minutos.")
        elif tarefa.exception():
            st.error("Não foi possível preparar a aplicação. O responsável deve conferir os registros da implantação.")
        else:
            st.rerun()

    acompanhar()
