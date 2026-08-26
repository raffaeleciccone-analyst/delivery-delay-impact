# -*- coding: utf-8 -*-
# Costruisce le pagine del report in formato PBIR (JSON, uno per visuale).
#
# Il modello lo scrive costruisci-modello.ps1; questo scrive la tela.
# Non tocca l'involucro (.platform, definition.pbir, version.json, il tema):
# quello lo ha generato Power BI e cambia versione con lui.
#
# Uso:  python costruisci-report.py && python verifica-tela.py

import io, json, os, re, shutil

RADICE = r"C:\dev\_powerbi"
REPORT = os.path.join(RADICE, "delivery-delay-impact.Report", "definition")
PAGINE = os.path.join(REPORT, "pages")

_S = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
S_VIS  = _S + "visualContainer/2.12.0/schema.json"
S_PAG  = _S + "page/2.1.0/schema.json"
S_PAGS = _S + "pagesMetadata/1.1.0/schema.json"

# =========================================================== DAL MODELLO


def costante(misura):
    """Legge dal TMDL il valore di una misura che e' un numero fisso.

    Serve per il tasso di cambio nel piede di pagina 1. La strada ovvia sarebbe
    una scheda numerica come quelle dei riquadri, ma una scheda di 30 pixel
    Power BI non la disegna: mostra la casella vuota, e sul PDF del 26/08 il
    numero non c'era. Cosi' invece il valore entra nel testo quando si genera la
    pagina: se qualcuno cambia la misura, il piede cambia alla prossima
    generazione, e non c'e' nessun numero scritto a mano che possa mentire."""
    tmdl = os.path.join(RADICE, "delivery-delay-impact.SemanticModel", "definition",
                        "tables", "Misure.tmdl")
    testo = io.open(tmdl, encoding="utf-8").read()
    m = re.search(r"^	measure '" + re.escape(misura) + r"' = ([0-9.]+)\s*$",
                  testo, re.M)
    if not m:
        raise SystemExit("non trovo la costante %s in Misure.tmdl" % misura)
    return m.group(1).replace(".", ",")


# =========================================================== LA GRIGLIA
# Dodici colonne, gronda 24, margine 48. Ogni visuale comincia e finisce su una
# colonna. verifica-tela.py lo controlla dopo ogni generazione.
L, A = 1920, 1080
MARGINE, GRONDA, COLONNE = 48, 24, 12
COL = (L - 2 * MARGINE - (COLONNE - 1) * GRONDA) // COLONNE      # 130


def X(i):
    return MARGINE + i * (COL + GRONDA)          # X(0)=48  X(9)=1434


def W(n):
    return n * COL + (n - 1) * GRONDA            # W(3)=438 W(12)=1824


TESTA = 156     # la testata scura
CIMA  = 180     # dove comincia il contenuto
FONDO = 1000    # dove finisce
PIEDE = 1024

# Il margine interno delle schede. Power BI non ne da' nessuno alle caselle di
# testo: il testo tocca il bordo del riquadro. L'unico modo di farlo respirare
# e' separare il contenitore dal contenuto, che e' quello che fa scheda().
RIENTRO_X, RIENTRO_S, RIENTRO_G = 20, 18, 16

# =========================================================== I COLORI
# Un accento e un contesto, piu' i grigi del testo. Il rosso segnala il problema
# e non compare per decorazione.
#
# Validati con scripts/validate_palette.js del metodo dataviz, su carta bianca:
#   #E34948 <-> #8A8880   CVD 8,4 (obiettivo 8)   visione normale 18,7   contrasto ok
# Il grigio chiaro di prima (#B4B2AB) stava a 2,1:1 sulla carta, sotto la soglia
# di 3:1: le barre "in orario" sparivano.
ROSSO        = "#E34948"
ROSSO_TENUE  = "#FBEBEA"   # il fondo del riquadro-perno
GRIGIO       = "#8A8880"   # il contesto nei grafici
SFONDO       = "#EDECE8"   # un gradino piu' grigio: la carta bianca stacca di piu'
CARTA        = "#FFFFFF"
BORDO        = "#E4E2DC"
INCHIOSTRO   = "#1A1A19"
INCHIOSTRO_2 = "#52514E"
INCHIOSTRO_3 = "#67655F"   # piedi e didascalie: 4,9:1 sul fondo nuovo

SCURO        = "#1A1A19"   # la testata
SU_SCURO     = "#FFFFFF"
SU_SCURO_2   = "#C9C7C0"
SU_SCURO_3   = "#93918A"

# Le parole in grazie, i numeri in bastoni. E' la coppia dei quotidiani, e serve
# a togliere di dosso al file l'aria di Power BI appena installato.
FONT_T = "Georgia, serif"
FONT   = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
FONT_G = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"

# =========================================================== MATTONCINI


def _lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def _txt(v):
    return _lit("'" + str(v).replace("'", "''") + "'")


def _col(hex_):
    return {"solid": {"color": _lit("'" + hex_ + "'")}}


def _campo(tabella, nome, misura=True):
    tipo = "Measure" if misura else "Column"
    return {
        "field": {tipo: {"Expression": {"SourceRef": {"Entity": tabella}}, "Property": nome}},
        "queryRef": tabella + "." + nome,
        "nativeQueryRef": nome,
    }


def _riquadro(sfondo=CARTA, ombra=True):
    """Carta, bordo tenue, niente barra di intestazione. L'ombra e' appena
    percepibile: stacca dal fondo senza decorare."""
    o = {
        "background": [{"properties": {"show": _lit("true"), "color": _col(sfondo),
                                       "transparency": _lit("0D")}}],
        "border": [{"properties": {"show": _lit("true"), "color": _col(BORDO),
                                   "radius": _lit("8D")}}],
        "visualHeader": [{"properties": {"show": _lit("false")}}],
        # Power BI se lo scrive da solo, e ci mette dentro il nome grezzo della
        # colonna: "...per fascia_ritardo". Va spento su tutto.
        "subTitle": [{"properties": {"show": _lit("false")}}],
    }
    if ombra:
        o["dropShadow"] = [{"properties": {"show": _lit("true"), "color": _col("#000000"),
                                           "transparency": _lit("94D"), "shadowSpread": _lit("0D"),
                                           "shadowBlur": _lit("10D"), "position": _txt("Outer")}}]
    return o


def _titolo(testo_, dim=14, colore=INCHIOSTRO, font=FONT_T):
    return {"title": [{"properties": {
        "show": _lit("true"),
        "text": _txt(testo_),
        "alignment": _txt("left"),
        "fontSize": _lit(str(dim) + "D"),
        "fontFamily": _txt(font),
        "fontColor": _col(colore),
        "titleWrap": _lit("true"),
    }}]}


def _contenitore(nome, x, y, w, h, z, visual):
    return {
        "$schema": S_VIS,
        "name": nome,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": visual,
    }


# =========================================================== I VISUALI


def testo(nome, x, y, w, h, z, paragrafi, sfondo=None, bordo=False, allinea=None):
    """paragrafi: (testo, dimensione, font, colore)"""
    par = []
    for t, dim, font, colore in paragrafi:
        stile = {"fontSize": str(dim) + "pt", "fontFamily": font, "color": colore}
        if font == FONT_G:
            stile["fontWeight"] = "bold"
        q = {"textRuns": [{"value": t, "textStyle": stile}]}
        if allinea:
            q["horizontalTextAlignment"] = allinea
        par.append(q)

    vco = {"visualHeader": [{"properties": {"show": _lit("false")}}]}
    if sfondo:
        vco["background"] = [{"properties": {"show": _lit("true"), "color": _col(sfondo),
                                             "transparency": _lit("0D")}}]
    if bordo:
        vco["border"] = [{"properties": {"show": _lit("true"), "color": _col(BORDO),
                                         "radius": _lit("8D")}}]
    return _contenitore(nome, x, y, w, h, z, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": par}}]},
        "visualContainerObjects": vco,
        "drillFilterOtherVisuals": True,
    })


