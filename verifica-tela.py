# -*- coding: utf-8 -*-
# Controlla la tela senza aprire Power BI.
#
# Power BI non dice niente quando una visuale esce dalla pagina, ne quando due
# si sovrappongono, ne quando una misura non esiste, ne quando taglia il testo
# che non ci sta: mostra il vuoto. Questi controlli sono l'unico modo di
# accorgersene scrivendo testo.
#
# Uso:  python verifica-tela.py

import io, json, os, re, sys

RADICE = r"C:\dev\_powerbi"
PAGINE = os.path.join(RADICE, "delivery-delay-impact.Report", "definition", "pages")
MODELLO = os.path.join(RADICE, "delivery-delay-impact.SemanticModel", "definition")

L, A = 1920, 1080
MARGINE, GRONDA, COL = 48, 24, 130
COLONNE_X = [MARGINE + i * (COL + GRONDA) for i in range(12)]
COLONNE_D = [x + COL for x in COLONNE_X]          # i bordi destri validi
# le fasce di testata e i righelli attraversano tutta la tela apposta
FUORI_GRIGLIA = ("-banda", "-filo", "-righello")

problemi = []
stretti = []   # avvisi: stime, non misure


def guasto(dove, cosa):
    problemi.append("%-34s %s" % (dove, cosa))


# ------------------------------------------------ cosa dichiara il modello
def leggi_modello():
    """Oltre ai nomi restituisce il DAX intero e le misure marcate nascoste:
    servono al controllo 8, che distingue una misura orfana da un ingranaggio
    intermedio — l'ingranaggio lo nomina qualcun altro."""
    misure, colonne, testi, nascoste = set(), set(), [], set()
    for f in os.listdir(os.path.join(MODELLO, "tables")):
        tab = f[:-5]
        testo = io.open(os.path.join(MODELLO, "tables", f), encoding="utf-8").read()
        testi.append(testo)
        corrente = None
        for riga in testo.splitlines():
            m = re.match(r"\tmeasure\s+('([^']*(?:''[^']*)*)'|\S+)", riga)
            if m:
                corrente = (m.group(2) or m.group(1)).replace("''", "'")
                misure.add(corrente)
            elif riga[:1] == "\t" and riga[:2] != "\t\t":
                corrente = None
            elif corrente and riga.strip() == "isHidden":
                nascoste.add(corrente)
        for m in re.finditer(r"^\tcolumn\s+('([^']*(?:''[^']*)*)'|\S+)", testo, re.M):
            colonne.add((tab, (m.group(2) or m.group(1)).replace("''", "'")))
    return misure, colonne, "\n".join(testi), nascoste


# ------------------------------------------------------- le visuali su disco
def leggi_visuali():
    fuori, misure_pagina = {}, {}
    for pag in sorted(os.listdir(PAGINE)):
        d = os.path.join(PAGINE, pag, "visuals")
        if not os.path.isdir(d):
            continue
        p = json.load(io.open(os.path.join(PAGINE, pag, "page.json"), encoding="utf-8"))
        misure_pagina[pag] = (p.get("width", L), p.get("height", A), p.get("type"))
        v = []
        for nome in sorted(os.listdir(d)):
            j = json.load(io.open(os.path.join(d, nome, "visual.json"), encoding="utf-8"))
            v.append(j)
        fuori[pag] = v
    return fuori, misure_pagina


def riferimenti(o, misure, colonne):
    """Raccoglie ogni Measure/Column citata nel JSON di una visuale."""
    if isinstance(o, dict):
        for chiave, tipo in (("Measure", misure), ("Column", colonne)):
            if chiave in o and isinstance(o[chiave], dict) and "Property" in o[chiave]:
                try:
                    ent = o[chiave]["Expression"]["SourceRef"]["Entity"]
                except (KeyError, TypeError):
                    continue
                tipo.add(o[chiave]["Property"] if chiave == "Measure"
                         else (ent, o[chiave]["Property"]))
        for v in o.values():
            riferimenti(v, misure, colonne)
    elif isinstance(o, list):
        for v in o:
            riferimenti(v, misure, colonne)


