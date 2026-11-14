"""Inicializa as constraints e os índices do projeto."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riscos.banco import Banco
from riscos.esquema import migrar

if __name__ == "__main__":
    banco = Banco()
    migrar(banco)
    print(banco.consultar("SHOW INDEXES YIELD name,type,state RETURN name,type,state"))
