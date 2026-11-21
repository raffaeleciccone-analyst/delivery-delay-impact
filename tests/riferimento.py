# I passaggi di Power Query rifatti in pandas, con gli stessi nomi (PIANO.md §2).
#
# Serve ai test: i numeri del cruscotto (SPEC C1-C8, C15-C19) si ricalcolano dai CSV
# senza aprire Power BI. Se questo file e Power BI danno numeri diversi, si cerca il
# passaggio che si comporta diversamente: non si aggiusta il numero atteso.
import os

import pandas as pd


def _csv(cartella, nome, **kw):
    return pd.read_csv(os.path.join(cartella, nome), **kw)


def ordini_grezzi(cartella):
    """01-OrdiniGrezzi.m: gli ordini come stanno nel file."""
    date = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
            "order_delivered_customer_date", "order_estimated_delivery_date"]
    return _csv(cartella, "olist_orders_dataset.csv", parse_dates=date)


def recensioni_per_ordine(cartella):
    """05-RecensioniPerOrdine.m: una riga per ordine, voto = media dei punteggi."""
    r = _csv(cartella, "olist_order_reviews_dataset.csv",
             parse_dates=["review_creation_date", "review_answer_timestamp"])
    g = r.groupby("order_id").agg(
        voto=("review_score", "mean"),
        recensioni_sull_ordine=("review_score", "size"),
        prima_risposta=("review_answer_timestamp", "min"),
    ).reset_index()
    # Negativa = 1 o 2 stelle: la soglia è una scelta e va detta
    g["voto_negativo"] = g["voto"] <= 2
    return g


def righe_ordine(cartella):
    """04-RigheOrdine.m: il fatturato sta qui (prezzo + spedizione)."""
    r = _csv(cartella, "olist_order_items_dataset.csv")
    r["valore_riga"] = r["price"] + r["freight_value"]
    return r


def conteggi_scartati(cartella):
    """§1 e §2 di DATI-SPORCHI.md: quanti ordini restano fuori, e perché."""
    o = ordini_grezzi(cartella)
    consegnati = o["order_status"] == "delivered"
    return {
        "non_consegnati": int((~consegnati).sum()),
        "consegnati_senza_data": int((consegnati & o["order_delivered_customer_date"].isna()).sum()),
    }


# ------------------------------------------------------------ la distanza (F10)
# Confini del Brasile: gli stessi quattro numeri di power-query/11-CoordinateCAP.m (PIANO §3)
LAT_MIN, LAT_MAX = -33.75, 5.27
LNG_MIN, LNG_MAX = -73.99, -34.79
RAGGIO_KM = 6371.0
FASCE_KM = [(100, "Sotto 100 km"), (500, "100-500 km"), (1000, "500-1.000 km"),
            (2000, "1.000-2.000 km"), (float("inf"), "Oltre 2.000 km")]
NON_CALCOLABILE = "Distanza non calcolabile"


def distanza_km(lat1, lng1, lat2, lng2):
    """Distanza in linea d'aria (formula dell'emisenoverso). Accetta numeri o colonne."""
    import numpy as np
    f1, f2 = np.radians(lat1), np.radians(lat2)
    df, dl = f2 - f1, np.radians(lng2) - np.radians(lng1)
    a = np.sin(df / 2) ** 2 + np.cos(f1) * np.cos(f2) * np.sin(dl / 2) ** 2
    return 2 * RAGGIO_KM * np.arcsin(np.sqrt(a))


def un_punto_per_cap(geo):
    """§9: scarta i punti fuori dal Brasile, poi un punto per CAP (mediana di lat e lng)."""
    dentro = geo["geolocation_lat"].between(LAT_MIN, LAT_MAX) & geo["geolocation_lng"].between(LNG_MIN, LNG_MAX)
    g = geo[dentro].groupby("geolocation_zip_code_prefix").agg(
        lat=("geolocation_lat", "median"), lng=("geolocation_lng", "median")).reset_index()
    return g.rename(columns={"geolocation_zip_code_prefix": "cap"})


def coordinate_cap(cartella):
    return un_punto_per_cap(_csv(cartella, "olist_geolocation_dataset.csv"))


def cap_senza_coordinate(cartella):
    noti = set(coordinate_cap(cartella)["cap"])
    clienti = set(_csv(cartella, "olist_customers_dataset.csv")["customer_zip_code_prefix"])
    venditori = set(_csv(cartella, "olist_sellers_dataset.csv")["seller_zip_code_prefix"])
    return {"clienti": len(clienti - noti), "venditori": len(venditori - noti)}


