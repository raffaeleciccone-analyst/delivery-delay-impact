# Criterio C20 di SPEC.md (F11): i numeri letti DENTRO Power BI coincidono con quelli attesi.
# Gira solo con il report aperto in Power BI Desktop (una sola finestra), altrimenti si salta.
import json
import os
import shutil
import subprocess

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# espressione DAX -> (valore atteso, decimali con cui il report lo mostra)
ATTESI = {
    "[Ordini consegnati]": (96_470, 0),
    "[Ordini recensiti]": (95_824, 0),
    "[Ordini in ritardo]": (6_534, 0),
    "[% ordini in ritardo]": (0.068, 3),
    "[Giorni di ritardo (mediana)]": (7, 0),
    "[% negative (consegne in orario)]": (0.092, 3),
    "[% recensioni in ritardo scritte prima del pacco]": (0.701, 3),
    "[% negative prima del pacco]": (0.806, 3),
    "[% negative in ritardo dopo il pacco]": (0.194, 3),
    "[% fatturato in ritardo]": (0.075, 3),
    "CALCULATE([Fase venditore (mediana)], Ordini[in_ritardo] = FALSE())": (1.8, 1),
    "CALCULATE([Fase venditore (mediana)], Ordini[in_ritardo] = TRUE())": (3.1, 1),
    "CALCULATE([Fase logistica (mediana)], Ordini[in_ritardo] = FALSE())": (7.0, 1),
    "CALCULATE([Fase logistica (mediana)], Ordini[in_ritardo] = TRUE())": (26.2, 1),
    "[Venditori misurati]": (2_970, 0),
    "[Venditori sopra soglia]": (627, 0),
    "[% ordini in ritardo gen-ago 2017]": (0.035, 3),
    "[% ordini in ritardo gen-ago 2018]": (0.077, 3),
}


@pytest.fixture(scope="module")
def dal_motore():
    if shutil.which("powershell") is None:
        pytest.skip("serve PowerShell (Windows)")
    p = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         os.path.join(RADICE, "leggi-misure.ps1")] + list(ATTESI),
        capture_output=True, text=True, encoding="utf-8", timeout=180)
    try:
        esito = json.loads(p.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        pytest.fail("leggi-misure.ps1 non ha risposto in JSON:\n" + p.stdout + p.stderr)
    if "errore" in esito:
        pytest.skip("C20 saltato: " + esito["errore"])
    return esito["misure"]


@pytest.mark.parametrize("dax", list(ATTESI))
def test_c20_misura_dentro_power_bi(dal_motore, dax):
    atteso, decimali = ATTESI[dax]
    valore = dal_motore[dax]
    assert valore is not None, "la misura è vuota nel modello: " + dax
    assert round(float(valore), decimali) == pytest.approx(atteso), dax
