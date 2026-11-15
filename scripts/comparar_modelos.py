"""Executa geração pareada em contextos congelados e preserva todas as saídas."""
import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from riscos.config import ROOT
from baixar_modelos import baixar


def pronto():
    try:
        with urlopen('http://127.0.0.1:18081/health', timeout=2) as r:
            return json.load(r).get('status') == 'ok'
    except (OSError, ValueError):
        return False


def gravar(path, dados):
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def executar(conjunto, pasta, servidor):
    if pronto():
        raise RuntimeError('A porta do modelo já está em uso; não é seguro presumir qual modelo está carregado.')
    if pasta.exists() and any(pasta.iterdir()):
        raise ValueError('Escolha uma pasta vazia para preservar rodadas anteriores.')
    pasta.mkdir(parents=True, exist_ok=True)
    catalogo = ROOT/'data/modelos-comparacao-v2.json'
    modelos = json.loads(catalogo.read_text(encoding='utf-8'))['modelos']
    config = {**os.environ, 'LLM_MODEL': 'qwen-riscos-local',
              'LLM_URL': 'http://127.0.0.1:18081/v1/chat/completions', 'LLM_TIMEOUT': '600'}
    modelos_dir = ROOT/'data/models'
    modelos_dir.mkdir(parents=True, exist_ok=True)
    congelados = pasta/'contextos-comparacao-v2.json'
    recuperacao = pasta/'recuperacao-v2.json'
    resultados = []
    for indice, modelo in enumerate(modelos):
        baixar(modelo, modelos_dir)
        config['LLM_ARTIFACT'] = f"{modelo['repositorio'].split('/')[-1]}@{modelo['revisao']}:Q4_K_M"
        with (pasta/(modelo['id']+'.log')).open('wb') as log:
            processo = subprocess.Popen([str(servidor), '--model', str(modelos_dir/modelo['destino']),
                '--alias', 'qwen-riscos-local', '--host', '127.0.0.1', '--port', '18081',
                '--ctx-size', '4096', '--threads', '2', '--parallel', '1', '--batch-size', '128'],
                cwd=ROOT, stdout=log, stderr=log)
            try:
                for _ in range(120):
                    if pronto():
                        break
                    if processo.poll() is not None:
                        raise RuntimeError('O modelo encerrou durante a inicialização: '+modelo['id'])
                    time.sleep(1)
                if not pronto():
                    raise TimeoutError('O modelo não ficou pronto: '+modelo['id'])
                if indice == 0:
                    subprocess.run([sys.executable, 'scripts/avaliar_recuperacao.py', '--conjunto', str(conjunto),
                                    '--saida', str(recuperacao)], cwd=ROOT, env=config, check=True)
                    dados = json.loads(recuperacao.read_text(encoding='utf-8'))
                    if dados['estado'] != 'concluida':
                        raise RuntimeError('A recuperação teve falhas; não há base completa para comparação.')
                    dados['linhas'] = [r for r in dados['linhas'] if r['metodo']=='grafo']
                    gravar(congelados, dados)
                saida = pasta/('respostas-'+modelo['id']+'.json')
                subprocess.run([sys.executable, 'scripts/avaliar_respostas.py', '--conjunto', str(conjunto),
                                '--recuperacao', str(congelados), '--saida', str(saida)],
                               cwd=ROOT, env=config, check=True)
                resultados.append(json.loads(saida.read_text(encoding='utf-8')))
            finally:
                processo.terminate()
                try:
                    processo.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    processo.kill()
                    processo.wait()
    pares = [{r['pergunta_id']: r['sha256_contexto'] for r in d['linhas']} for d in resultados]
    if pares[0] != pares[1]:
        raise ValueError('Os modelos não receberam os mesmos contextos.')
    protocolo = json.loads(conjunto.read_text(encoding='utf-8'))
    if set(pares[0]) != {p['id'] for p in protocolo['perguntas']}:
        raise ValueError('A comparação não cobre o conjunto inteiro.')
    dados_rec = json.loads(recuperacao.read_text(encoding='utf-8'))
    resumo = {'uso': protocolo['uso'], 'sha256_conjunto': hashlib.sha256(conjunto.read_bytes()).hexdigest(),
        'sha256_catalogo_modelos': hashlib.sha256(catalogo.read_bytes()).hexdigest(),
        'sha256_contextos_congelados': hashlib.sha256(congelados.read_bytes()).hexdigest(),
        'contextos_identicos_por_pergunta': True, 'quantidade_perguntas': len(pares[0]),
        'versao_recuperacao': dados_rec['versao_execucao'], 'modelos': {}, 'recuperacao': {},
        'run_github': os.getenv('GITHUB_RUN_ID'), 'revisao_semantica': 'pendente',
        'limites': ['Só a geração é comparada entre modelos; a recuperação é a mesma.',
                   'Mais afirmações não demonstram mais correção; saídas brutas e guardas estão preservadas.',
                   'Latências descritivas, sem ensaio controlado de hardware ou repetição estatística.',
                   'Perguntas diferentes de V1 no mesmo corpus conhecido e com critérios assistidos.']}
    for metodo in ('vetorial', 'hibrido', 'grafo'):
        linhas = [r for r in dados_rec['linhas'] if r['metodo']==metodo]
        recall = [r['recall_contexto'] for r in linhas if r['recall_contexto'] is not None]
        resumo['recuperacao'][metodo] = {'execucoes': len(linhas), 'recall_contexto_macro': statistics.mean(recall),
                                        'falhas': sum(bool(r['erro']) for r in linhas)}
    negativas={p['id'] for p in protocolo['perguntas'] if p['abstencao_esperada']}
    for modelo,dados in zip(modelos,resultados):
        validas=[r for r in dados['linhas'] if not r['erro']]
        resumo['modelos'][modelo['id']]={'artefato': dados['modelo'], 'versao_geracao': dados['versao_geracao'],
            'execucoes':len(dados['linhas']), 'falhas': len(dados['linhas'])-len(validas),
            'com_afirmacoes':sum(bool(r['resposta']['afirmacoes']) for r in validas),
            'abstencoes':sum(not r['resposta']['afirmacoes'] for r in validas),
            'abstencoes_obrigatorias_observadas':sum(not r['resposta']['afirmacoes'] for r in validas if r['pergunta_id'] in negativas),
            'latencia_mediana_segundos':statistics.median(r['latencia_geracao_segundos'] for r in validas) if validas else None}
    gravar(pasta/'resumo-comparacao-v2.json', resumo)
    print(json.dumps(resumo, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--conjunto',type=Path,default=ROOT/'data/perguntas-validacao-v2.json')
    parser.add_argument('--saida',type=Path,required=True)
    parser.add_argument('--servidor',type=Path,default=ROOT/'data/models/llama-linux/llama-server')
    args=parser.parse_args()
    executar(args.conjunto.resolve(),args.saida.resolve(),args.servidor.resolve())
