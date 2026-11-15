"""Adquire pesos oficiais em revisões fixas e confere SHA-256 antes da publicação local."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def baixar(modelo, pasta):
    destino = pasta / modelo["destino"]
    if destino.exists():
        with destino.open("rb") as arquivo:
            verificado = hashlib.file_digest(arquivo, "sha256").hexdigest() == modelo["sha256"]
        if verificado:
            print("Cache verificado:", destino.name)
            return
    url = f"https://huggingface.co/{modelo['repositorio']}/resolve/{modelo['revisao']}/{modelo['arquivo']}?download=true"
    parcial = destino.with_suffix(destino.suffix + ".part")
    print("Baixando", destino.name, flush=True)
    with urlopen(url, timeout=120) as resposta, parcial.open("wb") as arquivo:
        while bloco := resposta.read(1024 * 1024):
            arquivo.write(bloco)
    with parcial.open("rb") as arquivo:
        hash_ = hashlib.file_digest(arquivo, "sha256").hexdigest()
    if hash_ != modelo["sha256"]:
        raise ValueError("Checksum divergente: " + destino.name)
    parcial.replace(destino)
    print("Checksum verificado:", destino.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["embedding", "llm", "todos"], default="todos")
    args = parser.parse_args()
    modelos = json.loads((ROOT / "data/modelos.json").read_text(encoding="utf-8"))
    pasta = ROOT / "data/models"
    pasta.mkdir(parents=True, exist_ok=True)
    for tipo in (["embedding", "llm"] if args.tipo == "todos" else [args.tipo]):
        baixar(modelos[tipo], pasta)
        if tipo == "embedding":
            from huggingface_hub import hf_hub_download
            hf_hub_download(repo_id=modelos[tipo]["repositorio"], revision=modelos[tipo]["revisao"], filename="tokenizer.json")
