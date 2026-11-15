"""Resume recuperação e abstenção sem inferir suporte semântico por palavras-chave."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean


def ler(caminho):
    return json.loads(caminho.read_text(encoding="utf-8"))


def resumir(conjunto, recuperacao, respostas=None):
    perguntas = {p["id"]: p for p in conjunto["perguntas"]}
    variantes = {}
    for metodo in ("vetorial", "hibrido", "grafo"):
        linhas = [l for l in recuperacao["linhas"] if l["metodo"] == metodo]
        metricas = {}
        for grupo, ids in {
            "com_evidencia": {p["id"] for p in perguntas.values() if p["evidencias"]},
            "sem_controles_desenvolvimento": {p["id"] for p in perguntas.values()
                if p["evidencias"] and not p.get("proximidade_desenvolvimento", False)},
        }.items():
            elegiveis = [l for l in linhas if l["pergunta_id"] in ids]
            validas = [l for l in elegiveis if not l["erro"]]
            metricas[grupo] = {
                "perguntas": len(elegiveis), "execucoes_validas": len(validas),
                "recall_contexto_macro": mean(l["recall_contexto"] for l in validas) if validas else None,
                "recall_candidatos_macro": mean(l["recall_candidatos"] for l in validas) if validas else None,
                "nota": "Média somente das execuções válidas; falhas são informadas separadamente."}
        item = {"recuperacoes": len(linhas), "falhas_recuperacao": sum(bool(l["erro"]) for l in linhas),
                "recuperacao": metricas}
        if respostas:
            saidas = [l for l in respostas["linhas"] if l["metodo"] == metodo]
            validas = [l for l in saidas if not l["erro"]]
            negativas = [l for l in validas if perguntas[l["pergunta_id"]]["abstencao_esperada"]]
            item["geracao"] = {
                "execucoes": len(saidas), "falhas": len(saidas) - len(validas),
                "com_afirmacoes": sum(bool(l["resposta"]["afirmacoes"]) for l in validas),
                "abstencoes": sum(not l["resposta"]["afirmacoes"] for l in validas),
                "rejeitadas_pelas_guardas": sum(bool(l["resposta"]["validacao"]["erros"]) for l in validas),
                "casos_com_abstencao_obrigatoria": len(negativas),
                "abstencoes_nesses_casos": sum(not l["resposta"]["afirmacoes"] for l in negativas),
                "revisao_semantica_humana": "pendente"}
        variantes[metodo] = item
    return {"uso": conjunto["uso"], "estado_recuperacao": recuperacao["estado"],
        "estado_geracao": respostas["estado"] if respostas else "não executada",
        "sha256_conjunto": recuperacao["sha256_conjunto"],
        "versao_recuperacao": recuperacao["versao_execucao"],
        "versao_geracao": respostas["versao_geracao"] if respostas else None,
        "total_perguntas": len(perguntas), "variantes": variantes,
        "limites": ["Localizar a página e o termo não comprova suporte da resposta.",
            "Abstenção pode evitar erro e também recusar uma pergunta respondível.",
            "Não há taxa de alucinação ou superioridade semântica calculada automaticamente."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conjunto", required=True, type=Path)
    parser.add_argument("--recuperacao", required=True, type=Path)
    parser.add_argument("--respostas", type=Path)
    parser.add_argument("--saida", required=True, type=Path)
    args = parser.parse_args()
    recuperacao = ler(args.recuperacao)
    if hashlib.sha256(args.conjunto.read_bytes()).hexdigest() != recuperacao["sha256_conjunto"]:
        parser.error("O conjunto difere do congelado na recuperação.")
    respostas = ler(args.respostas) if args.respostas else None
    if respostas and hashlib.sha256(args.recuperacao.read_bytes()).hexdigest() != respostas["sha256_recuperacao"]:
        parser.error("As respostas pertencem a outra recuperação.")
    resultado = resumir(ler(args.conjunto), recuperacao, respostas)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado["variantes"], ensure_ascii=False, indent=2))