def banda(nome, x, y, w, h, z, colore):
    """Una fascia di colore: fondo, filo, righello."""
    return testo(nome, x, y, w, h, z, [("", 6, FONT, INCHIOSTRO)], sfondo=colore)


def scheda(nome, x, y, w, h, z, titolo_, corpo, dim=10, sfondo=CARTA):
    """Due visuali invece di una: la carta (fondo, bordo, ombra) e il testo
    dentro, rientrato di RIENTRO_X. E' l'unico modo di dare un margine interno
    a una casella di testo in Power BI, che altrimenti scrive fino al bordo.

    Per lo stesso motivo il titolo e' il primo paragrafo e non il titolo del
    contenitore: cosi' rientra insieme al resto del testo.

    corpo: stringa, oppure (stringa, stile) con stile in "forte" o "rosso"."""
    par = [{"textRuns": [{"value": titolo_, "textStyle": {
        "fontSize": "14pt", "fontFamily": FONT_T, "color": INCHIOSTRO}}]},
        {"textRuns": [{"value": "", "textStyle": {"fontSize": "5pt"}}]}]
    for c in corpo:
        t, stile = c if isinstance(c, tuple) else (c, "")
        if t == "":
            par.append({"textRuns": [{"value": "", "textStyle": {"fontSize": "6pt"}}]})
            continue
        s = {"fontSize": str(dim) + "pt", "fontFamily": FONT, "color": INCHIOSTRO_2}
        if stile == "forte":
            s.update({"fontFamily": FONT_G, "fontWeight": "bold", "color": INCHIOSTRO})
        elif stile == "rosso":
            s.update({"fontFamily": FONT_G, "fontWeight": "bold", "color": ROSSO})
        par.append({"textRuns": [{"value": t, "textStyle": s}]})

    carta = _contenitore(nome + "-carta", x, y, w, h, z, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [
            {"textRuns": [{"value": "", "textStyle": {"fontSize": "6pt"}}]}]}}]},
        "visualContainerObjects": _riquadro(sfondo),
        "drillFilterOtherVisuals": True,
    })
    dentro = _contenitore(nome + "-testo", x + RIENTRO_X, y + RIENTRO_S,
                          w - 2 * RIENTRO_X, h - RIENTRO_S - RIENTRO_G, z + 1, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": par}}]},
        "visualContainerObjects": {"visualHeader": [{"properties": {"show": _lit("false")}}]},
        "drillFilterOtherVisuals": True,
    })
    return [carta, dentro]


ETICHETTA_H = 40   # la fascia dell'etichetta: una riga da 11pt e il suo respiro


def riquadro(nome, x, y, w, h, z, misura, etichetta, accento=False, dim=34):
    """Tre visuali: la carta, l'etichetta e il numero.

    Con il titolo del contenitore l'etichetta restava incollata all'angolo in
    alto a sinistra mentre il numero si centrava nello spazio rimasto, e le due
    cose non stavano su nessun asse comune. Qui l'etichetta ha il suo margine e
    il numero le sta sotto, tutti e due centrati sulla stessa mezzeria.

    L'accento cambia il fondo invece di aggiungere un fregio."""
    carta = _contenitore(nome + "-carta", x, y, w, h, z, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [
            {"textRuns": [{"value": "", "textStyle": {"fontSize": "6pt"}}]}]}}]},
        "visualContainerObjects": _riquadro(ROSSO_TENUE if accento else CARTA),
        "drillFilterOtherVisuals": True,
    })
    eti = testo(nome + "-etichetta", x + RIENTRO_X, y + RIENTRO_S,
                w - 2 * RIENTRO_X, ETICHETTA_H, z + 1,
                [(etichetta, 11, FONT_G, INCHIOSTRO_2)], allinea="center")
    cima_n = y + RIENTRO_S + ETICHETTA_H
    numero = _numero(nome + "-numero", x + 12, cima_n, w - 24,
                     y + h - RIENTRO_G - cima_n, z + 2, misura,
                     dim + 6 if accento else dim, ROSSO if accento else INCHIOSTRO)
    return [carta, eti, numero]


def didascalia(nome, x, y, w, z, testo_):
    """Sotto ogni riquadro, la base su cui e' calcolato quel numero. Centrata
    come l'etichetta e il numero, sulla stessa mezzeria."""
    return testo(nome, x + 4, y, w - 8, 32, z, [(testo_, 9, FONT, INCHIOSTRO_3)],
                 allinea="center")


def _assi(dim_categoria=11, interno=None, etichette=True, asse_valori=False):
    """etichette: il numero scritto sopra ogni punto. Vanno bene su otto fasce,
    non su venti mesi per due serie: li' si sovrappongono e si legge il grafico
    peggio che senza. Quando si spengono, serve l'asse dei valori al loro posto,
    altrimenti la scala non e' scritta da nessuna parte."""
    asse_cat = {
        "showAxisTitle": _lit("false"), "fontSize": _lit(str(dim_categoria) + "D"),
        "fontFamily": _txt(FONT), "labelColor": _col(INCHIOSTRO_2),
    }
    if interno is not None:
        # con poche categorie Power BI tiene le barre sottili e le incolla in
        # cima, lasciando il fondo del riquadro bianco
        asse_cat["innerPadding"] = _lit(str(interno) + "D")
    return {
        "categoryAxis": [{"properties": asse_cat}],
        "valueAxis": [{"properties": {
            "show": _lit("true" if asse_valori else "false"),
            "showAxisTitle": _lit("false"),
            "gridlineShow": _lit("true" if asse_valori else "false"),
            "gridlineColor": _col(BORDO),
            "fontSize": _lit("10D"), "fontFamily": _txt(FONT),
            "labelColor": _col(INCHIOSTRO_3),
        }}],
        "labels": [{"properties": {
            "show": _lit("true" if etichette else "false"), "fontSize": _lit("11D"),
            "fontFamily": _txt(FONT_G), "color": _col(INCHIOSTRO),
            # 1 = nessuna unita'. Senza, l'ultima fascia di pagina 5 scriveva
            # "0K" su 360 ordini: un arrotondamento che cancella il dato.
            "labelDisplayUnits": _lit("1D"),
        }}],
    }


