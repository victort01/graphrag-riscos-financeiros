"""Embeddings multilíngues versionados para recuperar trechos financeiros."""
from functools import lru_cache
from .config import ROOT, ambiente

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REVISAO = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
ARQUIVO = "onnx/model_quint8_avx2.onnx"
IDENTIFICADOR = MODELO + "@" + REVISAO + ":quint8-avx2:mean:256"


@lru_cache(maxsize=1)
def carregar():
    import onnxruntime as ort
    from tokenizers import Tokenizer
    from huggingface_hub import hf_hub_download
    parametros = {"repo_id": MODELO, "revision": REVISAO, "local_files_only": True}
    tokenizer = Tokenizer.from_file(hf_hub_download(filename="tokenizer.json", **parametros))
    tokenizer.enable_truncation(max_length=256)
    tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
    caminho = ambiente().get("EMBEDDING_ONNX_PATH")
    if not caminho:
        local = ROOT / "data/models/minilm-quint8.onnx"
        caminho = str(local) if local.exists() else hf_hub_download(filename=ARQUIVO, **parametros)
    opcoes = ort.SessionOptions()
    opcoes.intra_op_num_threads = 4
    opcoes.inter_op_num_threads = 1
    return tokenizer, ort.InferenceSession(caminho, sess_options=opcoes, providers=["CPUExecutionProvider"])


def codificar(textos):
    import numpy as np
    if not textos:
        return []
    tokenizer, modelo = carregar()
    tokens = tokenizer.encode_batch(textos)
    entradas = {"input_ids": np.array([t.ids for t in tokens], dtype=np.int64),
                "attention_mask": np.array([t.attention_mask for t in tokens], dtype=np.int64),
                "token_type_ids": np.array([t.type_ids for t in tokens], dtype=np.int64)}
    entradas = {i.name: entradas[i.name] for i in modelo.get_inputs()}
    saida = modelo.run(None, entradas)[0]
    mascara = entradas["attention_mask"][..., None]
    media = (saida * mascara).sum(1) / np.maximum(mascara.sum(1), 1)
    return (media / np.maximum(np.linalg.norm(media, axis=1, keepdims=True), 1e-12)).tolist()