def distanza_per_ordine(cliente, venditori):
    """Una distanza per ordine: quella del venditore più lontano (C19)."""
    v = venditori.merge(cliente, on="order_id", how="inner")
    v["distanza_km"] = distanza_km(v["lat_cliente"], v["lng_cliente"], v["lat_venditore"], v["lng_venditore"])
    # se manca una coordinata la distanza resta vuota, e vuota resta per tutto l'ordine
    return v.groupby("order_id")["distanza_km"].max(skipna=False).reset_index()


def fascia_distanza(km):
    if km != km:  # NaN
        return NON_CALCOLABILE
    for limite, nome in FASCE_KM:
        if km < limite:
            return nome
    return FASCE_KM[-1][1]


def aggiungi_distanza(o, cartella):
    punti = coordinate_cap(cartella)
    clienti = _csv(cartella, "olist_customers_dataset.csv")[["customer_id", "customer_zip_code_prefix"]]
    clienti = clienti.merge(punti, left_on="customer_zip_code_prefix", right_on="cap", how="left")
    cliente = o[["order_id", "customer_id"]].merge(clienti, on="customer_id", how="left")
    cliente = cliente.rename(columns={"lat": "lat_cliente", "lng": "lng_cliente"})[
        ["order_id", "lat_cliente", "lng_cliente"]]

    vend = _csv(cartella, "olist_sellers_dataset.csv")[["seller_id", "seller_zip_code_prefix"]]
    vend = vend.merge(punti, left_on="seller_zip_code_prefix", right_on="cap", how="left")
    righe = _csv(cartella, "olist_order_items_dataset.csv")[["order_id", "seller_id"]].drop_duplicates()
    venditori = righe.merge(vend, on="seller_id", how="left").rename(
        columns={"lat": "lat_venditore", "lng": "lng_venditore"})[["order_id", "lat_venditore", "lng_venditore"]]

    o = o.merge(distanza_per_ordine(cliente, venditori), on="order_id", how="left")
    o["fascia_distanza"] = o["distanza_km"].map(fascia_distanza)
    return o


def costruisci_ordini(cartella):
    """02-Ordini.m: tabella dei fatti, un ordine consegnato."""
    o = ordini_grezzi(cartella)

    # Tieni solo gli ordini consegnati / Scarta i consegnati senza data di consegna
    o = o[o["order_status"] == "delivered"]
    o = o[o["order_delivered_customer_date"].notna()].copy()

    # Giorni di ritardo: si confrontano due DATE, non due istanti (§4b)
    o["consegna"] = o["order_delivered_customer_date"]
    o["giorni_ritardo"] = (o["consegna"].dt.normalize()
                           - o["order_estimated_delivery_date"].dt.normalize()).dt.days
    o["in_ritardo"] = o["giorni_ritardo"] > 0

    # Fascia di ritardo: gli stessi tagli di 02-Ordini.m (-10, -5, 0, 3, 7, 15, 30)
    tagli = [(-10, "10 gg o più in anticipo"), (-5, "5-9 gg in anticipo"), (0, "0-4 gg in anticipo"),
             (3, "1-3 gg di ritardo"), (7, "4-7 gg di ritardo"), (15, "8-15 gg di ritardo"),
             (30, "16-30 gg di ritardo")]
    def fascia(g):
        for limite, nome in tagli:
            if g <= limite:
                return nome
        return "Oltre 30 gg di ritardo"
    o["fascia_ritardo"] = o["giorni_ritardo"].map(fascia)

    # Le due fasi: venditore e corriere (sotto-domanda 5)
    giorno = pd.Timedelta(days=1)
    o["giorni_fase_venditore"] = (o["order_delivered_carrier_date"] - o["order_approved_at"]) / giorno
    o["giorni_fase_logistica"] = (o["order_delivered_customer_date"] - o["order_delivered_carrier_date"]) / giorno

    # §3 - Marca la cronologia incoerente (si marca, non si cancella)
    o["cronologia_ok"] = (o["giorni_fase_venditore"].notna() & o["giorni_fase_logistica"].notna()
                          & (o["giorni_fase_venditore"] >= 0) & (o["giorni_fase_logistica"] >= 0))

    o["data_acquisto"] = o["order_purchase_timestamp"].dt.normalize()

    # Aggancia il voto della recensione
    o = o.merge(recensioni_per_ordine(cartella), on="order_id", how="left")
    o["recensito"] = o["voto"].notna()
    o["voto_negativo"] = o["voto_negativo"].fillna(False).astype(bool)

    # §16 - Recensione prima del pacco: la PRIMA risposta contro l'istante di consegna
    o["recensione_prima_del_pacco"] = (o["recensito"] & o["prima_risposta"].notna()
                                       & (o["prima_risposta"] < o["consegna"]))

    # F10 - la distanza cliente-venditore più lontano, e la sua fascia
    o = aggiungi_distanza(o, cartella)
    return o.reset_index(drop=True)