def barre(nome, x, y, w, h, z, categoria, serie, titolo_, forma="colonne",
          legenda=None, ordina=None, dim_categoria=11, interno=None,
          etichette=True, asse_valori=False, dettaglio=None):
    """serie: lista di (misura, colore). Il colore si assegna per serie.

    forma: "colonne"    colonne impilate. Con una sola serie piena per categoria
                        la barra resta larga quanto la fascia, invece di
                        ritirarsi nel posto lasciato libero dall'altra serie;
           "fasce"      barre orizzontali impilate: le due fasi di una durata
                        sono le parti di un totale;
           "classifica" barre orizzontali ordinate, con le etichette diritte;
           "linee"      una grandezza nel tempo. Le colonne affiancate direbbero
                        la stessa cosa, ma su venti mesi diventano quaranta
                        stecchi e il profilo dell'anno non si vede piu'.
    """
    tipo = {"colonne": "columnChart", "fasce": "barChart",
            "classifica": "clusteredBarChart", "linee": "lineChart"}[forma]
    tab_cat, col_cat = categoria
    obj = _assi(dim_categoria, interno, etichette, asse_valori)
    if forma == "linee":
        obj["lineStyles"] = [{"properties": {"strokeWidth": _lit("2D"),
                                             "showMarker": _lit("true"),
                                             "markerSize": _lit("4D")}}]
    obj["legend"] = [{"properties": {
        "show": _lit("true" if (legenda and len(serie) > 1) else "false"),
        "position": _txt("Top"), "showTitle": _lit("false"),
        "fontSize": _lit("11D"), "labelColor": _col(INCHIOSTRO_2),
        "fontFamily": _txt(FONT),
    }}]
    if len(serie) > 1:
        obj["dataPoint"] = [
            {"properties": {"fill": _col(colore)},
             "selector": {"metadata": "Misure." + misura}}
            for misura, colore in serie
        ]
    else:
        obj["dataPoint"] = [{"properties": {"fill": _col(serie[0][1])}}]
    query = {"queryState": {
        "Category": {"projections": [_campo(tab_cat, col_cat, misura=False)]},
        "Y": {"projections": [_campo("Misure", m) for m, _ in serie]},
    }}
    if ordina:
        misura_ord, verso = ordina
        query["sortDefinition"] = {
            "sort": [{"field": _campo("Misure", misura_ord)["field"], "direction": verso}],
            "isDefaultSort": True,
        }
    vco = dict(_riquadro(), **_titolo(titolo_))
    if dettaglio:
        # il riquadro di dettaglio si apre sul punto sotto il mouse, con il
        # filtro di quel punto gia' addosso: e' l'unico modo di far rispondere
        # ai dati un grafico che non ha nessun altro visuale da filtrare
        vco["visualTooltip"] = [{"properties": {
            "show": _lit("true"), "type": _txt("Canvas"), "section": _txt(dettaglio),
        }}]
    return _contenitore(nome, x, y, w, h, z, {
        "visualType": tipo,
        "query": query,
        "objects": obj,
        "visualContainerObjects": vco,
        "drillFilterOtherVisuals": True,
    })


def tabella(nome, x, y, w, h, z, colonne, titolo_, ordina=None, larghezze=None):
    """larghezze: quanti pixel per colonna. Senza, Power BI le stringe sul
    contenuto e lascia vuoto tutto lo spazio che avanza a destra."""
    query = {"queryState": {"Values": {
        "projections": [_campo(t, c, misura=False) for t, c in colonne]}}}
    if ordina:
        tab_o, col_o, verso = ordina
        query["sortDefinition"] = {
            "sort": [{"field": _campo(tab_o, col_o, misura=False)["field"],
                      "direction": verso}],
            "isDefaultSort": True,
        }
    return _contenitore(nome, x, y, w, h, z, {
        "visualType": "tableEx",
        "query": query,
        "objects": dict({
            "grid": [{"properties": {"gridVertical": _lit("false"),
                                     "gridHorizontalColor": _col(BORDO),
                                     "outlineColor": _col(BORDO),
                                     "rowPadding": _lit("6D")}}],
            "values": [{"properties": {"fontSize": _lit("11D"),
                                       "fontFamily": _txt(FONT),
                                       "fontColor": _col(INCHIOSTRO_2)}}],
            "columnHeaders": [{"properties": {"fontFamily": _txt(FONT_G),
                                              "fontSize": _lit("11D"),
                                              "fontColor": _col(INCHIOSTRO_2),
                                              "backColor": _col(CARTA)}}],
        }, **({
            "general": [{"properties": {"autoSizeColumnWidth": _lit("false")}}],
            "columnWidth": [
                {"properties": {"value": _lit(str(px) + "D")},
                 "selector": {"metadata": tab + "." + col}}
                for (tab, col), px in zip(colonne, larghezze)
            ],
        } if larghezze else {})),
        "visualContainerObjects": dict(_riquadro(), **_titolo(titolo_)),
        "drillFilterOtherVisuals": True,
    })


def _numero(nome, x, y, w, h, z, misura, dim, colore, tabella="Misure", colonna=False):
    """Il numero da solo, senza fondo: e' un pezzo di un'altra composizione.
    Lo usano i riquadri e le didascalie che citano una misura."""
    return _contenitore(nome, x, y, w, h, z, {
        "visualType": "card",
        "query": {"queryState": {"Values": {
            "projections": [_campo(tabella, misura, misura=not colonna)]}}},
        "objects": {
            "labels": [{"properties": {
                "fontSize": _lit(str(dim) + "D"),
                "fontFamily": _txt(FONT_G),
                "color": _col(colore),
                # 1 = nessuna unita'. Senza, sceglie lui e arrotonda a "3K".
                "labelDisplayUnits": _lit("1D"),
            }}],
            "categoryLabels": [{"properties": {"show": _lit("false")}}],
            "wordWrap": [{"properties": {"show": _lit("false")}}],
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": _lit("false")}}],
            "border": [{"properties": {"show": _lit("false")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}],
        },
        "drillFilterOtherVisuals": True,
    })


def didascalia_misura(nome, x, y, w, z, misura, testo_, largo_n=150, largo_t=190,
                      alto=60):
    """Una didascalia in cui il numero non e' battuto a mano: scende dal modello
    come quello del riquadro sopra. Serve dove la cifra grande da sola non basta
    — un valore assoluto senza la sua quota non si sa se sia molto o poco.

    Le misure della casella non sono estetiche. La prima versione era 88x30 e
    **sul file aperto non disegnava niente**: Power BI, sotto una certa taglia,
    la scheda numerica la lascia vuota invece di rimpicciolire il numero, e non
    lo dice. Le schede che funzionano in questo file sono larghe almeno 180 e
    alte almeno 60; queste stanno sopra quella soglia, e il controllo 7 di
    verifica-tela.py adesso la fa rispettare."""
    sinistra = x + (w - (largo_n + 6 + largo_t)) // 2
    return [
        _numero(nome + "-numero", sinistra, y, largo_n, alto, z, misura, 13, INCHIOSTRO),
        testo(nome + "-testo", sinistra + largo_n + 6, y + (alto - 28) // 2,
              largo_t, 28, z + 1, [(testo_, 9, FONT, INCHIOSTRO_3)]),
    ]


def riga_valore(nome, x, y, w, z, etichetta, misura, largo_n=180, dim=14, alto=60):
    """Una riga del riquadro di dettaglio: la voce a sinistra, il numero a destra.
    Due visuali, perche' la voce e' testo e il numero deve scendere dal modello.

    Le righe sono alte 60 e la scheda larga 180 per la stessa ragione della
    didascalia: sotto quella taglia Power BI la scheda numerica la lascia vuota."""
    return [
        testo(nome + "-testo", x, y + (alto - 24) // 2, w - largo_n - 8, 24, z,
              [(etichetta, 10, FONT, INCHIOSTRO_2)]),
        _numero(nome + "-numero", x + w - largo_n, y, largo_n, alto, z + 1,
                misura, dim, INCHIOSTRO),
    ]


def filtro(nome, x, y, w, h, z, tabella, colonna, etichetta, gruppo):
    """Un filtro a discesa. Il gruppo di sincronizzazione fa si' che la scelta
    fatta su una pagina valga anche sulle altre che portano lo stesso gruppo:
    senza, si torna indietro di una pagina e il filtro e' sparito.

    Quali colonne si possono mettere qui non e' libero. Il filtro deve arrivare
    a tutte le misure della pagina, e i filtri scendono dal lato "uno" al lato
    "molti": Calendario e Clienti stanno sopra Ordini, che sta sopra RigheOrdine,
    quindi arrivano dappertutto. Venditori e Prodotti stanno sopra RigheOrdine ma
    NON sopra Ordini: un filtro sul venditore lascerebbe ferme le misure che
    scendono dagli ordini, e la pagina mostrerebbe due popolazioni diverse
    fingendo che siano la stessa. Per questo qui non c'e'."""
    return _contenitore(nome, x, y, w, h, z, {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {
            "projections": [_campo(tabella, colonna, misura=False)]}}},
        "syncGroup": {"groupName": gruppo, "fieldChanges": False, "filterChanges": True},
        "objects": {
            "data": [{"properties": {"mode": _txt("Dropdown")}}],
            # l'intestazione del filtro scriverebbe il nome grezzo della colonna
            # ("stato"): l'etichetta e' il titolo del contenitore
            "header": [{"properties": {"show": _lit("false")}}],
            "items": [{"properties": {
                "fontColor": _col(INCHIOSTRO), "fontSize": _lit("11D"),
                "fontFamily": _txt(FONT), "background": _col(CARTA),
            }}],
            "selection": [{"properties": {
                "selectAllCheckboxEnabled": _lit("true"), "singleSelect": _lit("false"),
            }}],
        },
        "visualContainerObjects": dict(_riquadro(ombra=False),
                                       **_titolo(etichetta, dim=11, colore=INCHIOSTRO_2,
                                                 font=FONT_G)),
        "drillFilterOtherVisuals": True,
    })


