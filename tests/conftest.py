# Fixture comuni ai test. I CSV di Olist non sono nel repository (SPEC §6): se mancano,
# i test che li usano vengono saltati e lo dicono, invece di fallire.
import os
import sys

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(RADICE, "dati_grezzi", "csv")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def ordini():
    """La tabella Ordini rifatta in pandas, una volta per tutta la sessione."""
    if not os.path.isfile(os.path.join(CSV, "olist_orders_dataset.csv")):
        pytest.skip("dati_grezzi/csv/ mancante: scarica il dump Olist (vedi README)")
    import riferimento
    return riferimento.costruisci_ordini(CSV)


@pytest.fixture(scope="session")
def cap_senza_coordinate():
    if not os.path.isfile(os.path.join(CSV, "olist_geolocation_dataset.csv")):
        pytest.skip("dati_grezzi/csv/ mancante")
    import riferimento
    return riferimento.cap_senza_coordinate(CSV)


@pytest.fixture(scope="session")
def righe():
    if not os.path.isfile(os.path.join(CSV, "olist_order_items_dataset.csv")):
        pytest.skip("dati_grezzi/csv/ mancante")
    import riferimento
    return riferimento.righe_ordine(CSV)
