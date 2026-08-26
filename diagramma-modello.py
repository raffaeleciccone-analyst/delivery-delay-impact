# -*- coding: utf-8 -*-
# Disegna lo schema a stella leggendolo dal modello, non ricopiandolo.
#
# La quarta schermata della consegna e' l'unica che non esce dall'export in PDF.
# La strada ovvia e' fotografare la vista Modello di Power BI; questa e' meglio
# per due motivi. Il disegno esce dal TMDL, quindi se il modello cambia il
# diagramma cambia con lui invece di restare una vecchia fotografia. E puo'
# dire quello che la vista Modello non dice: quali tabelle sono fatti, quali
# dimensioni, e perche' una relazione e' tratteggiata.
#
# Uso:  python diagramma-modello.py

import io, os, re, sys

try:
    import pymupdf
except ImportError:
    sys.exit("manca pymupdf: python -m pip install pymupdf")

RADICE = r"C:\dev\_powerbi"
MODELLO = os.path.join(RADICE, "delivery-delay-impact.SemanticModel", "definition")
FUORI = os.path.join(RADICE, "schermate")

# gli stessi del report
ROSSO, GRIGIO = (0.890, 0.286, 0.282), (0.541, 0.533, 0.502)
SFONDO, CARTA = (0.929, 0.925, 0.910), (1, 1, 1)
BORDO = (0.894, 0.886, 0.863)
INCHIOSTRO, INCHIOSTRO_2 = (0.102, 0.102, 0.098), (0.322, 0.318, 0.306)
INCHIOSTRO_3 = (0.404, 0.396, 0.373)
SCURO = (0.102, 0.102, 0.098)

L, A = 1600, 1000
SCALA = 2.0

CARATTERI = {
    "gr":  r"C:\Windows\Fonts\georgia.ttf",
    "grb": r"C:\Windows\Fonts\georgiab.ttf",
    "sn":  r"C:\Windows\Fonts\segoeui.ttf",
    "snb": r"C:\Windows\Fonts\seguisb.ttf",
}

# I due fatti in colonna al centro, le loro dimensioni a fianco: Clienti e
# Calendario stanno con Ordini, Venditori e Prodotti con RigheOrdine. Cosi'
# nessuna linea ne incrocia un'altra. In fondo, sotto un righello, le due
# tabelle senza relazioni.
POSTI = {
    "Clienti":              (100, 180),
    "Ordini":               (630, 180),
    "Calendario":           (100, 450),
    "RigheOrdine":          (630, 450),
    "Venditori":            (1160, 330),
    "Prodotti":             (1160, 570),
    "Misure":               (100, 790),
    "ControlloStatiOrdine": (630, 790),
}
FONDO_Y = 740          # il righello che separa le tabelle senza relazioni
FATTI = ("Ordini", "RigheOrdine")
LARGO, ALTO = 340, 116


# ------------------------------------------------------- si legge il modello

def leggi_modello():
    tabelle = {}
    for f in sorted(os.listdir(os.path.join(MODELLO, "tables"))):
        testo = io.open(os.path.join(MODELLO, "tables", f), encoding="utf-8").read()
        nome = f[:-5]
        colonne = re.findall(r"^\tcolumn\s+('([^']*(?:''[^']*)*)'|\S+)", testo, re.M)
        misure = re.findall(r"^\tmeasure\s+", testo, re.M)
        tabelle[nome] = {"colonne": len(colonne), "misure": len(misure)}

    testo = io.open(os.path.join(MODELLO, "relationships.tmdl"), encoding="utf-8").read()
    relazioni = []
    for blocco in testo.split("relationship ")[1:]:
        da = re.search(r"fromColumn:\s*(\S+)", blocco).group(1)
        a = re.search(r"toColumn:\s*(\S+)", blocco).group(1)
        attiva = "isActive: false" not in blocco
        relazioni.append({
            "da_tab": da.split(".")[0], "da_col": da.split(".", 1)[1],
            "a_tab": a.split(".")[0], "a_col": a.split(".", 1)[1],
            "attiva": attiva,
        })
    return tabelle, relazioni


# ---------------------------------------------------------------- si disegna

def riquadro(tab):
    x, y = POSTI[tab]
    return pymupdf.Rect(x, y, x + LARGO, y + ALTO)