# =========================================================== LA CORNICE


def intestazione(prefisso, titolo_, sottotitolo, occhiello, pagina_di):
    """La testata: una fascia scura chiusa sotto da un filo rosso. E' la cosa
    che si vede per prima e che tiene insieme le tre pagine."""
    return [
        banda(prefisso + "-banda", 0, 0, L, TESTA - 6, 1, SCURO),
        banda(prefisso + "-filo", 0, TESTA - 6, L, 6, 2, ROSSO),
        testo(prefisso + "-testa", MARGINE, 24, W(9), 118, 4, [
            (occhiello, 10, FONT_G, ROSSO),
            (titolo_, 27, FONT_T, SU_SCURO),
            (sottotitolo, 11, FONT, SU_SCURO_2),
        ]),
        testo(prefisso + "-pagina", X(9), 30, W(3), 30, 5,
              [(pagina_di, 10, FONT_G, SU_SCURO_3)], allinea="right"),
    ]


def piede(prefisso, testo_metodo, largo=12):
    """Sempre in fondo: da dove vengono i numeri e con che disciplina."""
    return [
        banda(prefisso + "-righello", MARGINE, PIEDE - 14, W(12), 1, 899, BORDO),
        testo(prefisso + "-piede", MARGINE, PIEDE, W(largo), 46, 900,
              [(testo_metodo, 9, FONT, INCHIOSTRO_3)]),
    ]


# =========================================================== LE PAGINE


def scrivi(percorso, oggetto):
    with io.open(percorso, "w", encoding="utf-8") as f:
        json.dump(oggetto, f, indent=2, ensure_ascii=False)


def distendi(elenco):
    """scheda() restituisce due visuali; qui la lista torna piatta."""
    fuori = []
    for e in elenco:
        fuori.extend(e if isinstance(e, list) else [e])
    return fuori


def pagina(nome, titolo_, visuali, spegni=(), tipo=None,
           larghezza=L, altezza=A, sfondo=SFONDO, nascosta=None, campo_ingresso=None):
    """spegni: coppie (sorgente, [bersagli]) per cui il clic sulla sorgente NON
    deve filtrare il bersaglio.

    Serve piu' di quanto sembri. Power BI incrocia i filtri fra visuali per
    impostazione predefinita: senza queste righe, chi clicca una fascia del
    grafico cambia i numeri dei riquadri in alto, mentre il testo scritto
    accanto resta quello di prima — e la pagina si contraddice da sola al primo
    clic. I riquadri sono la cornice fissa della pagina: si muovono con i filtri
    in alto, non con i clic sui grafici."""
    visuali = distendi(visuali)
    cartella = os.path.join(PAGINE, nome)
    os.makedirs(os.path.join(cartella, "visuals"), exist_ok=True)
    nomi = set(v["name"] for v in visuali)
    interazioni = []
    for sorgente, bersagli in spegni:
        for b in bersagli:
            assert sorgente in nomi, "%s: sorgente inesistente %s" % (nome, sorgente)
            assert b in nomi, "%s: bersaglio inesistente %s" % (nome, b)
            interazioni.append({"source": sorgente, "target": b, "type": "NoFilter"})
    corpo = {
        "$schema": S_PAG,
        "name": nome,
        "displayName": titolo_,
        "displayOption": "FitToPage",
        "height": altezza,
        "width": larghezza,
        "objects": {
            "background": [{"properties": {"color": _col(sfondo), "transparency": _lit("0D")}}],
            "outspace": [{"properties": {"color": _col(sfondo), "transparency": _lit("0D")}}],
        },
    }
    if tipo:
        corpo["type"] = tipo
        corpo["pageBinding"] = {"name": nome, "type": tipo}
    if nascosta if nascosta is not None else bool(tipo):
        corpo["visibility"] = "HiddenInViewMode"
    if campo_ingresso:
        # Il campo da cui si entra: Power BI ci deposita il valore del punto su
        # cui e' stato premuto il tasto destro. Il filtro sta sulla pagina, non
        # su una visuale, cosi' ci cascano dentro tutti i visuali insieme.
        tab_i, col_i = campo_ingresso
        espressione = {"Column": {"Expression": {"SourceRef": {"Entity": tab_i}},
                                  "Property": col_i}}
        corpo["filterConfig"] = {"filters": [{
            "name": "ingresso-" + nome,
            "field": espressione,
            "type": "Categorical",
            "howCreated": "Drillthrough",
        }]}
        corpo["pageBinding"]["parameters"] = [{
            "name": "ingresso-" + nome,
            "boundFilter": "ingresso-" + nome,
            "fieldExpr": espressione,
        }]
    if interazioni:
        corpo["visualInteractions"] = interazioni
    scrivi(os.path.join(cartella, "page.json"), corpo)
    for v in visuali:
        d = os.path.join(cartella, "visuals", v["name"])
        os.makedirs(d, exist_ok=True)
        scrivi(os.path.join(d, "visual.json"), v)


if os.path.isdir(PAGINE):
    shutil.rmtree(PAGINE)
os.makedirs(PAGINE)

# --------------------------------------------------------- I FILTRI
# Una fascia sola, sotto la testata e sopra il contenuto, uguale su tutte le
# pagine che ne hanno una. Sta sul fondo chiaro e non dentro la testata scura
# perche' un menu a discesa bianco su nero si legge male e va riverniciato tutto
# a mano: il posto giusto costa ottanta pixel di grafico e non costa nessun
# rischio.
FILTRI_Y, FILTRI_H = CIMA, 78
CORPO = FILTRI_Y + FILTRI_H + GRONDA                 # 282

GRUPPO_ANNO, GRUPPO_STATO = "anno-acquisto", "stato-cliente"

NOTA_FILTRI = ("I filtri valgono anche sulle altre pagine. I riquadri in alto non rispondono "
               "ai clic sui grafici: sono la cornice fissa della pagina.")


