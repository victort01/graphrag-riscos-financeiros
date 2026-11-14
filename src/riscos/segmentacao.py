"""Trechos estáveis e localizáveis, preservando o texto de cada página."""
import re
from .identidade import chave_hash

VERSAO = "paragrafos-v3"


def segmentar(documento):
    partes = []
    for pagina in documento["paginas"]:
        texto = pagina["texto"]
        for match in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", texto):
            original = match.group()
            limpo = " ".join(original.split())
            if len(limpo) < 2 or limpo.isdecimal() or re.match(r"^(?:Notas explicativas|KLBN[0-9]|Suzano S\.A\.)", limpo):
                continue
            linhas_numericas = sum(len(re.findall(r"\d[\d.,]*", l)) >= 3 for l in original.splitlines())
            natureza = "tabela" if linhas_numericas >= 3 else "narrativa"
            origem = {"pagina": pagina["pagina_pdf"], "inicio": match.start(), "fim": match.end()}
            # Uma frase pode continuar após uma quebra de bloco ou de página no PDF.
            if partes and natureza == partes[-1]["natureza"] == "narrativa" and not re.search(r"[.!?:;]$", partes[-1]["texto"]):
                anterior = partes[-1]
                if pagina["pagina_pdf"] - anterior["origens"][-1]["pagina"] <= 1 and len(anterior["texto"]) + len(limpo) < 2400:
                    anterior["texto"] += " " + limpo
                    anterior["original"] += "\n\n" + original
                    anterior["origens"].append(origem)
                    continue
            partes.append({"texto": limpo, "original": original, "origens": [origem], "natureza": natureza})
    trechos = []
    for parte in partes:
        limpo = parte["texto"]
        if len(limpo) < 70:
            continue
        for inicio in range(0, len(limpo), 2400):
            primeira, ultima = parte["origens"][0], parte["origens"][-1]
            trechos.append({
                "id": "trecho:" + chave_hash(documento["sha256"], primeira, ultima, inicio, VERSAO),
                "texto": limpo[inicio:inicio+2400], "texto_original": parte["original"],
                "documento_id": documento["documento_id"], "sha256": documento["sha256"],
                "pagina_inicio": primeira["pagina"], "pagina_fim": ultima["pagina"],
                "inicio_original": primeira["inicio"], "fim_original": ultima["fim"],
                "origens": parte["origens"], "segmentacao": VERSAO, "natureza": parte["natureza"],
                "recorte": inicio > 0 or len(limpo) > 2400,
            })
    return trechos