def bordo_verso(r, altro, scarto=(0.0, 0.0)):
    """Il punto sul bordo del riquadro, nella direzione dell'altro riquadro.

    `scarto` sposta il centro da cui si parte: serve quando due relazioni
    collegano le stesse due tabelle e le loro linee finirebbero una sopra
    l'altra. Il punto resta comunque sul bordo, perche' si taglia il bordo a
    partire dal centro spostato invece di spostare il punto gia' tagliato."""
    cx = (r.x0 + r.x1) / 2 + scarto[0]
    cy = (r.y0 + r.y1) / 2 + scarto[1]
    dx, dy = altro[0] - cx, altro[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = ((r.x1 - cx) if dx > 0 else (cx - r.x0)) / abs(dx) if dx else float("inf")
    sy = ((r.y1 - cy) if dy > 0 else (cy - r.y0)) / abs(dy) if dy else float("inf")
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def perpendicolare(a, b, quanto):
    """Il versore perpendicolare al segmento a-b, moltiplicato per `quanto`."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    return -dy / n * quanto, dx / n * quanto


# per misurare il testo servono i font veri, non i nomi
METRICHE = {n: pymupdf.Font(fontfile=p) for n, p in CARATTERI.items()}


def scrivi(pagina, testo, x, y, dim, font, colore, centro=False):
    largo = METRICHE[font].text_length(testo, fontsize=dim)
    pagina.insert_text((x - largo / 2 if centro else x, y), testo,
                       fontname=font, fontfile=CARATTERI[font],
                       fontsize=dim, color=colore)


tabelle, relazioni = leggi_modello()

doc = pymupdf.open()
pag = doc.new_page(width=L, height=A)
for nome, percorso in CARATTERI.items():
    pag.insert_font(fontname=nome, fontfile=percorso)

pag.draw_rect(pymupdf.Rect(0, 0, L, A), color=None, fill=SFONDO)
pag.draw_rect(pymupdf.Rect(0, 0, L, 6), color=None, fill=ROSSO)

scrivi(pag, "IL MODELLO", 100, 62, 11, "snb", ROSSO)
scrivi(pag, "Schema a stella: otto tabelle, sei relazioni", 100, 100, 27, "gr", INCHIOSTRO)

# ------------------------------------------------------------- le relazioni
# Quando due relazioni collegano le stesse due tabelle (Ordini e Calendario,
# per la seconda data) le loro linee si sovrapporrebbero. Si scostano di
# quarantadue pixel per parte, perpendicolarmente alla linea, e le etichette
# non stanno tutte a meta': scorrono lungo la linea, se no si accavallano.
coppie = {}
for rel in relazioni:
    coppie.setdefault((rel["da_tab"], rel["a_tab"]), []).append(rel)

for (da, a), gruppo in coppie.items():
    ra, rb = riquadro(da), riquadro(a)
    ca = ((ra.x0 + ra.x1) / 2, (ra.y0 + ra.y1) / 2)
    cb = ((rb.x0 + rb.x1) / 2, (rb.y0 + rb.y1) / 2)
    perp = perpendicolare(ca, cb, 42)

    for i, rel in enumerate(gruppo):
        k = i - (len(gruppo) - 1) / 2.0
        scarto = (perp[0] * k, perp[1] * k)
        pa = bordo_verso(ra, cb, scarto)
        pb = bordo_verso(rb, ca, scarto)

        colore = ROSSO if not rel["attiva"] else GRIGIO
        forma = pag.new_shape()
        forma.draw_line(pymupdf.Point(*pa), pymupdf.Point(*pb))
        forma.finish(color=colore, width=2,
                     dashes="[7 5] 0" if not rel["attiva"] else None, closePath=False)
        forma.commit()

        def verso(p, q, d=24):
            dx, dy = q[0] - p[0], q[1] - p[1]
            n = (dx * dx + dy * dy) ** 0.5 or 1.0
            return p[0] + dx / n * d, p[1] + dy / n * d

        mx, my = verso(pa, pb)
        ux, uy = verso(pb, pa)
        scrivi(pag, "*", mx, my + 5, 20, "snb", colore, centro=True)
        scrivi(pag, "1", ux, uy + 5, 13, "snb", colore, centro=True)

        # l'etichetta si scosta perpendicolarmente alla linea, se no la linea
        # le passa dentro: sopra non basta, perche' una diagonale risale
        f = 0.5 if len(gruppo) == 1 else 0.32 + 0.36 * i
        mx = pa[0] + (pb[0] - pa[0]) * f
        my = pa[1] + (pb[1] - pa[1]) * f
        def scostata(quanto):
            ox, oy = perpendicolare(pa, pb, quanto)
            if oy > 0 or (abs(oy) < 0.5 and ox < 0):
                ox, oy = -ox, -oy
            return mx + ox, my + oy + 4

        if rel["attiva"]:
            x1, y1 = scostata(16)
            scrivi(pag, rel["da_col"], x1, y1, 11, "sn", INCHIOSTRO_3, centro=True)
        else:
            # due righe, tutte e due dalla stessa parte della linea: mettere la
            # seconda sotto la voleva dire farci passare in mezzo il tratteggio
            x1, y1 = scostata(48)
            x2, y2 = scostata(26)
            scrivi(pag, rel["da_col"], x1, y1, 11, "sn", ROSSO, centro=True)
            scrivi(pag, "inattiva, si accende con USERELATIONSHIP",
                   x2, y2, 11, "snb", ROSSO, centro=True)

# -------------------------------------------------------------- le tabelle
for tab, (x, y) in POSTI.items():
    r = riquadro(tab)
    fatto = tab in FATTI
    collegata = any(rel["da_tab"] == tab or rel["a_tab"] == tab for rel in relazioni)

    pag.draw_rect(r, color=BORDO, fill=SCURO if fatto else CARTA, width=1, radius=0.07)

    if fatto:
        etichetta, col_e = "FATTI", (1, 1, 1)
        col_n, col_d = (1, 1, 1), (0.788, 0.780, 0.753)
    elif not collegata:
        etichetta = ("Le misure stanno in una tabella dedicata" if tab == "Misure"
                     else "Conta gli otto stati anche quando l'analisi e' filtrata")
        col_e, col_n, col_d = INCHIOSTRO_3, INCHIOSTRO, INCHIOSTRO_2
    else:
        etichetta, col_e = "DIMENSIONE", GRIGIO
        col_n, col_d = INCHIOSTRO, INCHIOSTRO_2

    scrivi(pag, etichetta, r.x0 + 20, r.y0 + 30,
           9 if collegata or fatto else 10, "snb" if (collegata or fatto) else "sn", col_e)
    scrivi(pag, tab, r.x0 + 20, r.y0 + 62, 19, "grb" if fatto else "gr", col_n)
    info = tabelle[tab]
    dettaglio = ("%d misure" % info["misure"]) if info["misure"] else \
                ("%d colonne" % info["colonne"])
    scrivi(pag, dettaglio, r.x0 + 20, r.y0 + 92, 11, "sn", col_d)

# ------------------------------------------------- la fascia senza relazioni
pag.draw_line(pymupdf.Point(100, FONDO_Y), pymupdf.Point(L - 100, FONDO_Y),
              color=BORDO, width=1)
scrivi(pag, "SENZA RELAZIONI, DI PROPOSITO", 100, FONDO_Y + 30, 9, "snb", INCHIOSTRO_3)

# ------------------------------------------------------------------ il piede
scrivi(pag, "Disegnato leggendo delivery-delay-impact.SemanticModel con "
            "diagramma-modello.py: se il modello cambia, cambia anche questo disegno.",
       100, A - 58, 11, "sn", INCHIOSTRO_3)
scrivi(pag, "La tabella data e' creata a parte, non derivata dai fatti. La seconda data "
            "(data_consegna) resta inattiva e si accende in DAX con USERELATIONSHIP.",
       100, A - 34, 11, "sn", INCHIOSTRO_3)

if not os.path.isdir(FUORI):
    os.makedirs(FUORI)

png = os.path.join(FUORI, "05-modello.png")
pag.get_pixmap(matrix=pymupdf.Matrix(SCALA, SCALA)).save(png)
io.open(os.path.join(FUORI, "05-modello.svg"), "w", encoding="utf-8").write(
    pag.get_svg_image())
doc.close()

print("letto dal modello: %d tabelle, %d relazioni (%d inattiva)"
      % (len(tabelle), len(relazioni), sum(1 for r in relazioni if not r["attiva"])))
print("scritto %s  (%d x %d)" % (png, L * SCALA, A * SCALA))
print("scritto anche 05-modello.svg, vettoriale, per il README")
