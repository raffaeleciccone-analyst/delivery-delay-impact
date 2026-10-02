# I numeri che il .pbix deve riprodurre

I conteggi di `DATI-SPORCHI.md` e `DOMANDA.md` sono stati calcolati leggendo i CSV, **non
dentro Power BI**. Se il cruscotto e il README dicono numeri diversi, il README mente.

Questa e' la lista da spuntare appena il modello sta in piedi, prima di disegnare
qualsiasi cosa. Ogni riga si controlla con una misura buttata su una tabella qualsiasi e
poi cancellata: sono trenta minuti, e sono quelli che tengono insieme il progetto.

Se un numero non torna, non si aggiusta il documento: si trova quale passaggio di
Power Query si comporta diversamente. Quasi sempre e' un filtro applicato in un ordine
diverso, o una base sbagliata (vedi l'ultima sezione).

---

## I numeri, ricontati il 2/10 dopo le correzioni §4b e §16

Calcolati in Python sui CSV, replicando i passaggi di Power Query. Lo stesso script
riproduce prima tutti i numeri del 23/08 (8,1%, 54,0%, 1.388, 1.390, 4,2% e 9,4%...), poi
cambia solo il confronto fra date: cosi' lo scarto e' tutto dovuto alla correzione.

| # | Misura | 23/08 | Atteso dal 2/10 | Dal modello |
|---|---|---:|---:|---:|
| 5 | Ordini in ritardo | 7.826 (8,1%) | **6.534 (6,8%)** | **6,8%** |
| 6 | Giorni di ritardo (mediana) | 5,8 | **7** | **7,0** |
| 7 | Margine di consegna (mediana) | 12,3 | **13** | **13** |
| 9 | % negative in orario | 9,2% | **9,2%** | **9,2%** |
| 21 | % recensioni in ritardo scritte prima del pacco | - | **70,1%** (4.476 su 6.381) | **70,1%** |
| 22 | % negative prima del pacco | - | **80,6%** | **80,6%** |
| 23 | % negative in ritardo dopo il pacco | - | **19,4%** (su 1.905) | **19,4%** |
| 11 | % fatturato in ritardo | 8,77% | **7,5%** | **7,5%** |
| 12 | Fase venditore in orario / in ritardo | 1,784 / 3,019 | **1,79 / 3,07** | **1,8 / 3,1** |
| 13 | Fase logistica in orario / in ritardo | 6,935 / 23,922 | **6,96 / 26,20** | **7,0 / 26,2** |
| - | % ritardo gen-ago 2017 / 2018 | 4,2% / 9,4% | **3,5% / 7,7%** | **3,5% / 7,7%** |

La colonna «Dal modello» e' letta dal report esportato in PDF il 2/10 dopo l'aggiornamento
dei dati in Power BI Desktop. Le tre mediane (righe 6, 12 e 13) il cruscotto le mostra con un decimale: tornano a
quel decimale.

Spuntati anche, perche' le correzioni non li toccano: ordini consegnati 96.470, recensiti
95.824, venditori misurati 2.970, sopra soglia 627, coppie venditore-ordine 97.811, ordini
esclusi 2.963, cronologia incoerente 1.388. La riconciliazione del 23 agosto, con i numeri
di allora, sta in `CHANGELOG.md`.

Non cambiano: 96.470, 95.824, 2.970, 627, 97.811, 2.963, 1.388, le negative gen-ago
(10,5% e 13,3%, che dipendono dal mese d'acquisto e non dal ritardo).

## Le due basi, da non confondere mai

Nel cruscotto convivono due popolazioni diverse, e ogni misura deve dichiarare la sua:

- **96.470**, ordini consegnati con data. E' la base di tutto cio' che riguarda tempi,
  ritardi e venditori: per sapere se un pacco e' arrivato tardi la recensione non serve.
- **95.824**, di quelli, i recensiti. E' la base di tutto cio' che riguarda i voti.

Le 646 righe di differenza sembrano niente e non lo sono: usare la base sbagliata sposta
i venditori da 2.970 a 2.965 e quelli con almeno un ritardo da 1.390 a 1.376. **E'
l'errore che e' stato commesso e corretto scrivendo `DATI-SPORCHI.md`**, la direzione
della conclusione non cambiava, ma cinque numeri pubblicati erano sbagliati.

Un errore cosi' non da' nessun messaggio di errore. L'unica difesa e' scrivere la base
accanto al numero, sempre.
