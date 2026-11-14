"""Aquisição de PDFs públicos e extração por página para a validação do corpus."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def salvar_json(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporario.replace(caminho)


def adquirir(fonte, offline):
    destino = ROOT / "data/raw" / (fonte["id"] + ".pdf")
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        if offline:
            raise FileNotFoundError(f"Fonte ausente no cache: {fonte['id']}")
        requisicao = Request(fonte["url"], headers={"User-Agent": "PesquisaAcademicaGraphRAG/0.1"})
        with urlopen(requisicao, timeout=90) as resposta:
            conteudo = resposta.read(80 * 1024 * 1024 + 1)
        if len(conteudo) > 80 * 1024 * 1024:
            raise ValueError("Documento excede o limite de 80 MiB.")
        if not conteudo.startswith(b"%PDF"):
            raise ValueError(f"A fonte retornou conteúdo diferente de PDF: {fonte['id']}")
        temporario = destino.with_suffix(".download")
        temporario.write_bytes(conteudo)
        temporario.replace(destino)
    digest = hashlib.sha256(destino.read_bytes()).hexdigest()
    if fonte.get("sha256") and digest != fonte["sha256"]:
        raise ValueError(f"Checksum divergente: {fonte['id']}. Preserve e revise a nova versão.")
    return destino, digest


def extrair(fonte, offline):
    pdf, digest = adquirir(fonte, offline)
    leitor = PdfReader(pdf)
    if leitor.is_encrypted:
        raise ValueError(f"Documento cifrado exige revisão: {fonte['id']}")
    paginas = []
    for numero, pagina in enumerate(leitor.pages, 1):
        # A disposição preserva cabeçalhos e colunas para conferir escala e escopo.
        texto = pagina.extract_text(extraction_mode="layout") or ""
        paginas.append({"pagina_pdf": numero, "texto": texto})
    total = sum(len(p["texto"]) for p in paginas)
    if total == 0:
        raise ValueError(f"PDF sem texto extraível: {fonte['id']}")
    registro = {"documento_id": fonte["id"], "sha256": digest, "paginas": paginas,
                "extraido_em_utc": datetime.now(timezone.utc).isoformat()}
    salvar_json(ROOT / "data/processed" / (fonte["id"] + ".json"), registro)
    resumo = {"documento_id": fonte["id"], "sha256": digest, "bytes": pdf.stat().st_size,
              "paginas": len(paginas), "caracteres": total,
              "paginas_com_menos_de_100_caracteres": [p["pagina_pdf"] for p in paginas if len(p["texto"].strip()) < 100],
              "caracteres_substituidos": sum(p["texto"].count("\ufffd") for p in paginas),
              "avaliado_em_utc": registro["extraido_em_utc"]}
    salvar_json(ROOT / "data/reports" / (fonte["id"] + ".json"), resumo)
    return resumo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Usa somente os PDFs já baixados.")
    parser.add_argument("--id", action="append", help="Seleciona IDs do manifesto. Pode ser repetido.")
    args = parser.parse_args()
    manifesto = json.loads((ROOT / "data/manifesto.json").read_text(encoding="utf-8"))
    fontes = manifesto["documentos"]
    if args.id:
        desconhecidos = set(args.id) - {fonte["id"] for fonte in fontes}
        if desconhecidos:
            parser.error(f"IDs ausentes do manifesto: {sorted(desconhecidos)}")
        fontes = [fonte for fonte in fontes if fonte["id"] in args.id]
    for fonte in fontes:
        resumo = extrair(fonte, args.offline)
        print(f"{fonte['id']}: {resumo['paginas']} páginas, {resumo['caracteres']} caracteres", flush=True)


if __name__ == "__main__":
    main()

