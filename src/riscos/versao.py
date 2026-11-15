"""Identifica código, catálogos e dependências declaradas sem incluir segredos locais."""
import hashlib
import platform
import sys
import subprocess
from .config import ROOT


def identificar():
    arquivos = list((ROOT / "src").rglob("*.py"))
    arquivos += list((ROOT / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.ps1"))
    arquivos += list(ROOT.glob("requirements*.txt"))
    arquivos += [ROOT / p for p in ("app.py", "compose.yaml", ".env.example", "ui/grafo.html", "ui/vendor/cytoscape.min.js", "data/manifesto.json", "data/modelos.json")]
    hash_ = hashlib.sha256()
    for arquivo in sorted(arquivos, key=lambda p: p.relative_to(ROOT).as_posix()):
        hash_.update(arquivo.relative_to(ROOT).as_posix().encode())
        hash_.update(b"\0")
        hash_.update(arquivo.read_bytes())
        hash_.update(b"\0")
    git = {"commit_git": None, "arvore_git_alterada": None}
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=5)
        estado = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=5)
        git = {"commit_git": commit.stdout.strip(), "arvore_git_alterada": bool(estado.stdout.strip())}
    except (OSError, subprocess.SubprocessError):
        pass
    return {"sha256_codigo_catalogos_dependencias": hash_.hexdigest(), "python": sys.version.split()[0],
            "plataforma": platform.system(), "arquitetura": platform.machine(), **git}
