# Criterio C14 di SPEC.md: i numeri scritti nel README sono quelli che escono dai dati.
# Ogni numero si ricalcola dal riferimento e si cerca, formattato all'italiana, nel README.
import os

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def it(x, decimali=1):
    """6.8 -> '6,8'; 96470 -> '96.470'"""
    if decimali == 0:
        return f"{x:,.0f}".replace(",", ".")
    return f"{x:.{decimali}f}".replace(".", ",")


def pct(serie_bool, decimali=1):
    return it(100 * serie_bool.mean(), decimali) + "%"


@pytest.fixture(scope="module")
def readme():
    return open(os.path.join(RADICE, "README.md"), encoding="utf-8").read()


def numeri_attesi(o):
    rec = o[o["recensito"]]
    rit = rec[rec["in_ritardo"]]
    neg_per_fascia = rec.groupby("fascia_ritardo")["voto_negativo"].mean() * 100
    mese = o.groupby(o["data_acquisto"].dt.to_period("M"))["in_ritardo"].mean() * 100
    dist = o.groupby("fascia_distanza")["in_ritardo"].mean() * 100
    return {
        "ordini consegnati": it(len(o), 0),
        "% in ritardo": pct(o["in_ritardo"]),
        "% negative prima del pacco (arrotondata)": pct(rit.loc[rit["recensione_prima_del_pacco"], "voto_negativo"], 0),
        "% negative dopo il pacco": pct(rit.loc[~rit["recensione_prima_del_pacco"], "voto_negativo"]),
        "% negative in orario": pct(rec.loc[~rec["in_ritardo"], "voto_negativo"]),
        "negative con 10+ giorni di anticipo": it(neg_per_fascia["10 gg o più in anticipo"]) + "%",
        "negative con 0-4 giorni di anticipo": it(neg_per_fascia["0-4 gg in anticipo"]) + "%",
        "negative con 4-7 giorni di ritardo": it(neg_per_fascia["4-7 gg di ritardo"]) + "%",
        "ritardi novembre 2017": it(mese[pd_period("2017-11")]) + "%",
        "ritardi marzo 2018": it(mese[pd_period("2018-03")]) + "%",
        "ritardi sotto 100 km": it(dist["Sotto 100 km"]) + "%",
        "ritardi oltre 2.000 km": it(dist["Oltre 2.000 km"]) + "%",
        "ordini senza distanza": it(int(o["distanza_km"].isna().sum()), 0) + " ordini",
    }


def pd_period(s):
    import pandas as pd
    return pd.Period(s, freq="M")


def test_c14_i_numeri_del_readme_vengono_dai_dati(ordini, readme):
    mancanti = {nome: valore for nome, valore in numeri_attesi(ordini).items() if valore not in readme}
    assert not mancanti, "numeri attesi ma non trovati nel README: %s" % mancanti
