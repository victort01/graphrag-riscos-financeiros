"""Trechos estáveis e localizáveis, preservando o texto de cada página."""
import re
from .identidade import chave_hash

VERSAO = "paragrafos-v5-colunas"


def regioes_de_leitura(texto):
    """Isola as colunas do quadro de assuntos de auditoria antes de formar frases."""
    cabecalho = re.search(r"(?m)^[^\n]*?Como o assunto foi conduzido", texto)
    if not cabecalho or not re.search(r"Porque [ée] um PAA", texto):
        return [(texto, None, "pagina")]
    referencia = cabecalho.group().index("Como o assunto foi conduzido")
    inicios = [m.end()-1 for linha in texto.splitlines() for m in re.finditer(r" {4,}\S", linha)
               if referencia-8 <= m.end()-1 <= referencia+8]
    corte = min(inicios, default=referencia)
    if corte < 20:
        return [(texto, None, "pagina")]
    regioes = []
    for coluna, (inicio, fim) in enumerate(((0, corte), (corte, None)), 1):
        linhas, mapa, posicao, origem = [], [], 0, 0
        for linha in texto.splitlines(keepends=True):
            parte = linha.rstrip("\r\n")[inicio:fim]
            linhas.append(parte + "\n")
            mapa.append((posicao, posicao + len(parte), origem + inicio))
            posicao += len(parte) + 1
            origem += len(linha)
        regioes.append(("".join(linhas), mapa, f"coluna_{coluna}"))
    return regioes


def origens_bloco(pagina, inicio, fim, mapa):
    if mapa is None:
        return [{"pagina": pagina, "inicio": inicio, "fim": fim}]
    return [{"pagina": pagina, "inicio": original + max(inicio-a, 0),
             "fim": original + min(fim-a, b-a)}
            for a, b, original in mapa if a < fim and b > inicio]


def segmentar(documento):
    partes = []
    for pagina in documento["paginas"]:
        texto = pagina["texto"]
        for regiao, mapa, coluna in regioes_de_leitura(texto):
            for match in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", regiao):
                original = match.group()
                limpo = " ".join(original.split())
                if len(limpo) < 2 or limpo.isdecimal() or re.match(r"^(?:Notas explicativas|KLBN[0-9]|Suzano S\.A\.)", limpo):
                    continue
                linhas_numericas = sum(len(re.findall(r"\d[\d.,]*", l)) >= 3 for l in original.splitlines())
                natureza = "tabela" if linhas_numericas >= 3 else "narrativa"
                origens = origens_bloco(pagina["pagina_pdf"], match.start(), match.end(), mapa)
                # Uma frase pode continuar após uma quebra de bloco ou de página no PDF.
                if partes and coluna == partes[-1]["regiao"] and natureza == partes[-1]["natureza"] == "narrativa" and not re.search(r"[.!?:;]$", partes[-1]["texto"]):
                    anterior = partes[-1]
                    if pagina["pagina_pdf"] - anterior["origens"][-1]["pagina"] <= 1 and len(anterior["texto"]) + len(limpo) < 2400:
                        anterior["texto"] += " " + limpo
                        anterior["original"] += "\n\n" + original
                        anterior["origens"].extend(origens)
                        continue
                partes.append({"texto": limpo, "original": original, "origens": origens, "natureza": natureza, "regiao": coluna})
    trechos = []
    for parte in partes:
        limpo = parte["texto"]
        if len(limpo) < 70:
            continue
        for inicio in range(0, len(limpo), 2400):
            primeira, ultima = parte["origens"][0], parte["origens"][-1]
            trechos.append({
                "id": "trecho:" + chave_hash(documento["documento_id"], documento["sha256"], primeira, ultima, inicio, VERSAO),
                "texto": limpo[inicio:inicio+2400], "texto_original": parte["original"],
                "documento_id": documento["documento_id"], "sha256": documento["sha256"],
                "pagina_inicio": primeira["pagina"], "pagina_fim": ultima["pagina"],
                "inicio_original": primeira["inicio"], "fim_original": ultima["fim"],
                "origens": parte["origens"], "segmentacao": VERSAO, "natureza": parte["natureza"],
                "recorte": inicio > 0 or len(limpo) > 2400,
            })
    return trechos