def filtri(prefisso, anno=True, nota=NOTA_FILTRI):
    """La fascia dei filtri. L'anno non c'e' sulla pagina della tendenza: li' i
    riquadri sono un confronto fra due anni fissi, e un filtro sull'anno che non
    li tocca sarebbe un comando che sembra fare qualcosa e non fa niente."""
    v = []
    i = 0
    if anno:
        v.append(filtro(prefisso + "-f-anno", X(0), FILTRI_Y, W(2), FILTRI_H, 5,
                        "Calendario", "Anno", "Anno d'acquisto", GRUPPO_ANNO))
        i = 2
    v.append(filtro(prefisso + "-f-stato", X(i), FILTRI_Y, W(2), FILTRI_H, 6,
                    "Clienti", "stato", "Stato del cliente", GRUPPO_STATO))
    v.append(testo(prefisso + "-nota-filtri", X(8), FILTRI_Y + 12, W(4), 44, 7,
                   [(nota, 9, FONT, INCHIOSTRO_3)], allinea="right"))
    return v


# ------------------------------------------------- IL RIQUADRO DI DETTAGLIO
# Una pagina fuori misura, nascosta, che compare sotto il mouse sul grafico
# delle fasce con addosso il filtro del punto puntato.
#
# Serve a rispondere alla domanda «e allora cosa faccio, ci clicco sopra?».
# Sul grafico delle fasce un clic non ha dove andare: gli unici altri visuali
# della pagina sono i riquadri, che sono la cornice fissa e non si devono
# muovere. Il riquadro di dettaglio da' al puntatore un posto dove andare senza
# spostare niente di quello che sta scritto intorno.
#
# Le quattro voci scendono tutte da Ordini o da RigheOrdine, cioe' da dove
# arriva il filtro della fascia: nessuna resta ferma fingendo di aver risposto.
DET_L, DET_A, DET_M, DET_RIGA = 380, 424, 16, 66
DET_W = DET_L - 2 * DET_M
DET_Y = 96

pagina("dettaglio-fascia", "Dettaglio della fascia", [
    _numero("det-fascia", DET_M, 14, DET_W, 60, 1, "fascia_ritardo", 14, ROSSO,
            tabella="Ordini", colonna=True),
    banda("det-filo", DET_M, 84, DET_W, 1, 2, BORDO),

    riga_valore("det-r1", DET_M, DET_Y, DET_W, 10,
                "Ordini consegnati", "Ordini consegnati"),
    riga_valore("det-r2", DET_M, DET_Y + DET_RIGA, DET_W, 12,
                "Voto medio", "Voto medio"),
    riga_valore("det-r3", DET_M, DET_Y + 2 * DET_RIGA, DET_W, 14,
                "Recensioni negative", "% recensioni negative"),
    riga_valore("det-r4", DET_M, DET_Y + 3 * DET_RIGA, DET_W, 16,
                "Fatturato", "Fatturato (EUR)"),

    testo("det-nota", DET_M, DET_Y + 4 * DET_RIGA + 6, DET_W, 44, 20,
          [("Ordini e fatturato sui consegnati; voto e recensioni sui recensiti.",
            8, FONT, INCHIOSTRO_3)]),
], tipo="Tooltip", larghezza=DET_L, altezza=DET_A, sfondo=CARTA)


# --------------------------------------------------------- 1. LA DOMANDA
# I riquadri crescono da 150 a 210: l'etichetta ha bisogno della sua fascia con
# un margine sopra, e il grafico di quello spazio non aveva bisogno.
RIQ_Y, RIQ_H = CORPO, 152                            # 282 .. 434
DID_Y = RIQ_Y + RIQ_H + 6                            # 440
GRA_Y = DID_Y + 60                                   # 500
P1_SCH_H = 326                                       # 500 .. 826
VOTI_Y = GRA_Y + P1_SCH_H + GRONDA                   # 850
MEZZA = W(2)                                         # 284: mezza colonna da quattro

pagina("la-domanda", "1. La domanda", intestazione(
    "p1", "I ritardi di consegna quanto ci costano in recensioni negative?",
    "Marketplace Olist, Brasile. 96.470 ordini consegnati fra settembre 2016 e ottobre 2018. "
    "Dati Kaggle, licenza CC BY-NC-SA 4.0.",
    "LA DOMANDA", "PAGINA 1 DI 4") + filtri("p1") + [

    riquadro("p1-c1", X(0), RIQ_Y, W(3), RIQ_H, 10, "% ordini in ritardo",
             "Consegnati dopo la data promessa"),
    riquadro("p1-c2", X(3), RIQ_Y, W(3), RIQ_H, 11, "% recensioni negative in orario",
             "Recensioni negative, consegne in orario"),
    riquadro("p1-c3", X(6), RIQ_Y, W(3), RIQ_H, 12, "% recensioni negative in ritardo",
             "Recensioni negative, consegne in ritardo", accento=True),
    riquadro("p1-c4", X(9), RIQ_Y, W(3), RIQ_H, 13, "Fatturato in ritardo (EUR)",
             "Fatturato che passa da ordini in ritardo"),

    didascalia("p1-d1", X(0), DID_Y, W(3), 14, "Base: 96.470 ordini consegnati."),
    didascalia("p1-d2", X(3), DID_Y, W(3), 15, "Base: 95.824 ordini anche recensiti."),
    didascalia("p1-d3", X(6), DID_Y, W(3), 16, "Stessa base, solo gli ordini oltre la promessa."),
    # il quarto riquadro e' l'unico che porta un valore assoluto: da solo non si
    # sa se sia molto o poco, e la quota che serve a saperlo viene dal modello
    didascalia_misura("p1-d4", X(9), DID_Y, W(3), 17, "% fatturato in ritardo",
                      "del fatturato consegnato."),

    barre("p1-dirupo", X(0), GRA_Y, W(8), FONDO - GRA_Y, 20,
          ("Ordini", "fascia_ritardo"),
          [("% negative (consegne in orario)", GRIGIO),
           ("% negative (consegne in ritardo)", ROSSO)],
          "Recensioni negative per fascia: in grigio le consegne in orario, "
          "in rosso quelle oltre la promessa",
          forma="fasce", dim_categoria=11,
          dettaglio="dettaglio-fascia"),

    scheda("p1-lettura", X(8), GRA_Y, W(4), P1_SCH_H, 21,
           "Il salto sta nei primi giorni di ritardo", [
               "Fra dieci giorni di anticipo e la consegna appena in orario le recensioni "
               "negative passano dall'8,9% all'11,0%. Due punti su venti giorni di scarto.",
               "",
               ("Fra 3 e 7 giorni di ritardo si arriva al 61,3%: la maggioranza delle "
                "recensioni e' negativa.", "rosso"),
               "",
               ("Perche' non c'e' un coefficiente di correlazione", "forte"),
               "Calcolato su tutti gli ordini varrebbe -0,18, cioe' un legame debole. Il valore "
               "e' schiacciato dal 92% di consegne in anticipo, che domina il conteggio. Per "
               "questo la pagina mostra le fasce.",
           ], dim=11),

    # il crollo del voto e' il numero che regge tutto il lavoro: stava scritto
    # nei documenti e da nessuna parte nel cruscotto
    riquadro("p1-voto1", X(8), VOTI_Y, MEZZA, FONDO - VOTI_Y, 22, "Voto medio in orario",
             "Voto, consegne in orario", dim=30),
    riquadro("p1-voto2", X(10), VOTI_Y, MEZZA, FONDO - VOTI_Y, 23, "Voto medio in ritardo",
             "Voto, consegne in ritardo", dim=30),
] + piede("p1",
          "Dati Olist (Kaggle, CC BY-NC-SA 4.0), scaricati e congelati il 23/08/2026. "
          "Ordini consegnati: 96.470 su 99.441. I voti si appoggiano ai 95.824 ordini anche "
          "recensiti. Le due basi sono diverse e ogni misura dichiara la propria. Gli importi "
          "sono convertiti da reais a euro a " + costante("Cambio reais per euro") +
          ", media dei cambi mensili BCE del periodo pesata per il fatturato: convertendo "
          "mese per mese il totale cambia dello 0,5%."),
    spegni=[("p1-dirupo", ["p1-c1-numero", "p1-c2-numero", "p1-c3-numero", "p1-c4-numero",
                           "p1-d4-numero", "p1-voto1-numero", "p1-voto2-numero"])],
)

