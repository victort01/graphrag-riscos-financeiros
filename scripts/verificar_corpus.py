"""Confere a integridade do acervo e os localizadores da leitura exploratória."""
import hashlib
import json

from validar_fontes import ROOT


def ler(relativo):
    return json.loads((ROOT / relativo).read_text(encoding="utf-8"))


def verificar():
    fontes = ler("data/manifesto.json")["documentos"]
    evidencias = ler("data/evidencias-exploratorias.json")
    perguntas = ler("data/perguntas-exploratorias.json")
    documentos = {}
    hashes = set()
    for fonte in fontes:
        pdf = ROOT / "data/raw" / (fonte["id"] + ".pdf")
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest != fonte["sha256"] or digest in hashes:
            raise ValueError(f"Checksum divergente ou documento duplicado: {fonte['id']}")
        hashes.add(digest)
        texto = ler("data/processed/" + fonte["id"] + ".json")
        if texto["sha256"] != digest:
            raise ValueError(f"Extração de outra versão: {fonte['id']}")
        if [p["pagina_pdf"] for p in texto["paginas"]] != list(range(1, len(texto["paginas"]) + 1)):
            raise ValueError(f"Paginação inconsistente: {fonte['id']}")
        documentos[fonte["id"]] = texto
    mapa_evidencias = {e["id"]: e for e in evidencias}
    if len(mapa_evidencias) != len(evidencias):
        raise ValueError("Identificadores de evidência duplicados.")
    for evidencia in evidencias:
        paginas = documentos[evidencia["documento_id"]]["paginas"]
        texto = " ".join(paginas[evidencia["pagina_pdf"] - 1]["texto"].split()).casefold()
        if evidencia["termo_de_conferencia"].casefold() not in texto:
            raise ValueError(f"Localizador exploratório não confere: {evidencia['id']}")
    cruzamentos = 0
    for pergunta in perguntas:
        usados = {mapa_evidencias[i]["documento_id"] for i in pergunta["evidencias"]}
        cruzamentos += len(usados) > 1
    if len(perguntas) < 8 or cruzamentos < 4:
        raise ValueError("A amostra ainda não satisfaz as metas de perguntas exploratórias.")
    return {"documentos": len(fontes), "empresas": len({f["empresa_id"] for f in fontes}),
            "paginas": sum(len(d["paginas"]) for d in documentos.values()),
            "evidencias_localizadas": len(evidencias), "perguntas": len(perguntas),
            "perguntas_entre_documentos": cruzamentos,
            "escopo": "Integridade e localizadores; respostas exploratórias requerem revisão humana."}


if __name__ == "__main__":
    print(json.dumps(verificar(), ensure_ascii=False, indent=2))

