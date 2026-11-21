# Ritardi di consegna — PIANO (come)

> Il COSA sta in SPEC.md. Qui c'è il COME.
> Ogni scelta tecnica cita la frase della spec che la giustifica.
> Se una scelta qui contraddice la spec, vince la spec: si corregge il piano.
> Stato: 21/11/2026, prima stesura (progetto esistente portato "by spec" + distanza nuova).

## 1. Architettura

```
dati_grezzi/csv/*.csv  (Kaggle, non nel repo — D1)
        │
        ├──> power-query/*.m ──> costruisci-modello.ps1 ──> .SemanticModel (TMDL)   ┐
        │                                                                          ├─> Power BI Desktop
        │                         costruisci-report.py ──> .Report (PBIR JSON)      ┘        │
        │                                                                                     │ (aperto)
        └──> tests/riferimento.py  (stessi passaggi in pandas)                               │
                     │                                                                        │
                     └──> tests/  ──  C1-C8, C15-C19 sui CSV                                  │
                                  ──  C9-C13, C21 sui file del report                         │
                                  ──  C20 ──> leggi-misure.ps1 ──> motore di Power BI ────────┘
                                  ──  C14 sul README
```

Il modello e il report restano generati dagli script (F9). La novità è la cartella `tests/`: tutti i
criteri della spec diventano test pytest, lanciati con un solo comando.

## 2. Il riferimento in Python

`tests/riferimento.py` rifà in pandas gli stessi passaggi delle query M, con gli stessi nomi, e restituisce
una tabella `ordini` con le colonne di `Ordini` (giorni_ritardo, in_ritardo, cronologia_ok, recensito,
recensione_prima_del_pacco, distanza_km, fascia_distanza...). Motivo: C1-C8 e C15-C19 chiedono numeri
calcolati dai CSV, e oggi lo script che li calcolava non è nel repository (RICONCILIAZIONE.md lo cita).

Regola: **se riferimento e Power BI non coincidono, si cerca quale passaggio differisce**, non si
aggiusta il numero atteso (è la regola di RICONCILIAZIONE.md). C20 è il test che fa il confronto.

## 3. Dati / modello

| Elemento | Contenuto | Perché (spec) |
|---|---|---|
| `11-CoordinateCAP.m` (nuova, non caricata) | un punto per prefisso CAP: mediana di lat e lng, dopo aver tolto i punti fuori dal Brasile | F10, C16, DATI-SPORCHI §9 |
| `Ordini[distanza_km]` (nuova) | distanza in linea d'aria cliente–venditore più lontano; vuota se manca una coordinata | F10, C15, C17, C19 |
| `Ordini[fascia_distanza]`, `Ordini[fascia_distanza_ordine]` (nuove) | 5 fasce + "Distanza non calcolabile"; colonna per ordinarle | C18, C21 |
| misura `Ordini senza distanza` (nuova) | ordini con distanza vuota, mostrata sotto il grafico | C17 |
| grafico `p2-distanza` (nuovo, pagina 2) | barre: `% consegnati in ritardo` per `fascia_distanza` | F10, C21, Q3 |
| `leggi-misure.ps1` (nuovo) | si collega al Power BI aperto e stampa in JSON il valore di una lista di misure | F11, C20 |

### Scelte e motivi
- **Distanza calcolata in Power Query, non in un CSV preparato da Python.** Motivo: F9, il modello si
  ricostruisce dai dati grezzi con i soli script del progetto.
- **Mediana delle coordinate, non media.** Motivo: C16 e DATI-SPORCHI §9 (un punto sbagliato sposta la
  media, non la mediana). "Centro" in C16 vuol dire questo.
- **Confini del Brasile: latitudine da −33,75 a 5,27, longitudine da −73,99 a −34,79.** Motivo: §9 conta
  47 punti fuori dal Brasile; il riferimento Python e la query M usano gli stessi quattro numeri, scritti
  in un posto solo per lato.
