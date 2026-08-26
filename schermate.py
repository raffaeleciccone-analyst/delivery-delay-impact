# -*- coding: utf-8 -*-
# Converte il PDF esportato da Power BI nelle schermate della consegna.
#
# Perche' dal PDF e non con una cattura a mano: l'export rende la pagina a piena
# risoluzione, senza la cornice della finestra e senza le tre icone (filtro,
# messa a fuoco, «...») che Power BI mostra in alto a destra quando il mouse
# passa sopra una visuale. In uno screenshot quelle finiscono dentro.
#
# In Power BI:  File -> Esporta -> Esporta report in PDF
#
# Uso:  python schermate.py <percorso del PDF>
#       python schermate.py                      (cerca il PDF piu' recente)

import glob, io, os, sys

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("manca pymupdf: installalo con  python -m pip install pymupdf")

RADICE = r"C:\dev\_powerbi"
FUORI = os.path.join(RADICE, "schermate")

# Le pagine escono nell'ordine di pages.json. I nomi dei file cominciano con un
# numero perche' su GitHub la cartella si ordina da sola.
# "dettaglio-fascia" non c'e': e' il riquadro che compare al passaggio del
# mouse, ed e' nascosto in visualizzazione, quindi l'export in PDF lo salta.
# "dentro-un-mese" invece e' visibile e viene esportata come le altre.
NOMI = [
    "01-la-domanda.png",
    "02-di-chi-e-il-ritardo.png",
    "03-come-cambia.png",
    "04-cosa-non-dice.png",
    "05-dentro-un-mese.png",
]

# La tela e' 1920x1080. A 2x le schermate reggono uno schermo denso e restano
# leggibili quando GitHub le rimpicciolisce.
SCALA = 2.0


def trova_pdf():
    cerca = [os.path.join(RADICE, "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Downloads", "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Desktop", "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Documents", "*.pdf")]
    trovati = []
    for c in cerca:
        trovati.extend(glob.glob(c))
    if not trovati:
        sys.exit("nessun PDF trovato: passalo come argomento\n"
                 "  python schermate.py \"C:\\percorso\\del\\file.pdf\"")
    return max(trovati, key=os.path.getmtime)


pdf = sys.argv[1] if len(sys.argv) > 1 else trova_pdf()
if not os.path.isfile(pdf):
    sys.exit("non trovo %s" % pdf)

doc = fitz.open(pdf)
print("PDF: %s  (%d pagine)" % (pdf, doc.page_count))

if doc.page_count != len(NOMI):
    print("ATTENZIONE: mi aspettavo %d pagine, ne trovo %d. "
          "Controlla di aver esportato tutto il report." % (len(NOMI), doc.page_count))

if not os.path.isdir(FUORI):
    os.makedirs(FUORI)

for i, pagina in enumerate(doc):
    nome = NOMI[i] if i < len(NOMI) else "%02d-pagina.png" % (i + 1)
    percorso = os.path.join(FUORI, nome)
    pix = pagina.get_pixmap(matrix=fitz.Matrix(SCALA, SCALA))
    pix.save(percorso)
    print("  %-28s %4d x %4d   %6.1f KB"
          % (nome, pix.width, pix.height, os.path.getsize(percorso) / 1024.0))

doc.close()

manca = os.path.join(FUORI, "04-modello.png")
if not os.path.isfile(manca):
    print()
    print("Manca ancora 04-modello.png: la vista Modello non esce nell'export.")
    print("In Power BI apri la vista Modello (l'icona in basso a sinistra),")
    print("sistema le otto tabelle in modo che le sei relazioni si vedano tutte,")
    print("e catturala a mano dentro schermate\\04-modello.png.")
