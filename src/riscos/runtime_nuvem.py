"""Inicialização única dos modelos em um host Linux com disco efêmero."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import time
from urllib.request import urlopen

from .config import ROOT, ambiente


def pronto():
    try:
        with urlopen("http://127.0.0.1:18081/health", timeout=2) as resposta:
            return json.load(resposta).get("status") == "ok"
    except (OSError, ValueError):
        return False


def iniciar():
    if pronto():
        return
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        raise RuntimeError("O runtime de nuvem requer Linux x86-64.")
    config = ambiente()
    url = config.get("LLAMA_RUNTIME_URL", "")
    esperado = config.get("LLAMA_RUNTIME_SHA256", "")
    if not url.startswith("https://github.com/victort01/graphrag-riscos-financeiros/releases/download/") or not re.fullmatch(r"[a-f0-9]{64}", esperado):
        raise ValueError("Configure o runtime publicado e seu SHA-256 antes de iniciar a aplicação.")
    pasta = ROOT / "data/models/llama-linux"
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / "runtime.tar.gz"
    with urlopen(url, timeout=120) as origem, arquivo.open("wb") as destino:
        while bloco := origem.read(1024 * 1024):
            destino.write(bloco)
    with arquivo.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != esperado:
            raise ValueError("Checksum do runtime divergente.")
    servidor = pasta / "llama-server"
    with tarfile.open(arquivo) as tar:
        membro = tar.getmember("llama-server")
        if not membro.isfile():
            raise ValueError("O runtime não contém o executável esperado.")
        # Ler um único membro evita materializar caminhos ou links do pacote.
        with tar.extractfile(membro) as origem, servidor.open("wb") as destino:
            while bloco := origem.read(1024 * 1024):
                destino.write(bloco)
    servidor.chmod(0o700)
    subprocess.run([sys.executable, str(ROOT / "scripts/baixar_modelos.py")], cwd=ROOT, check=True)
    os.environ["LLM_URL"] = "http://127.0.0.1:18081/v1/chat/completions"
    logs = ROOT / "data/reports"
    logs.mkdir(parents=True, exist_ok=True)
    with (logs / "modelo-nuvem.log").open("ab") as log:
        processo = subprocess.Popen([
            str(servidor), "--model", str(ROOT / "data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            "--alias", "qwen-riscos-local", "--host", "127.0.0.1", "--port", "18081",
            "--ctx-size", "4096", "--threads", "2", "--parallel", "1", "--batch-size", "128"],
            stdout=log, stderr=log)
    for _ in range(120):
        if pronto():
            return
        if processo.poll() is not None:
            raise RuntimeError("O servidor do modelo encerrou durante a inicialização.")
        time.sleep(1)
    processo.terminate()
    raise TimeoutError("O servidor do modelo não ficou pronto em 120 segundos.")