# ------------------------------------------------ 2. DI CHI E' IL RITARDO
# Il grafico delle fasi ha due sole barre: in 396 pixel stavano in mezzo a un
# riquadro mezzo vuoto. Scende a 224, e i pixel liberati vanno al grafico degli
# stati, che di righe ne ha quattordici.
R1_Y, R1_H = CORPO, 202                              # 282 .. 484
R2_Y = R1_Y + R1_H + GRONDA                          # 508
KPI_H = 140
RIGA_B = R2_Y + KPI_H + GRONDA                       # 672
SOG_Y = RIGA_B + KPI_H + GRONDA                      # 836

pagina("di-chi-e-il-ritardo", "2. Di chi e' il ritardo", intestazione(
    "p2", "Il ritardo si forma quasi tutto dopo il venditore.",
    "Sugli ordini in ritardo il venditore impiega 1,2 giorni in piu' del solito, la logistica 17. "
    "La pagina scompone il tempo di consegna nelle due fasi che i dati registrano.",
    "DI CHI E' IL RITARDO", "PAGINA 2 DI 4") + filtri("p2", nota=(
        "I filtri valgono anche sulle altre pagine. Il clic su uno stato muove i due "
        "riquadri sui venditori; le mediane restano ferme, il filtro non le raggiunge.")) + [

    # impilate: le due fasi sono i pezzi di una sola durata, e impilandole si
    # legge anche il totale
    barre("p2-fasi", X(0), R1_Y, W(6), R1_H, 10,
          ("Ordini", "esito_consegna"),
          [("Fase venditore (mediana)", GRIGIO),
           ("Fase logistica (mediana)", ROSSO)],
          "Giorni mediani per fase della consegna",
          forma="fasce", legenda=True, dim_categoria=12, interno=12),

    scheda("p2-lettura", X(6), R1_Y, W(6), R1_H, 11,
           "Come si forma il ritardo", [
               "Due intervalli registrati: dall'approvazione al corriere (venditore), e da "
               "li' alla consegna (logistica).",
               "",
               ("In orario: 1,8 giorni il venditore, 6,9 la logistica.", "forte"),
               ("In ritardo: 3,0 il venditore, 23,9 la logistica.", "rosso"),
               "",
               "I conti tornano: 1,2 piu' 17,0 fanno 18,2; tolto il margine di 12,3 restano "
               "5,9 attesi contro 5,8 misurati.",
           ], dim=11),

    # orizzontale e ordinata: e' una classifica, e le sigle degli stati si
    # leggono diritte invece che ruotate di novanta gradi
    barre("p2-stati", X(0), R2_Y, W(8), FONDO - R2_Y, 12,
          ("Venditori", "stato"), [("% ritardo dello stato", ROSSO)],
          "Ritardo per stato del venditore: la geografia spiega piu' del singolo venditore",
          forma="classifica", ordina=("% ritardo dello stato", "Descending")),

    riquadro("p2-c1", X(8), R2_Y, MEZZA, KPI_H, 13, "Venditori misurati",
             "Venditori con consegne", dim=30),
    riquadro("p2-c2", X(10), R2_Y, MEZZA, KPI_H, 14, "Venditori sopra soglia",
             "Sopra i 30 ordini consegnati", dim=30),
    riquadro("p2-c3", X(8), RIGA_B, MEZZA, KPI_H, 15, "Giorni di ritardo (mediana)",
             "Ritardo mediano, in giorni", dim=30),
    riquadro("p2-c4", X(10), RIGA_B, MEZZA, KPI_H, 16, "Margine di consegna (mediana)",
             "Anticipo mediano, in giorni", dim=30),

    scheda("p2-soglia", X(8), SOG_Y, W(4), FONDO - SOG_Y, 17,
           "Perche' la soglia sta a 30 ordini", [
               "Sotto i 30 ordini la percentuale e' rumore: 3 ordini, 100% di ritardo.",
               ("I venditori esclusi non sono a posto: sono non misurabili.", "forte"),
               "",
               "1.390 venditori su 2.970 fanno almeno un ritardo; i venti peggiori il 24%.",
           ]),
] + piede("p2",
          "Il grafico per stato tiene solo gli stati con almeno 100 ordini consegnati. Le durate "
          "per fase escludono 1.388 ordini con timestamp incoerenti, contati a parte. Il ritardo "
          "per stato si appoggia alle righe d'ordine, perche' il filtro dello stato del venditore "
          "non risale fino alla tabella degli ordini: per lo stesso motivo il filtro in alto e' "
          "sullo stato del cliente, che invece ci arriva."),
    spegni=[
        ("p2-fasi", ["p2-c1-numero", "p2-c2-numero", "p2-c3-numero", "p2-c4-numero",
                     "p2-stati"]),
        # il clic su uno stato filtra le righe d'ordine ma non gli ordini: sul
        # grafico delle fasi non cambierebbe niente, e un grafico che non
        # risponde sembra un grafico che dice "nessuna differenza"
        # NB: p2-c1 e p2-c2 NON sono qui. Contano venditori, il filtro dello
        # stato arriva ai venditori, e il clic su uno stato li muove come deve.
        # Fermi restano solo i due riquadri sulle mediane, che scendono dagli
        # ordini e da un filtro sul venditore non sarebbero raggiunti.
        ("p2-stati", ["p2-c3-numero", "p2-c4-numero", "p2-fasi"]),
    ],
)

# ------------------------------------------------------- 3. COME CAMBIA
# La pagina che mancava. Le prime due dicono quanto costa il ritardo e da dove
# viene, tutte e due su tutto il periodo insieme: nessuna delle due risponde
# alla prima domanda che fa chi deve decidere, cioe' se la cosa sta migliorando
# o peggiorando. Il calendario per rispondere c'era gia'.
P3_GRA_H = 236                                       # 500 .. 736
P3_SCH_Y = GRA_Y + P3_GRA_H + GRONDA                 # 760

