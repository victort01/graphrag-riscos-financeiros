"""Identifica código, catálogos e dependências declaradas sem incluir segredos locais."""
import hashlib
import platform
import sys
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
    return {"sha256_codigo_catalogos_dependencias": hash_.hexdigest(), "python": sys.version.split()[0],
            "plataforma": platform.system(), "arquitetura": platform.machine()}