- **Formula dell'emisenoverso (haversine), raggio 6.371 km.** Motivo: C15, distanza in linea d'aria
  (§4 della spec: niente distanza su strada).
- **Venditore più lontano per gli ordini con più venditori.** Motivo: C19.
- **Fasce: <100, 100-500, 500-1.000, 1.000-2.000, >2.000 km**; il taglio cade nella fascia superiore
  (100 km esatti → "100-500"). Motivo: Q3 risolta; l'estremo va deciso perché C18 conta ogni ordine una volta.
- **La fascia "Distanza non calcolabile" sta nel modello ma non nel grafico.** Il grafico filtra le cinque
  fasce e sotto dice quanti ordini sono esclusi. Motivo: C17 (contati, non nascosti) e C21 (cinque fasce).
- **C20 da PowerShell, non da Python.** Motivo: la DLL per parlare con il motore
  (`Microsoft.PowerBI.AdomdClient.dll`) è già installata con Power BI e PowerShell la carica senza
  installare niente; da Python servirebbe `pythonnet`. Il test pytest lancia lo script e legge il JSON.
- **La porta del Power BI aperto si trova da sola** nel file `msmdsrv.port.txt` sotto
  `%LOCALAPPDATA%\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\`. Se non c'è nessuna istanza,
  o ce n'è più di una, C20 viene saltato e lo dice. Motivo: §6 della spec, i test "dentro Power BI" si
  saltano quando Power BI è chiuso.
- **I test sui CSV si saltano se `dati_grezzi/csv/` manca** (CI su GitHub). Motivo: §6, i dati non si
  ridistribuiscono.
- **C13 rigenera il report e controlla con git che non cambi niente.** Motivo: C13; è il controllo fatto a
  mano il 21/11.

## 4. Struttura del codice

```
power-query/11-CoordinateCAP.m   nuova: un punto per CAP
power-query/02-Ordini.m          + distanza_km, fascia_distanza, fascia_distanza_ordine
costruisci-modello.ps1           + query CoordinateCAP, colonne nuove, misura "Ordini senza distanza"
costruisci-report.py             + grafico p2-distanza nella pagina 2
leggi-misure.ps1                 nuovo: legge le misure dal Power BI aperto (F11)
tests/
  conftest.py                    carica i CSV una volta; salta se mancano
  riferimento.py                 i passaggi di Power Query rifatti in pandas
  test_numeri.py                 C1-C8
  test_distanza.py               C15-C19
  test_report.py                 C9-C13, C21
  test_powerbi.py                C20
  test_documenti.py              C14
requirements-test.txt            pandas, pytest
```

## 5. Test

```
pip install -r requirements-test.txt
python -m pytest tests -v
```

Un test per criterio, con il criterio nel nome (`test_c2_ordini_in_ritardo`). I valori attesi di C1-C7 sono
quelli di RICONCILIAZIONE.md; quelli della distanza si fissano dopo il primo calcolo (SPEC §5) e si
scrivono in RICONCILIAZIONE.md.

Ordine di lavoro:
1. test C1-C8 → falliscono (manca `riferimento.py`) → scrivo `riferimento.py` → passano.
2. test C9-C13 → passano subito (avvolgono `verifica-tela.py` e il controllo con git, che esistono già).
3. test C15-C19 e C21 → falliscono → query M, modello, report, riferimento → passano.
4. test C20 → con Power BI aperto sul report aggiornato.
5. Prova che i test valgono: rompo apposta una regola (es. il ritardo calcolato sugli istanti invece che
   sulle date, l'errore corretto il 2/10) e controllo che C2 se ne accorga.
6. Schermate, README (C14), RICONCILIAZIONE.md, CHANGELOG.md.

## 6. Da fare
- [ ] Passi 1-6 qui sopra.
- [ ] Aggiungere `pytest` alla CI su GitHub (oggi il repo non ha una CI): girerebbero C9-C14 e C21,
      gli altri si saltano senza dati.
