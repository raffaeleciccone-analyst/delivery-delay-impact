# Criteri C15-C19 di SPEC.md: la distanza fra venditore e cliente (F10).
# C15 e C16 si provano su dati inventati piccoli, così si sa la risposta giusta;
# C17-C19 sui CSV veri.
import pandas as pd
import pytest

import riferimento

FASCE = ["Sotto 100 km", "100-500 km", "500-1.000 km", "1.000-2.000 km", "Oltre 2.000 km"]
NON_CALCOLABILE = "Distanza non calcolabile"


def test_c15_san_paolo_rio_circa_360_km():
    km = riferimento.distanza_km(-23.5505, -46.6333, -22.9068, -43.1729)
    assert abs(km - 360) <= 5


def test_c15_stesso_punto_zero_km():
    assert riferimento.distanza_km(-23.55, -46.63, -23.55, -46.63) == 0


def test_c16_un_cap_con_piu_punti_diventa_uno_solo():
    geo = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000, 1000, 1000, 2000],
        "geolocation_lat": [-23.0, -23.2, -30.0, -10.0],
        "geolocation_lng": [-46.0, -46.2, -46.1, -50.0],
    })
    punti = riferimento.un_punto_per_cap(geo)
    assert len(punti) == 2
    p = punti.set_index("cap").loc[1000]
    # mediana, non media: il punto a -30 (sbagliato ma dentro il Brasile) non sposta il centro
    assert p["lat"] == -23.2 and p["lng"] == -46.1


def test_c16_i_punti_fuori_dal_brasile_si_scartano():
    geo = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000, 3000],
        "geolocation_lat": [-23.0, 42.0],     # il secondo è in Europa
        "geolocation_lng": [-46.0, 12.0],
    })
    punti = riferimento.un_punto_per_cap(geo)
    assert list(punti["cap"]) == [1000]


def test_c17_ordini_senza_coordinate_esclusi_e_contati(ordini):
    senza = ordini["distanza_km"].isna()
    assert senza.sum() > 0
    assert (ordini.loc[senza, "fascia_distanza"] == NON_CALCOLABILE).all()


def test_c17_cap_senza_coordinate(cap_senza_coordinate):
    # 158 CAP distinti (279 clienti): DATI-SPORCHI §9 diceva 278 contando i clienti
    assert cap_senza_coordinate == {"clienti": 158, "venditori": 7}


def test_c18_fasce_piu_esclusi_danno_il_totale(ordini):
    conta = ordini["fascia_distanza"].value_counts()
    assert set(conta.index) <= set(FASCE + [NON_CALCOLABILE])
    assert int(conta.sum()) == 96_470
    assert ordini["fascia_distanza"].notna().all()


def test_c18_estremi_delle_fasce():
    assert riferimento.fascia_distanza(99.9) == "Sotto 100 km"
    assert riferimento.fascia_distanza(100) == "100-500 km"
    assert riferimento.fascia_distanza(2000) == "Oltre 2.000 km"
    assert riferimento.fascia_distanza(float("nan")) == NON_CALCOLABILE


def test_c19_ordine_con_piu_venditori_usa_il_piu_lontano():
    cliente = pd.DataFrame({"order_id": ["A"], "lat_cliente": [-23.55], "lng_cliente": [-46.63]})
    venditori = pd.DataFrame({
        "order_id": ["A", "A"],
        "lat_venditore": [-23.55, -22.91],   # uno nello stesso punto, uno a Rio
        "lng_venditore": [-46.63, -43.17],
    })
    d = riferimento.distanza_per_ordine(cliente, venditori)
    assert abs(d.loc[d["order_id"] == "A", "distanza_km"].iloc[0] - 360) <= 5
