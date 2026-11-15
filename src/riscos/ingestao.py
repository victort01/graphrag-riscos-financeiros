"""Pipeline de documento com artefatos locais e publicação transacional."""
import json
from collections import defaultdict
from pathlib import Path

from .banco import Banco
from .config import ROOT
from .esquema import RELACOES, ROTULOS
from .extracao import VERSAO, extrair
from .identidade import VERSAO as IDENTIDADES
from .segmentacao import VERSAO as SEGMENTACAO, segmentar
from .versoes import VERSAO as VERSIONAMENTO, metadados, hash_fonte, validar_publicacao
from .embeddings import IDENTIFICADOR

PIPELINE = VERSAO + "/" + SEGMENTACAO + "/" + IDENTIDADES + "/" + VERSIONAMENTO


def validar_dados(dados):
    if any(t["documento_id"] != dados["fonte"]["id"] or t["sha256"] != dados["fonte"]["sha256"] for t in dados["trechos"]):
        raise ValueError("Um trecho pertence a outro documento ou checksum.")
    entidades = {e["id"]: e for e in dados["entidades"]}
    trechos = {t["id"]: t for t in dados["trechos"]}
    if len(entidades) != len(dados["entidades"]) or len(trechos) != len(dados["trechos"]):
        raise ValueError("Identidades duplicadas no documento preparado.")
    for declaracao in dados["declaracoes"]:
        sujeito = entidades[declaracao["sujeito_id"]]
        objeto = entidades[declaracao["objeto_id"]]
        trecho = trechos[declaracao["trecho_id"]]
        tipos_origem, tipos_destino = RELACOES[declaracao["predicado"]]
        if sujeito.get("revisao_identidade") or objeto.get("revisao_identidade"):
            raise ValueError("Uma relação usa entidade ambígua que exige qualificação.")
        if sujeito["tipo"] not in tipos_origem or objeto["tipo"] not in tipos_destino:
            raise ValueError("Relação incompatível com o esquema.")
        if declaracao["evidencia"] not in trecho["texto"] or trecho["natureza"] != "narrativa":
            raise ValueError("A evidência da declaração não está em um trecho narrativo válido.")
        if declaracao["documento_id"] != dados["fonte"]["id"]:
            raise ValueError("Declaração de outra fonte.")


def preparar(fonte):
    metadados(fonte)
    path = ROOT / "data/processed" / (fonte["id"] + ".json")
    documento = json.loads(path.read_text(encoding="utf-8"))
    if documento["documento_id"] != fonte["id"]:
        raise ValueError("A extração pertence a outro registro documental.")
    if documento["sha256"] != fonte["sha256"]:
        raise ValueError("A extração e o manifesto se referem a PDFs diferentes.")
    trechos = segmentar(documento)
    entidades, declaracoes = {}, []
    for trecho in trechos:
        encontrados, mencoes, relacoes = extrair(trecho, fonte)
        trecho["mencoes"] = mencoes
        for entidade in encontrados:
            entidades.setdefault(entidade["id"], entidade)
            aliases = entidades[entidade["id"]]["aliases"]
            aliases.extend(a for a in entidade["aliases"] if a not in aliases)
        declaracoes.extend(relacoes)
    declaracoes_unicas = {d["id"]: d for d in declaracoes}
    dados = {"fonte": fonte, "pipeline": PIPELINE, "trechos": trechos,
             "entidades": list(entidades.values()), "declaracoes": list(declaracoes_unicas.values())}
    validar_dados(dados)
    return dados