pagina("come-cambia", "3. Come cambia", intestazione(
    "p3", "Il ritardo e' piu' che raddoppiato in un anno.",
    "Gennaio-agosto 2018 contro lo stesso periodo del 2017: dal 4,2% al 9,4% di consegne oltre "
    "la promessa, e le recensioni negative dal 10,5% al 13,3%.",
    "COME CAMBIA", "PAGINA 3 DI 4") + filtri("p3", anno=False) + [

    riquadro("p3-c1", X(0), RIQ_Y, W(3), RIQ_H, 10, "% ordini in ritardo gen-ago 2018",
             "Consegne in ritardo, gen-ago 2018", accento=True),
    riquadro("p3-c2", X(3), RIQ_Y, W(3), RIQ_H, 11, "% ordini in ritardo gen-ago 2017",
             "Stesso periodo dell'anno prima"),
    riquadro("p3-c3", X(6), RIQ_Y, W(3), RIQ_H, 12, "% recensioni negative gen-ago 2018",
             "Recensioni negative, gen-ago 2018"),
    riquadro("p3-c4", X(9), RIQ_Y, W(3), RIQ_H, 13, "% recensioni negative gen-ago 2017",
             "Stesso periodo dell'anno prima"),

    didascalia("p3-d1", X(0), DID_Y, W(3), 14, "52.777 ordini consegnati."),
    didascalia("p3-d2", X(3), DID_Y, W(3), 15, "21.997: il marketplace e' cresciuto."),
    didascalia("p3-d3", X(6), DID_Y, W(3), 16, "Base: i soli ordini anche recensiti."),
    didascalia("p3-d4", X(9), DID_Y, W(3), 17, "Stessa base, stessa finestra."),

    barre("p3-tendenza", X(0), GRA_Y, W(8), FONDO - GRA_Y, 20,
          ("Calendario", "Etichetta mese"),
          [("% ordini in ritardo (mese)", ROSSO),
           ("% ordini in ritardo (anno prec.)", GRIGIO)],
          "Consegne oltre la promessa, per mese d'acquisto",
          forma="linee", legenda=True, dim_categoria=10,
          etichette=False, asse_valori=True),

    barre("p3-negative", X(8), GRA_Y, W(4), P3_GRA_H, 21,
          ("Calendario", "Etichetta mese"),
          [("% recensioni negative (mese)", ROSSO),
           ("% recensioni negative (anno prec.)", GRIGIO)],
          "Recensioni negative, per mese",
          forma="linee", legenda=True, dim_categoria=9,
          etichette=False, asse_valori=True),

    scheda("p3-lettura", X(8), P3_SCH_Y, W(4), FONDO - P3_SCH_Y, 22,
           "Sono picchi, non una deriva", [
               "Nel 2017 sta sotto il 4%. Poi 14,3% a novembre e 21,4% a marzo 2018.",
               "Giugno 2018 torna all'1,4%.",
               "",
               ("Si risolve con la capacita', non sospendendo venditori.", "rosso"),
               "",
               ("Perche' la grigia comincia dal 2018", "forte"),
               "L'anno prima esiste solo dentro il periodo utile.",
           ], dim=11),
] + piede("p3",
          "Il mese e' quello dell'acquisto: la relazione attiva fra Ordini e Calendario e' su "
          "data_acquisto. La serie vive su gennaio 2017 - agosto 2018, e fuori da quella "
          "finestra le misure restano vuote e il mese non compare sull'asse. I quattro riquadri "
          "sono un confronto fra due finestre fisse: il filtro sullo stato li tocca, un filtro "
          "sull'anno no, ed e' il motivo per cui su questa pagina non c'e'."),
    spegni=[
        ("p3-tendenza", ["p3-c1-numero", "p3-c2-numero", "p3-c3-numero", "p3-c4-numero",
                         "p3-negative"]),
        ("p3-negative", ["p3-c1-numero", "p3-c2-numero", "p3-c3-numero", "p3-c4-numero",
                         "p3-tendenza"]),
    ],
)

# ----------------------------------------------------- 4. COSA NON DICE
# Le schede dei limiti si stringono da 252 a 216 per lasciare 340 pixel alla
# tabella: con 268 mostrava sei degli otto stati e le ultime due righe si
# raggiungevano solo scorrendo. Una tabella che scorre dentro un cruscotto e'
# una tabella che nessuno legge fino in fondo.
# La tabella degli otto stati scorreva anche a 320 pixel: le righe di tableEx
# sono piu' alte di quanto stimassi. Invece di stringere ancora le schede, la
# tabella passa nella colonna di destra e prende l'altezza di due file, 512
# pixel. Le schede dei limiti diventano tre per fila invece di quattro, e le
# ultime due scendono nella fascia in basso accanto alla nota.
# Misurato sul file aperto: la tabella riempie 320 pixel e ne aveva 512, quindi
# ne restavano quasi duecento vuoti sotto l'ultima riga. Adesso la pagina e' una
# griglia 3x3 di schede a sinistra (otto limiti piu' la nota) e una colonna a
# destra con la tabella e i due riquadri.
# Questa pagina non ha la fascia dei filtri: i suoi numeri sono il verbale di
# cosa entra e cosa esce dall'analisi, e un verbale filtrato non e' un verbale.
FILE_Y = [CIMA, 454, 728]                           # 180, 454, 728
FILE_H = [250, 250, FONDO - 728]                    # 250, 250, 272
TAB_H  = 376                                        # titolo, intestazione e otto righe
P4_KPI_Y = CIMA + TAB_H + GRONDA                    # 580
P4_KPI_H = (FONDO - P4_KPI_Y - GRONDA) // 2         # 214

LIMITI = [
    ("Correlazione e causa",
     ["Un coefficiente su tutti gli ordini varrebbe -0,18, cioe' un legame debole: il valore "
      "e' schiacciato dal 92% di consegne in anticipo. Per questo la pagina 1 mostra le fasce.",
      "",
      "Ritardo e recensione bassa possono anche avere la stessa origine: un venditore lento "
      "puo' essere anche scadente."]),
    ("La recensione non misura il danno economico",
     ["Da questi dati non si puo' sapere se un cliente con una stella ha smesso di comprare. "
      "Ci sono 96.096 persone per 99.441 ordini: il 97% compra una volta sola, e non c'e' un "
      "comportamento successivo da osservare."]),
    ("«In ritardo» e' rispetto a una promessa",
     ["Quando un ordine arriva in orario, arriva 12,3 giorni prima della data promessa "
      "(mediana). Allargando la stima il ritardo sparirebbe dai numeri senza che nessuno "
      "consegni prima, e questa analisi non se ne accorgerebbe."]),
    ("Le fasi arrivano fin dove arrivano i timestamp",
     ["Quello che succede dentro il corriere non e' registrato. Su 1.388 ordini i timestamp "
      "sono incoerenti, con la spedizione prima dell'approvazione: quegli ordini sono esclusi "
      "dalle misure per fase e contati a parte."]),
    ("Nel report convivono due basi di calcolo",
     ["96.470 ordini consegnati per i tempi e i venditori, 95.824 anche recensiti per i voti. "
      "Ogni misura dichiara la propria base.",
      "",
      ("Confonderle produce numeri plausibili e sbagliati.", "forte")]),
    ("1.278 ordini hanno piu' di un venditore",
     ["Il ritardo appartiene all'ordine, il venditore alla riga d'ordine. Attribuire il ritardo "
      "a tutti i venditori dell'ordine lo conta piu' volte: le coppie venditore-ordine sono "
      "97.811 contro 96.470 ordini."]),
    ("Manca il costo dell'intervento",
     ["L'analisi dice quanto fatturato passa dagli ordini in ritardo, non quanto costerebbe "
      "ridurli.",
      "",
      ("Senza quel dato non si puo' scegliere se e quanto investire.", "forte")]),
    ("Il mese e' quello dell'acquisto",
     ["La pagina 3 aggancia gli ordini al calendario per data d'acquisto, che e' la relazione "
      "attiva del modello. Un ordine comprato a fine febbraio e consegnato in ritardo a marzo "
      "pesa su febbraio.",
      "",
      "Il periodo utile e' gennaio 2017 - agosto 2018: il 2016 conta 329 ordini in tutto, "
      "novembre 2016 e' assente, e settembre-ottobre 2018 sono venti ordini di coda del dump."]),
]

