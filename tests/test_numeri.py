# Criteri C1-C8 di SPEC.md: i numeri del cruscotto, ricalcolati dai CSV.
# I valori attesi sono quelli di RICONCILIAZIONE.md (ricontati il 2/10/2026).
import pytest


def quota(serie_bool):
    return round(100 * serie_bool.mean(), 1)


def test_c1_ordini_consegnati_e_recensiti(ordini):
    assert len(ordini) == 96_470
    assert int(ordini["recensito"].sum()) == 95_824


def test_c2_ordini_in_ritardo_e_mediana(ordini):
    assert int(ordini["in_ritardo"].sum()) == 6_534
    assert quota(ordini["in_ritardo"]) == 6.8
    assert ordini.loc[ordini["in_ritardo"], "giorni_ritardo"].median() == 7


def test_c3_recensioni_negative_prima_e_dopo_il_pacco(ordini):
    rec = ordini[ordini["recensito"]]
    in_orario = rec[~rec["in_ritardo"]]
    assert quota(in_orario["voto_negativo"]) == 9.2

    ritardi = rec[rec["in_ritardo"]]
    prima = ritardi[ritardi["recensione_prima_del_pacco"]]
    dopo = ritardi[~ritardi["recensione_prima_del_pacco"]]
    assert len(ritardi) == 6_381
    assert len(prima) == 4_476
    assert quota(ritardi["recensione_prima_del_pacco"]) == 70.1
    assert quota(prima["voto_negativo"]) == 80.6
    assert len(dopo) == 1_905
    assert quota(dopo["voto_negativo"]) == 19.4


def test_c4_quota_di_fatturato_in_ritardo(ordini, righe):
    r = righe.merge(ordini[["order_id", "in_ritardo"]], on="order_id", how="inner")
    assert round(100 * r.loc[r["in_ritardo"], "valore_riga"].sum() / r["valore_riga"].sum(), 1) == 7.5


def test_c5_fasi_venditore_e_corriere(ordini):
    assert int((~ordini["cronologia_ok"]).sum()) == 1_388
    ok = ordini[ordini["cronologia_ok"]]
    med = ok.groupby("in_ritardo")[["giorni_fase_venditore", "giorni_fase_logistica"]].median()
    assert round(med.loc[False, "giorni_fase_venditore"], 2) == 1.79
    assert round(med.loc[True, "giorni_fase_venditore"], 2) == 3.07
    assert round(med.loc[False, "giorni_fase_logistica"], 2) == 6.96
    assert round(med.loc[True, "giorni_fase_logistica"], 2) == 26.20


def test_c6_venditori_e_soglia_di_30_ordini(ordini, righe):
    coppie = righe[righe["order_id"].isin(ordini["order_id"])][["seller_id", "order_id"]].drop_duplicates()
    assert len(coppie) == 97_811
    per_venditore = coppie.groupby("seller_id").size()
    assert len(per_venditore) == 2_970
    assert int((per_venditore >= 30).sum()) == 627


def test_c7_ritardi_gennaio_agosto_2017_e_2018(ordini):
    d = ordini["data_acquisto"]
    gen_ago = d.dt.month <= 8
    assert quota(ordini.loc[gen_ago & (d.dt.year == 2017), "in_ritardo"]) == 3.5
    assert quota(ordini.loc[gen_ago & (d.dt.year == 2018), "in_ritardo"]) == 7.7


def test_c8_consegnato_nel_giorno_promesso_non_e_in_ritardo(ordini):
    stesso_giorno = ordini[ordini["giorni_ritardo"] == 0]
    assert len(stesso_giorno) > 0
    assert not stesso_giorno["in_ritardo"].any()
    # un pacco arrivato alle 14 del giorno promesso: con gli istanti risulterebbe in ritardo (§4b)
    con_ora = stesso_giorno[stesso_giorno["consegna"].dt.hour > 0]
    assert len(con_ora) > 0


def test_c8_consegnati_senza_data_esclusi():
    import riferimento
    from conftest import CSV
    import os
    if not os.path.isfile(os.path.join(CSV, "olist_orders_dataset.csv")):
        pytest.skip("dati_grezzi/csv/ mancante")
    conteggi = riferimento.conteggi_scartati(CSV)
    assert conteggi["non_consegnati"] == 2_963
    assert conteggi["consegnati_senza_data"] == 8


def test_c8_un_ordine_con_piu_recensioni_conta_una_volta(ordini):
    assert ordini["order_id"].is_unique
    multiple = ordini[ordini["recensioni_sull_ordine"] > 1]
    assert len(multiple) > 0
    # il voto è la media: può non essere intero
    assert (multiple["voto"] % 1 != 0).any()