def publicar(banco, dados):
    validar_dados(dados)
    fonte = dados["fonte"]
    meta = metadados(fonte)
    existentes = banco.consultar("""MATCH (d:Documento)-[:REFERE_SE_A]->(e:Empresa)
        WHERE e.id=$empresa AND d.data_referencia=$periodo AND coalesce(d.tipo,$tipo)=$tipo
        RETURN d.id AS id,d.sha256 AS sha,d.versao AS versao,
        coalesce(d.vigente,true) AS vigente,d.substitui AS substitui,d.chave_versao AS chave_versao""",
        {"empresa": meta["empresa_id"], "periodo": fonte["data_referencia"], "tipo": fonte["tipo"]})
    ids = banco.consultar("MATCH (d:Documento {id:$id}) RETURN d.id AS id", {"id": fonte["id"]})
    if ids and fonte["id"] not in {d["id"] for d in existentes}:
        raise ValueError("O ID do documento já pertence a outra série documental.")
    validar_publicacao(fonte, existentes)
    grupos_entidades = defaultdict(list)
    for entidade in dados["entidades"]:
        if entidade["tipo"] not in ROTULOS:
            raise ValueError("Tipo de entidade fora do esquema.")
        props = {k: v for k, v in entidade.items() if k != "tipo"}
        props["aliases_texto"] = " ".join(entidade["aliases"])
        grupos_entidades[entidade["tipo"]].append(props)
    grupos_relacoes = defaultdict(list)
    for declaracao in dados["declaracoes"]:
        if declaracao["predicado"] not in RELACOES:
            raise ValueError("Tipo de relação fora do esquema.")
        grupos_relacoes[declaracao["predicado"]].append(declaracao)
    empresa_id = meta["empresa_id"]
    docprops = {k: fonte[k] for k in ("id", "sha256", "url", "empresa", "data_referencia", "exercicio_principal")}
    docprops.update(pipeline=dados["pipeline"], estado_narrativo="concluido", estado_tabular="pendente",
                    fonte_hash=hash_fonte(fonte), data_recebimento_cvm=fonte.get("data_recebimento_cvm"), **meta)
    # A escrita no documento adquire o lock antes de substituir seus fatos.
    legado = any(d["id"] == fonte["id"] and not d["chave_versao"] for d in existentes)
    identidade = "id:$id,sha256:$sha" + ("" if legado else ",chave_versao:$chave")
    comandos = [("MERGE (d:Documento {" + identidade + "}) SET d.ultima_carga=datetime()",
                 {"id": fonte["id"], "sha": fonte["sha256"], "chave": meta["chave_versao"]})]
    if meta["substitui"]:
        # Retirar a chave única e atribuí-la à nova versão na mesma transação
        # impede duas versões vigentes mesmo sob publicações concorrentes.
        comandos += [("""MATCH (d:Documento {id:$id}),(a:Documento {id:$anterior})
            SET a.vigente=false,a.chave_vigente=null MERGE (d)-[:SUBSTITUI]->(a)""",
            {"id": fonte["id"], "anterior": meta["substitui"]}),
            ("MATCH ()-[r]->() WHERE r.documento_id=$id SET r.vigente=false", {"id": meta["substitui"]})]
    comandos += [("MATCH ()-[r]->() WHERE r.documento_id=$id DELETE r", {"id": fonte["id"]}),
                ("MATCH (d:Declaracao {documento_id:$id}) DETACH DELETE d", {"id": fonte["id"]}),
                ("MATCH (t:Trecho {documento_id:$id}) WHERE NOT t.id IN $ids DETACH DELETE t",
                 {"id": fonte["id"], "ids": [t["id"] for t in dados["trechos"]]})]
    for tipo, entidades in grupos_entidades.items():
        comandos.append((f"""UNWIND $linhas AS row MERGE (n:Entidade:{tipo} {{id:row.id}})
                         WITH n,row,coalesce(n.aliases,[]) AS anteriores SET n += row
                         SET n.aliases=reduce(a=anteriores,novo IN row.aliases |
                           CASE WHEN novo IN a THEN a ELSE a + [novo] END)
                         SET n.aliases_texto=reduce(texto='',alias IN n.aliases | texto+' '+alias)""",
                         {"linhas": entidades}))
    comandos.append(("MATCH (e:Empresa {id:$empresa}) MATCH (d:Documento {id:$id}) "
                     "SET d += $props SET d.vigente=NOT EXISTS { MATCH (:Documento)-[:SUBSTITUI]->(d) } "
                     "SET d.chave_vigente=CASE WHEN d.vigente THEN $serie ELSE null END "
                     "MERGE (d)-[:REFERE_SE_A]->(e)",
                     {"empresa": empresa_id, "id": fonte["id"], "props": docprops, "serie": meta["chave_serie"]}))
    trechos = [{k: t[k] for k in ("id", "texto", "documento_id", "sha256", "pagina_inicio", "pagina_fim",
                                  "inicio_original", "fim_original", "segmentacao", "natureza", "recorte")}
               for t in dados["trechos"]]
    vetores = banco.consultar("""MATCH (t:Trecho)-[:PERTENCE_A]->(d:Documento)
        WHERE d.id IN $ids AND d.empresa=$empresa AND d.data_referencia=$periodo
        AND t.embedding IS NOT NULL AND t.modelo_embedding=$modelo
        RETURN t.sha256 AS sha256,t.texto AS texto,t.pagina_inicio AS pagina_inicio,t.pagina_fim AS pagina_fim,
        t.inicio_original AS inicio_original,t.fim_original AS fim_original,
        t.embedding AS embedding,t.modelo_embedding AS modelo_embedding""",
        {"ids": [fonte["id"], meta["substitui"]], "empresa": fonte["empresa"], "periodo": fonte["data_referencia"], "modelo": IDENTIFICADOR})
    campos = ("sha256", "texto", "pagina_inicio", "pagina_fim", "inicio_original", "fim_original")
    por_conteudo = {tuple(t[c] for c in campos): t for t in vetores}
    preservados = 0
    for trecho in trechos:
        anterior = por_conteudo.get(tuple(trecho[c] for c in campos))
        trecho.update(embedding=anterior["embedding"] if anterior else None,
                      modelo_embedding=anterior["modelo_embedding"] if anterior else None)
        preservados += anterior is not None
    comandos.append(("UNWIND $linhas AS row MATCH (d:Documento {id:row.documento_id}) "
                     "MERGE (t:Trecho {id:row.id}) SET t += row MERGE (t)-[:PERTENCE_A]->(d)", {"linhas": trechos}))
    comandos.append(("""UNWIND $linhas AS row MATCH (e:Empresa {id:$empresa}),
        (s:Entidade {id:row.sujeito_id}), (o:Entidade {id:row.objeto_id}), (t:Trecho {id:row.trecho_id})
        MERGE (d:Declaracao {id:row.id}) SET d = row
        MERGE (e)-[:TEM_DECLARACAO]->(d) MERGE (d)-[:SUJEITO]->(s) MERGE (d)-[:OBJETO]->(o)
        MERGE (d)-[:EVIDENCIADA_POR]->(t) MERGE (p:Periodo {id:row.periodo})
        MERGE (d)-[:NO_PERIODO]->(p)""", {"linhas": dados["declaracoes"], "empresa": empresa_id}))
    for tipo, relacoes in grupos_relacoes.items():
        comandos.append((f"""UNWIND $linhas AS row MATCH (s:Entidade {{id:row.sujeito_id}}),
            (o:Entidade {{id:row.objeto_id}}),(doc:Documento {{id:row.documento_id}})
            MERGE (s)-[r:{tipo} {{declaracao_id:row.id}}]->(o)
            SET r.documento_id=row.documento_id,r.periodo=row.periodo,r.empresa_id=row.empresa_id,r.vigente=doc.vigente,
                r.natureza=row.natureza,r.condicoes=row.condicoes,r.polaridade=row.polaridade""",
                         {"linhas": relacoes}))
    banco.transacao(comandos)
    return {"embeddings_preservados": preservados}


def executar(fonte, reprocessar=False, somente_preparar=False):
    banco = None if somente_preparar else Banco()
    if banco:
        existentes = banco.consultar("MATCH (d:Documento {id:$id}) RETURN d.pipeline AS pipeline, "
                                     "d.sha256 AS sha,d.estado_narrativo AS estado,d.fonte_hash AS fonte_hash", {"id": fonte["id"]})
        if existentes and existentes[0]["sha"] != fonte["sha256"]:
            raise ValueError("Manifesto diverge da versão já publicada no grafo.")
        if existentes and existentes[0]["pipeline"] == PIPELINE and existentes[0]["fonte_hash"] == hash_fonte(fonte) and existentes[0]["estado"] == "concluido" and not reprocessar:
            return {"documento": fonte["id"], "estado": "cache"}
    dados = preparar(fonte)
    destino = ROOT / "data/extracted" / (fonte["id"] + ".json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(destino)
    publicacao = publicar(banco, dados) if banco else {}
    return {"documento": fonte["id"], "trechos": len(dados["trechos"]), "entidades": len(dados["entidades"]),
            "declaracoes": len(dados["declaracoes"]), "estado_narrativo": "concluido", "estado_tabular": "pendente", **publicacao}
