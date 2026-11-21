# Criteri C9-C13 e C21 di SPEC.md: il modello e il report, controllati senza aprire Power BI.
# C9-C11 usano verifica-tela.py (i suoi controlli esistevano già); questo file li divide per
# criterio, così un rosso dice quale regola è saltata.
import json
import os
import shutil
import subprocess
import sys

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINE = os.path.join(RADICE, "delivery-delay-impact.Report", "definition", "pages")
REPORT = "delivery-delay-impact.Report"


@pytest.fixture(scope="module")
def esito_tela():
    p = subprocess.run([sys.executable, os.path.join(RADICE, "verifica-tela.py")],
                       cwd=RADICE, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


def problemi(esito, *parole):
    _, testo = esito
    return [r for r in testo.splitlines() if any(p in r for p in parole)]


def visuali(pagina):
    cartella = os.path.join(PAGINE, pagina, "visuals")
    return {n: json.load(open(os.path.join(cartella, n, "visual.json"), encoding="utf-8"))
            for n in os.listdir(cartella)}


def test_c9_misure_e_colonne_usate_esistono(esito_tela):
    assert problemi(esito_tela, "misura inesistente", "colonna inesistente") == []


def test_c10_niente_fuori_pagina_sovrapposto_o_fuori_griglia(esito_tela):
    assert problemi(esito_tela, "esce dalla tela", "si sovrappongono", "fuori griglia",
                    "scheda troppo piccola") == []


def test_c11_nessuna_misura_inutilizzata(esito_tela):
    assert problemi(esito_tela, "misura mai usata") == []


def test_c9_c11_verifica_tela_nel_complesso(esito_tela):
    codice, testo = esito_tela
    assert codice == 0, testo


def test_c12_pagine_del_report():
    ordine = json.load(open(os.path.join(PAGINE, "pages.json"), encoding="utf-8"))["pageOrder"]
    for pagina in ["la-domanda", "di-chi-e-il-ritardo", "come-cambia", "dentro-un-mese", "cosa-non-dice"]:
        assert pagina in ordine, pagina


@pytest.mark.skipif(shutil.which("git") is None, reason="git non disponibile")
def test_c13_rigenerare_il_report_non_cambia_niente():
    sporco = subprocess.run(["git", "status", "--porcelain", "--", REPORT], cwd=RADICE,
                            capture_output=True, text=True).stdout
    if sporco.strip():
        pytest.skip("il report ha modifiche non salvate: C13 si controlla a lavoro salvato")
    subprocess.run([sys.executable, "costruisci-report.py"], cwd=RADICE, check=True,
                   capture_output=True)
    dopo = subprocess.run(["git", "status", "--porcelain", "--", REPORT], cwd=RADICE,
                          capture_output=True, text=True).stdout
    assert dopo.strip() == "", "lo script produce un report diverso da quello salvato:\n" + dopo


def test_c21_grafico_ritardo_per_fascia_di_distanza():
    v = visuali("di-chi-e-il-ritardo")
    assert "p2-distanza" in v, "manca il grafico p2-distanza nella pagina 2"
    testo = json.dumps(v["p2-distanza"], ensure_ascii=False)
    assert "fascia_distanza" in testo
    assert "% in ritardo per distanza" in testo