POSTI = [(X(3 * (i % 3)), FILE_Y[i // 3], FILE_H[i // 3]) for i in range(9)]

schede_limiti = [
    scheda("p4-l%d" % (i + 1), px, py, W(3), ph, 10 + i, t, corpo)
    for i, ((px, py, ph), (t, corpo)) in enumerate(zip(POSTI, LIMITI))
]

pagina("cosa-non-dice", "4. Cosa NON dice", intestazione(
    "p4", "Cosa questa analisi NON dice",
    "Ogni numero di questa pagina e' misurato sugli stessi dati dell'analisi. I limiti stanno "
    "qui perche' condizionano il modo in cui si leggono le prime tre pagine.",
    "I LIMITI", "PAGINA 4 DI 4") + schede_limiti + [

    tabella("p4-esclusi", X(9), CIMA, W(3), TAB_H, 30,
            [("ControlloStatiOrdine", "Stato dell'ordine"),
             ("ControlloStatiOrdine", "Ordini")],
            "Cosa entra nell'analisi",
            ordina=("ControlloStatiOrdine", "Ordini", "Descending"),
            larghezze=(216, 132)),

    scheda("p4-nota", POSTI[8][0], POSTI[8][1], W(3), POSTI[8][2], 31,
           "Come leggere la tabella", [
               "2.963 ordini non sono mai arrivati: annullati, non disponibili o ancora in "
               "viaggio. Piu' otto consegnati senza data di consegna.",
               "",
               ("Un venditore che fa annullare un ordine invece di consegnarlo in ritardo, "
                "qui risulta migliore.", "rosso"),
               "",
               "I numeri non sono battuti a mano: vengono da una tabella del modello. Se i "
               "dati cambiano, cambiano anche loro.",
           ]),

    riquadro("p4-c1", X(9), P4_KPI_Y, W(3), P4_KPI_H, 32, "Ordini esclusi dall'analisi",
             "Ordini mai arrivati", dim=30),
    riquadro("p4-c2", X(9), FONDO - P4_KPI_H, W(3), P4_KPI_H, 33, "Coppie venditore-ordine",
             "Contro 96.470 ordini", dim=30),
] + piede("p4",
          "Ogni numero e' riconciliato fra il calcolo di esplorazione in Python e il modello "
          "Power BI. Dove i due non coincidevano e' stata corretta la documentazione, tenendo "
          "il valore misurato."),
    spegni=[("p4-esclusi", ["p4-c1-numero", "p4-c2-numero"])],
)

# ------------------------------------------------------- 5. DENTRO UN MESE
# La pagina 3 dice che marzo 2018 fa il 21,4% e giugno l'1,4%, e a quel punto la
# domanda successiva e' sempre la stessa: e allora cosa e' successo a marzo?
# Fino a ieri non c'era modo di chiederlo.
#
# Ci si arriva col tasto destro su un mese della pagina 3 (drillthrough): Power
# BI deposita il mese scelto nel filtro d'ingresso, che sta sulla pagina e non su
# una visuale, cosi' ci cascano dentro tutti i visuali insieme.
#
# La pagina NON e' nascosta, ed e' una scelta. Una pagina di drillthrough
# nascosta ha un solo modo di uscire, il pulsante Indietro, che Power BI mette
# da se' solo quando la pagina la costruisci nell'interfaccia — scrivendo il
# JSON non c'e', e chi entra resta chiuso dentro. Lasciandola visibile si esce
# dalla linguetta, e aperta da li' mostra tutto il periodo: e' una lettura che
# ha senso lo stesso.
#
# Le due misure per fase sono le stesse di pagina 2, ristrette al mese: sono
# quelle che rispondono davvero, perche' dicono se quel mese e' stato il
# venditore o la logistica.
M5_RIQ_H = 168                                       # 180 .. 348
M5_DID_Y = CIMA + M5_RIQ_H + 6                       # 354
M5_GRA_Y = M5_DID_Y + 44                             # 398
M5_H = FONDO - M5_GRA_Y                              # 602

pagina("dentro-un-mese", "5. Dentro un mese", intestazione(
    "p5", "Dentro un mese",
    "Col tasto destro su un mese della pagina 3 la pagina si apre su quel mese. Le due "
    "domande sono: quanto era lungo il ritardo, e da quale fase arrivava.",
    "DETTAGLIO", "DA UN MESE DELLA PAGINA 3") + [

    riquadro("p5-c1", X(0), CIMA, W(3), M5_RIQ_H, 10, "% ordini in ritardo",
             "Consegne oltre la promessa", accento=True),
    riquadro("p5-c2", X(3), CIMA, W(3), M5_RIQ_H, 11, "Ordini consegnati",
             "Ordini consegnati"),
    riquadro("p5-c3", X(6), CIMA, W(3), M5_RIQ_H, 12, "% recensioni negative",
             "Recensioni negative"),
    riquadro("p5-c4", X(9), CIMA, W(3), M5_RIQ_H, 13, "Fatturato (EUR)",
             "Fatturato consegnato"),

    didascalia("p5-d1", X(0), M5_DID_Y, W(3), 14, "Sul mese d'acquisto."),
    didascalia("p5-d2", X(3), M5_DID_Y, W(3), 15, "Base dei tempi."),
    didascalia("p5-d3", X(6), M5_DID_Y, W(3), 16, "Base dei soli ordini recensiti."),
    didascalia("p5-d4", X(9), M5_DID_Y, W(3), 17, "Somma delle righe d'ordine."),

    barre("p5-fasce", X(0), M5_GRA_Y, W(5), M5_H, 20,
          ("Ordini", "fascia_ritardo"), [("Ordini consegnati", ROSSO)],
          "Quanto era lungo: ordini per fascia",
          forma="fasce", dim_categoria=11),

    barre("p5-fasi", X(5), M5_GRA_Y, W(4), M5_H, 21,
          ("Ordini", "esito_consegna"),
          [("Fase venditore (mediana)", GRIGIO),
           ("Fase logistica (mediana)", ROSSO)],
          "Da dove arrivava: giorni mediani per fase",
          forma="fasce", legenda=True, dim_categoria=12, interno=12),

    scheda("p5-lettura", X(9), M5_GRA_Y, W(3), M5_H, 22,
           "Come si legge", [
               "Il grafico a sinistra dice se il mese ha prodotto molti ritardi corti o pochi "
               "ritardi lunghi. Sono due problemi diversi e si affrontano in modo diverso.",
               "",
               "Quello accanto dice da quale delle due fasi arrivava il tempo, con le stesse "
               "due misure della pagina 2 ristrette al mese.",
               "",
               ("Se in un mese cattivo si allunga solo la fase logistica, quel mese non e' un "
                "problema di venditori.", "forte"),
               "",
               "Restano fuori gli ordini a cronologia incoerente, come in pagina 2.",
           ], dim=11),
] + piede("p5",
          "Il mese e' quello dell'acquisto. I quattro riquadri e il grafico delle fasce "
          "girano sui consegnati, le recensioni negative sui soli recensiti, e le due "
          "mediane per fase escludono gli ordini con timestamp incoerenti. Senza un mese "
          "selezionato la pagina mostra tutto il periodo."),
    campo_ingresso=("Calendario", "Etichetta mese"),
    tipo="Drillthrough",
    nascosta=False,
    spegni=[
        ("p5-fasce", ["p5-c1-numero", "p5-c2-numero", "p5-c3-numero", "p5-c4-numero",
                      "p5-fasi"]),
        ("p5-fasi", ["p5-c1-numero", "p5-c2-numero", "p5-c3-numero", "p5-c4-numero",
                     "p5-fasce"]),
    ],
)

# --------------------------------------------------------- l'indice pagine
ordine = ["la-domanda", "di-chi-e-il-ritardo", "come-cambia", "cosa-non-dice",
          "dentro-un-mese", "dettaglio-fascia"]
scrivi(os.path.join(PAGINE, "pages.json"), {
    "$schema": S_PAGS,
    "pageOrder": ordine,
    "activePageName": ordine[0],
})

n = sum(len(os.listdir(os.path.join(PAGINE, p, "visuals"))) for p in ordine)
print("scritte %d pagine, %d visuali" % (len(ordine), n))