def altezza_stimata(visual, larghezza):
    """Quanto e' alto, all'incirca, il testo di una casella.

    E' una stima, non una misura: Power BI impagina con le metriche vere del
    carattere, che qui non ci sono. Serve solo ad accorgersi che una scheda sta
    per traboccare, perche' Power BI il testo di troppo NON lo taglia: ci mette
    una barra di scorrimento, che dentro un cruscotto e' peggio.

    Larghezza media del carattere: 0,54 em nei bastoni, 0,56 nelle grazie.
    Erano 0,50 e 0,52, ed erano ottimiste: sul file aperto il 26/08 le caselle
    che questa stima dava intorno al 90% scorrevano davvero. I due numeri sono
    stati rialzati contro quel render, non scelti a occhio."""
    alto = 0.0
    for p in visual["objects"]["general"][0]["properties"]["paragraphs"]:
        for r in p["textRuns"]:
            s = r.get("textStyle", {})
            pt = float(str(s.get("fontSize", "10pt")).replace("pt", ""))
            px = pt * 96.0 / 72.0
            em = 0.56 if "Georgia" in s.get("fontFamily", "") else 0.54
            per_riga = max(1, int(larghezza / (px * em)))
            righe = max(1, -(-len(r["value"]) // per_riga))
            alto += righe * px * 1.35
    return alto


def sovrappone(a, b):
    return not (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"] or
                a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])


misure_mod, colonne_mod, dax_mod, misure_nascoste = leggi_modello()
misure_usate = set()
pagine, misure_pagina = leggi_visuali()

print("modello: %d misure, %d colonne" % (len(misure_mod), len(colonne_mod)))
print()

for pag, visuali in pagine.items():
    largo_pag, alto_pag, tipo_pag = misure_pagina[pag]
    print("--- %s: %d visuali%s" % (pag, len(visuali),
                                    {"Tooltip": "  (riquadro al mouse)",
                                     "Drillthrough": "  (pagina di dettaglio)"}.get(tipo_pag, "")))

    # 1. ogni misura e ogni colonna citata esiste davvero
    for v in visuali:
        m, c = set(), set()
        riferimenti(v["visual"], m, c)
        misure_usate |= m
        for nome in sorted(m - misure_mod):
            guasto(pag + "/" + v["name"], "misura inesistente: %s" % nome)
        for tab, nome in sorted(c - colonne_mod):
            guasto(pag + "/" + v["name"], "colonna inesistente: %s[%s]" % (tab, nome))

    # 2. niente esce dalla tela
    for v in visuali:
        p = v["position"]
        if (p["x"] < 0 or p["y"] < 0 or p["x"] + p["width"] > largo_pag
                or p["y"] + p["height"] > alto_pag):
            guasto(pag + "/" + v["name"], "esce dalla tela (%dx%d): x%d y%d %dx%d"
                   % (largo_pag, alto_pag, p["x"], p["y"], p["width"], p["height"]))

    # 3. niente si sovrappone, tranne quello che deve: la testata e' a strati, e
    #    ogni scheda e' una carta con il suo testo rientrato sopra
    corpo = [v for v in visuali if not v["name"].endswith(FUORI_GRIGLIA)
             and not v["name"].endswith(("-testa", "-pagina"))]
    for i, a in enumerate(corpo):
        for b in corpo[i + 1:]:
            if a["name"].rsplit("-", 1)[0] == b["name"].rsplit("-", 1)[0]:
                continue
            if sovrappone(a["position"], b["position"]):
                guasto(pag, "si sovrappongono: %s e %s" % (a["name"], b["name"]))

    # 4. il corpo sta sulla griglia a dodici colonne. Quello che sta dentro una
    #    carta (il testo delle schede, l'etichetta e il numero dei riquadri) e'
    #    rientrato apposta: sulla griglia ci sta la carta che lo contiene.
    for v in (corpo if tipo_pag != "Tooltip" else []):
        if v["name"].endswith(("-testo", "-etichetta", "-numero")):
            continue
        p = v["position"]
        if p["x"] not in COLONNE_X and p["x"] - 4 not in COLONNE_X:
            guasto(pag + "/" + v["name"], "bordo sinistro fuori griglia: x=%d" % p["x"])
        destro = p["x"] + p["width"]
        if destro not in COLONNE_D and destro + 4 not in COLONNE_D:
            guasto(pag + "/" + v["name"], "bordo destro fuori griglia: x=%d" % destro)

    # 5. il titolo di una visuale sta su una riga sola (stima)
    #    Un titolo che va a capo si prende una ventina di pixel di altezza, e
    #    quelli mancano al contenuto: e' cosi' che e' ricomparsa due volte la
    #    barra di scorrimento nella tabella di pagina 3.
    for v in visuali:
        try:
            t = v["visual"]["visualContainerObjects"]["title"][0]["properties"]
        except (KeyError, IndexError, TypeError):
            continue
        testo_t = t["text"]["expr"]["Literal"]["Value"].strip("'").replace("''", "'")
        pt = float(t["fontSize"]["expr"]["Literal"]["Value"].rstrip("D"))
        largo = len(testo_t) * pt * 96.0 / 72.0 * 0.52
        utile = v["position"]["width"] - 40
        # avvisa gia' all'85%: la stima e' approssimativa, e un titolo che va a
        # capo si e' rivelato costoso due volte
        if largo > utile * 0.85:
            stretti.append("%-34s titolo stimato %d px su %d: rischia di andare a capo"
                           % (pag + "/" + v["name"], largo, utile))

    # 6. il testo ci sta dentro (stima)
    for v in visuali:
        # le fasce di colore e le carte delle schede non hanno testo dentro
        if (v["visual"]["visualType"] != "textbox"
                or v["name"].endswith(FUORI_GRIGLIA) or v["name"].endswith("-carta")):
            continue
        p = v["position"]
        alto = altezza_stimata(v["visual"], p["width"])
        if alto > p["height"] * 0.85:
            stretti.append("%-34s testo stimato %d px in %d di altezza"
                           % (pag + "/" + v["name"], alto, p["height"]))

    # 7. il numero di un riquadro ci sta nella sua casella
    #    Due modi di sbagliare, tutti e due silenziosi.
    #    Il primo: la casella e' piu' bassa del carattere e il numero perde la
    #    pancia. Serve circa 1,4 volte il corpo.
    #    Il secondo, scoperto sul PDF del 26/08: sotto una certa taglia Power BI
    #    la scheda non la disegna proprio, e lascia la casella vuota. Due
    #    schede da 30x88 e 30x118 sono uscite bianche mentre quelle da 66x260
    #    funzionavano. La soglia sta in mezzo: qui si pretendono 56x150, che e'
    #    dal lato sicuro di tutte e due le misure.
    for v in visuali:
        if v["visual"]["visualType"] != "card":
            continue
        try:
            pt = float(v["visual"]["objects"]["labels"][0]["properties"]
                       ["fontSize"]["expr"]["Literal"]["Value"].rstrip("D"))
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        serve = max(pt * 96.0 / 72.0 * 1.25, 56)
        h, larg = v["position"]["height"], v["position"]["width"]
        if h < serve or larg < 150:
            guasto(pag + "/" + v["name"],
                   "scheda troppo piccola, resta vuota: %dx%d px, servono %dx150"
                   % (larg, h, serve))

# 8. nessuna misura del modello gira a vuoto
#    Una misura che non sta su nessun visuale e che nessun'altra misura cita e'
#    una risposta promessa e mai data: chi apre il modello la trova nell'elenco
#    dei campi e si chiede a cosa serva. Gli ingranaggi intermedi sono un'altra
#    cosa e si riconoscono da soli, perche' qualcun altro li nomina; quelli che
#    servono solo ai controlli si marcano isHidden e si tolgono di mezzo.
orfane = []
for nome in sorted(misure_mod - misure_usate - misure_nascoste):
    # citata da un'altra misura? allora e' un ingranaggio, non un'orfana
    if ("[" + nome + "]") not in dax_mod:
        orfane.append(nome)
if orfane:
    for nome in orfane:
        guasto("modello", "misura mai usata da nessuno: %s" % nome)

print()
if stretti:
    print("%d caselle al limite (stima, da confermare a occhio):" % len(stretti))
    for a in sorted(set(stretti)):
        print("  " + a)
    print()

if problemi:
    print("%d problemi:" % len(problemi))
    for p in sorted(set(problemi)):
        print("  " + p)
    sys.exit(1)
print("nessun problema: riferimenti, ingombri e griglia tornano.")
