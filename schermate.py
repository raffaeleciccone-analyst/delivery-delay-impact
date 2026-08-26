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
    "04-dentro-un-mese.png",
    "05-cosa-non-dice.png",
]

# La tela e' 1920x1080. A 2x le schermate reggono uno schermo denso e restano
# leggibili quando GitHub le rimpicciolisce.
SCALA = 2.0

# il nome che il PDF deve avere perche' sia il nostro
ATTESO = "delivery-delay-impact"


def trova_pdf():
    """Il PDF piu' recente che somigli a questo report.

    La prima versione prendeva il piu' recente e basta, e il 26/08 ha pescato un
    CV dai Download scrivendoci sopra una schermata. Adesso il nome deve
    contenere quello del progetto. Fra i posti dove guardare c'e' anche la
    cartella temporanea dei lavori di stampa di Power BI, dove il PDF finisce se
    invece di Esporta si usa Stampa."""
    temp = os.environ.get("TEMP", "")
    cerca = [os.path.join(RADICE, "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Downloads", "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Desktop", "*.pdf"),
             os.path.join(os.path.expanduser("~"), "Documents", "*.pdf"),
             os.path.join(temp, "Power BI Desktop", "print-job-*", "*.pdf")]
    trovati = []
    for c in cerca:
        trovati.extend(glob.glob(c))
    nostri = [p for p in trovati if ATTESO in os.path.basename(p).lower()]
    if not nostri:
        sys.exit("nessun PDF di questo report: ne cerco uno che si chiami '%s...'.\n"
                 "Passalo come argomento:\n"
                 "  python schermate.py \"C:\\percorso\\del\\file.pdf\"" % ATTESO)
    return max(nostri, key=os.path.getmtime)


pdf = sys.argv[1] if len(sys.argv) > 1 else trova_pdf()
if not os.path.isfile(pdf):
    sys.exit("non trovo %s" % pdf)

doc = fitz.open(pdf)
print("PDF: %s  (%d pagine)" % (pdf, doc.page_count))

# Non un avviso: un'uscita. Con un avviso, il 26/08 lo script ha convertito la
# prima pagina di un PDF sbagliato e l'ha salvata come 01-la-domanda.png.
# Meglio nessuna schermata che una schermata di un altro documento.
if doc.page_count != len(NOMI):
    sys.exit("mi aspettavo %d pagine, ne trovo %d in %s. "
             "Non scrivo niente: controlla di aver esportato tutto il report."
             % (len(NOMI), doc.page_count, pdf))

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

manca = os.path.join(FUORI, "06-modello.png")
if not os.path.isfile(manca):
    print()
    print("Manca 06-modello.png: non viene dall'export, lo disegna")
    print("diagramma-modello.py leggendo il TMDL.")
    print("  python diagramma-modello.py")
