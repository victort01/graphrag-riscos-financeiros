"""Cópia de exibição dos previews; a versão editável é o PowerPoint."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

base = Path(__file__).resolve().parent
paginas = sorted((base / ".build/slides").glob("slide-*.png"))
if len(paginas) != 14:
    raise ValueError("Renderize os 14 slides finais antes de exportar.")
saida = base / "apresentacao-revisao.pdf"
pdf = canvas.Canvas(str(saida), pagesize=(960, 540), pageCompression=1)
pdf.setTitle("Exposições financeiras em grafos - versão para revisão")
pdf.setAuthor("Grupo de Tendências em Ciência da Computação - Unipê")
for pagina in paginas:
    pdf.drawImage(ImageReader(str(pagina)), 0, 0, width=960, height=540)
    pdf.showPage()
pdf.save()
print(saida)
