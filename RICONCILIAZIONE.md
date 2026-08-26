# I numeri che il .pbix deve riprodurre

I conteggi di `DATI-SPORCHI.md` e `DOMANDA.md` sono stati calcolati leggendo i CSV, **non
dentro Power BI**. Se il cruscotto e il README dicono numeri diversi, il README mente.

Questa e' la lista da spuntare **appena il modello sta in piedi**, prima di disegnare
qualsiasi cosa. Ogni riga si controlla con una misura buttata su una tabella qualsiasi e
poi cancellata: sono trenta minuti, e sono quelli che tengono insieme il progetto.

Se un numero non torna, **non si aggiusta il documento**: si trova quale passaggio di
Power Query si comporta diversamente. Quasi sempre e' un filtro applicato in un ordine
diverso, o una base sbagliata (vedi l'ultima sezione).

---

## TUTTI SPUNTATI — 23/08, sul modello costruito

Il modello e' stato scritto in un'istanza di Power BI Desktop e interrogato con le sue
misure DAX (non con formule scritte a parte). Ogni riga qui sotto e' il risultato di una
misura del modello, letto dal motore.

| # | Misura | Atteso | Ottenuto |
|---|---|---:|---:|
| 3 | Ordini consegnati | 96.470 | **96.470** |
| 4 | Ordini recensiti | 95.824 | **95.824** |
| 5 | Ordini in ritardo | 7.826 (8,1%) | **7.826 (8,11%)** |
| 6 | Giorni di ritardo (mediana) | 5,8 | **5,806** |
| 7 | Margine di consegna (mediana) | 12,3 | **12,318** |
| 8 | Voto medio in orario / in ritardo | 4,29 / 2,57 | **4,294 / 2,567** |
| 10 | Fatturato consegnato e recensito | R$ 15.289.974 | **R$ 15.289.974,39** |
| 11 | % fatturato in ritardo | 8,6% sui recensiti | **8,58% sui recensiti, 8,77% su tutti** |
| 12 | Fase venditore in orario / in ritardo | 1,7 / 3,0 | **1,784 / 3,019** |
| 13 | Fase logistica in orario / in ritardo | 6,9 / 23,9 | **6,935 / 23,922** |
| 14 | Venditori misurati | 2.970 | **2.970** |
| 15 | Venditori sopra soglia | 627 | **627** |
| 16 | Coppie venditore-ordine | 97.811 | **97.811** |
| 17 | Ordini esclusi dal cruscotto | 2.963 | **2.963** |

**Nessuna divergenza.** L'unico scarto — l'8,77% contro l'8,6% — non era un errore ma una
base diversa, ed e' stato corretto in `DATI-SPORCHI.md`: per il fatturato la popolazione
giusta e' tutti i consegnati, non i soli recensiti.

Restano da spuntare quando ci saranno i visuali: 18 (geolocalizzazione, se si fa), 19 e 20
(il calendario continuo e novembre 2016 a zero sull'asse).

## Spuntati prima, sul file costruito a mano

Interrogando il motore locale del file aperto (`localhost:64255`, ADOMD), non leggendoli
dallo schermo:

| # | Cosa | Atteso | Ottenuto |
|---|---|---:|---:|
| 3 | Ordini consegnati con data | 96.470 | **96.470** |
| 4 | Consegnati e recensiti | 95.824 | **95.824** |
| 5 | Consegnati in ritardo | 7.826 | **7.826** |
| — | Ordini a cronologia sana | 95.082 | **95.082** |
| 6 | Ritardo mediano | 5,8 | **5,806** |
| 8 | Voto medio in orario / in ritardo | 4,29 / 2,57 | **4,294 / 2,567** |
| — | Righe di ControlloStatiOrdine | 8 | **8** |

**Power Query riproduce i numeri calcolati sui CSV.** Le due trappole di lettura (§14
a capo dentro i commenti, §15 punto decimale) sono superate: se una delle due fosse
scattata, questi numeri sarebbero diversi.

**Trovato nello stesso controllo:** Power BI aveva creato **nove tabelle data automatiche**
nascoste (`LocalDateTable_...`, una per colonna data, piu' un modello). E' la funzione
«Data/ora automatica», e va spenta — va in conflitto con la tabella `Calendario` creata a
mano e gonfia il file. Si toglie da Opzioni -> Caricamento dati, sia per il file corrente
sia nelle impostazioni globali.

## Da spuntare

| # | Cosa | Atteso | Come |
|---|---|---:|---|
| 1 | Righe caricate da `olist_orders_dataset` prima di ogni filtro | 99.441 | conteggio righe |
| 2 | Ordini con stato `delivered` | 96.478 | |
| 3 | Ordini consegnati **con** data di consegna | 96.470 | la base dei tempi |
| 4 | Ordini consegnati **e** recensiti | 95.824 | la base dei voti |
| 5 | Ordini consegnati oltre la data stimata | 7.826 (8,1%) | |
| 6 | Giorni di ritardo, mediana / media / massimo | 5,8 / 9,6 / 189 | solo sui 7.826 |
| 7 | Anticipo mediano quando in orario | 12,3 giorni | segno opposto |
| 8 | Voto medio in orario / in ritardo | 4,29 / 2,57 | base 4 |
| 9 | Quota di 1-2 stelle in orario / in ritardo | 9,2% / 54,0% | base 4 |
| 10 | Fatturato consegnato e recensito (prezzo + spedizione) | R$ 15.289.974 | base 4 |
| 11 | Quota del fatturato su ordini in ritardo | 8,6% | base 4 |
| 12 | Mediana fase venditore, in orario / in ritardo | 1,7 / 3,0 giorni | base 3, cronologia sana |
| 13 | Mediana fase logistica, in orario / in ritardo | 6,9 / 23,9 giorni | base 3, cronologia sana |
| 14 | Venditori con almeno un ordine consegnato | 2.970 | base 3 |
| 15 | Venditori sopra la soglia di 30 ordini | 627 (83,5% degli ordini) | base 3 |
| 16 | Righe venditore-ordine | 97.811 | **non** 96.470 |
| 17 | Prodotti senza categoria dopo la traduzione | 610 + le 2 categorie non tradotte | zero vuoti nuovi |
| 18 | Righe di geolocalizzazione dopo la riduzione | 19.015 - i punti scartati | una per CAP |
| 19 | Mesi nel calendario fra il primo e l'ultimo ordine | nessun buco, **nov 2016 compreso** | |
| 20 | Ordini di novembre 2016 | 0, e il mese si vede lo stesso | il controllo della time intelligence |

La 19 e la 20 insieme sono il controllo che vale piu' di tutti: se novembre 2016 sparisce
dall'asse invece di comparire a zero, la tabella data non sta funzionando da tabella data,
e ogni confronto anno su anno del cruscotto e' sbagliato senza dirlo.

## Le due basi, da non confondere mai

Nel cruscotto convivono due popolazioni diverse, e **ogni misura deve dichiarare la sua**:

- **96.470** — ordini consegnati con data. E' la base di tutto cio' che riguarda **tempi,
  ritardi e venditori**: per sapere se un pacco e' arrivato tardi la recensione non serve.
- **95.824** — di quelli, i recensiti. E' la base di tutto cio' che riguarda i **voti**.

Le 646 righe di differenza sembrano niente e non lo sono: usare la base sbagliata sposta
i venditori da 2.970 a 2.965 e quelli con almeno un ritardo da 1.390 a 1.376. **E'
l'errore che e' stato commesso e corretto scrivendo `DATI-SPORCHI.md`** — la direzione
della conclusione non cambiava, ma cinque numeri pubblicati erano sbagliati.

Un errore cosi' non da' nessun messaggio di errore. L'unica difesa e' scrivere la base
accanto al numero, sempre.
