# Correzioni dopo la pubblicazione

Ogni correzione dice cosa si leggeva prima, perché era sbagliato e cosa si legge adesso.
I numeri vecchi stanno qui, non nei documenti di lavoro.

---

## 2 ottobre 2026: il ritardo per data, e le recensioni scritte prima del pacco

**Prima.** «L'8,1% degli ordini arriva dopo la data promessa. Su quelli le recensioni
negative passano dal 9,2% al 54,0%.»

**Perché era sbagliato.** L'ha trovato una revisione fatta con l'IA, in due punti:
1. il ritardo era calcolato fra due istanti, ma la data promessa è un giorno a
   mezzanotte: 1.292 ordini consegnati nel giorno promesso risultavano in ritardo;
2. il 54% mescolava chi giudica la consegna e chi, senza pacco, giudica l'attesa: sui
   ritardi il questionario parte due giorni dopo la data promessa, e 7 clienti su 10
   rispondono prima di avere il pacco.

**Adesso.** 6,8% di ordini in ritardo. Chi risponde dopo la consegna dà una recensione negativa nel 19,4% dei
casi contro il 9,2% in orario; chi risponde prima, nell'80,6%. Il confronto regge dentro
la stessa fascia di ritardo, a parità di stato e a parità di mese (`DATI-SPORCHI.md`).

**Nello stesso giro:** misure sul momento della recensione (40 in tutto), pagina 1 rifatta,
i venditori normalizzati per volume, la fase «logistica» descritta come trasporto e non come
colpa, gli script senza percorsi scritti a mano.

### Le tre ipotesi verificate, come erano scritte il 23 agosto (con le note del 2 ottobre)

## `[V]` Il legame ritardo -> recensione: **c'è, ed è netto**

**Corretto il 2 ottobre 2026** (§4b e §16). Con il ritardo contato per data, e separando
chi risponde prima di avere il pacco:

| fascia | ordini recensiti | % 1-2 stelle | di cui scritte prima del pacco |
|---|---:|---:|---:|
| 10 gg o più in anticipo | 61.523 | 8,9% | 0% |
| 5-9 gg in anticipo | 20.032 | 9,6% | 0% |
| 0-4 gg in anticipo | 7.888 | 11,3% | 0,1 punti |
| **1-3 gg di ritardo** | 1.852 | **32,2%** | 17,8 punti |
| **4-7 gg** | 1.748 | **67,6%** | 63,0 punti |
| 8-15 gg | 1.601 | 80,0% | 79,0 punti |
| 16-30 gg | 851 | 82,1% | 81,7 punti |
| oltre 30 gg | 329 | 67,8% | 66,6 punti |

Il dirupo resta, ma da 4 giorni di ritardo in su è fatto quasi solo di recensioni scritte
mentre il pacco non c'è. Chi il pacco lo riceve in ritardo dà una recensione negativa nel **19,4%** dei casi,
il doppio del 9,2% in orario: è questo il danno della consegna. Il resto è il danno
dell'attesa. La correlazione di Spearman non cambia (-0,176).

La tabella qui sotto è quella del 23/08, contata per istanti e senza separare il momento
della recensione. Resta per confronto.

Su 95.824 ordini consegnati e recensiti (media dei punteggi dove ce n'è più d'una):

| fascia | ordini | voto medio | % 1-2 stelle |
|---|---:|---:|---:|
| oltre 10 gg in anticipo | 56.905 | 4,32 | 8,9% |
| 5-10 gg in anticipo | 22.442 | 4,28 | 9,1% |
| 0-5 gg in anticipo | 8.816 | 4,15 | 11,0% |
| **0-3 gg in ritardo** | 2.636 | **3,77** | **19,1%** |
| 3-7 gg | 1.773 | **2,32** | **61,3%** |
| 7-15 gg | 1.917 | 1,73 | 78,4% |
| 15-30 gg | 992 | 1,62 | 81,6% |
| oltre 30 gg | 343 | 2,02 | 68,5% |

In orario: voto **4,29**, il 9,2% di recensioni negative. In ritardo: voto 2,57, il
**54%** negative. Il ritardo moltiplica per quasi sei la quota di recensioni negative.

Ma non è una pendenza, è un dirupo. Fra «10 giorni in anticipo» e «appena in orario»
non succede quasi niente; tutto accade nei primi giorni oltre la promessa, e fra 3 e 7
giorni la maggioranza delle recensioni è già negativa. Per questo la correlazione di
Spearman su tutti gli ordini vale solo -0,176: il 92% arriva in anticipo e schiaccia
il coefficiente. Un cruscotto che mostrasse quel -0,18 direbbe il falso. Si mostrano
le fasce.

L'ultima riga si rialza (2,02 contro 1,62): 343 ordini, pochi, e chi aspetta più di un
mese forse è già stato rimborsato. Non è un risultato, è un avviso a non leggere la
coda.

#### `[V]` Il fatturato esposto: **R$ 1,35 milioni, l'8,8%**

**Corretto il 2/10:** contando il ritardo per data sono R$ 1.150.892, il **7,5%** del
fatturato consegnato, su 6,8% degli ordini. La conclusione sotto non cambia.

**Corretto il 23/08 costruendo il modello.** Il primo calcolo dava l'8,6%, ma era fatto
sui soli ordini recensiti (R$ 15.289.974), la base era ereditata dall'analisi sulle
recensioni, e per il fatturato non c'entra niente: un ordine costa e incassa che sia stato
recensito o no.

Sulla base giusta, tutti i 96.470 consegnati, R$ 15.418.395, la quota degli ordini
in ritardo è l'8,77%. Il modello riproduce anche il numero vecchio (8,58% sui
recensiti): non era sbagliato, era su un'altra popolazione.

L'8,1% degli ordini consegnati arriva in ritardo e pesa l'8,8% del fatturato: gli ordini
in ritardo non sono sistematicamente più grandi o più piccoli degli altri.

#### `[V]` Di chi è il ritardo: **della logistica, non dei venditori**

**Corretto il 2/10**, contando per data: il venditore ci mette 1,3 giorni in più (mediana
da 1,8 a 3,1), la logistica **19 in più** (da 7,0 a 26,2). 1.274 venditori su 2.970
fanno almeno un ritardo, e i venti peggiori ne spiegano il 25%. La conclusione non cambia.

Giorni mediani per fase:

| fase | ordini in orario | ordini in ritardo |
|---|---:|---:|
| approvazione -> corriere (**venditore**) | 1,7 | 3,0 |
| corriere -> cliente (**logistica**) | 6,9 | **23,9** |

Ricontrollato togliendo i 1.388 ordini a cronologia rotta (§3): 1,78 → 3,02 e
6,93 → 23,92. Non cambia niente, il che era il punto del controllo.

E l'aritmetica torna, che è la verifica che conta: 1,2 giorni in più dal venditore più
17,0 dalla logistica fanno **18,2 giorni** in più; il margine mediano di consegna in
orario è 12,3 giorni; 18,2 - 12,3 = 5,9 giorni di ritardo atteso, contro
**5,8 misurati**. Le tre misure sono state calcolate separatamente e si incastrano.

Il venditore ci mette 1,3 giorni in più. La logistica ce ne mette **17 in più**. La
seconda metà del titolo, *«quali venditori li causano»*, ha una risposta scomoda:
in larga parte non sono loro.

Questo non toglie la domanda, la migliora. Ma cambia la tela: la pagina sui venditori non
può essere una classifica dei cattivi. Deve mostrare quanto del ritardo è attribuibile
e quanto no, altrimenti il cruscotto propone di sospendere venditori per un problema di
corrieri. Va scritto in cima alla pagina, non nel pannello dei limiti.

E la concentrazione è bassa: **1.390 venditori su 2.970** producono almeno un ritardo, e
i venti peggiori spiegano solo il 24% dei ritardi. Non c'è una manciata di colpevoli.

**La soglia scelta: 30 ordini consegnati.** Tiene 627 venditori, il 21,1% di loro, ma
l'83,5% degli ordini. Sotto quella soglia le percentuali sono rumore. Il peggiore
sopra soglia sta al 34,9% di ritardi su 43 ordini.

La base è «tutti i consegnati», non «i consegnati e recensiti». Sembra un dettaglio e
non lo è: per sapere se un ordine è arrivato tardi la recensione non serve, e usare la
base sbagliata sposta il conteggio dei venditori da 2.970 a 2.965 e quello dei venditori
con almeno un ritardo da 1.390 a 1.376. Ogni misura per venditore deve dichiarare su
quale delle due basi gira, perché le due convivono nello stesso cruscotto: le misure
sulle recensioni non possono che stare sulla base recensita.

E il conteggio va per ordine-venditore, non per ordine: le righe venditore-ordine sono
**97.811** contro 96.470 ordini, per via dei 1.278 ordini multi-venditore (§13). Sommare
i «ritardi per venditore» non dà il numero dei ritardi.

### La riconciliazione del 23 agosto, prima delle correzioni

## TUTTI SPUNTATI, 23/08, sul modello costruito

Il modello è stato scritto in un'istanza di Power BI Desktop e interrogato con le sue
misure DAX (non con formule scritte a parte). Ogni riga qui sotto è il risultato di una
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

Nessuna divergenza. L'unico scarto, l'8,77% contro l'8,6%, non era un errore ma una
base diversa, ed è stato corretto in `DATI-SPORCHI.md`: per il fatturato la popolazione
giusta è tutti i consegnati, non i soli recensiti.

Restano da spuntare quando ci saranno i visuali: 18 (geolocalizzazione, se si fa), 19 e 20
(il calendario continuo e novembre 2016 a zero sull'asse).

#### Spuntati prima, sul file costruito a mano

Interrogando il motore locale del file aperto (`localhost:64255`, ADOMD), non leggendoli
dallo schermo:

| # | Cosa | Atteso | Ottenuto |
|---|---|---:|---:|
| 3 | Ordini consegnati con data | 96.470 | **96.470** |
| 4 | Consegnati e recensiti | 95.824 | **95.824** |
| 5 | Consegnati in ritardo | 7.826 | **7.826** |
|, | Ordini a cronologia sana | 95.082 | **95.082** |
| 6 | Ritardo mediano | 5,8 | **5,806** |
| 8 | Voto medio in orario / in ritardo | 4,29 / 2,57 | **4,294 / 2,567** |
|, | Righe di ControlloStatiOrdine | 8 | **8** |

Power Query riproduce i numeri calcolati sui CSV. Le due trappole di lettura (§14
a capo dentro i commenti, §15 punto decimale) sono superate: se una delle due fosse
scattata, questi numeri sarebbero diversi.

Trovato nello stesso controllo: Power BI aveva creato nove tabelle data automatiche
nascoste (`LocalDateTable_...`, una per colonna data, più un modello). È la funzione
«Data/ora automatica», e va spenta, va in conflitto con la tabella `Calendario` creata a
mano e gonfia il file. Si toglie da Opzioni -> Caricamento dati, sia per il file corrente
sia nelle impostazioni globali.

#### Da spuntare

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

La 19 e la 20 insieme sono il controllo che vale più di tutti: se novembre 2016 sparisce
dall'asse invece di comparire a zero, la tabella data non sta funzionando da tabella data,
e ogni confronto anno su anno del cruscotto è sbagliato senza dirlo.

### Il riquadro del README sulla correzione

Una revisione fatta con l'IA ha trovato due errori nella prima versione, che diceva «le recensioni
negative passano dal 9,2% al 54%»:

1. **Il ritardo era calcolato fra due istanti**, ma la data promessa è un giorno a
   mezzanotte: un pacco arrivato alle 14 del giorno promesso risultava in ritardo. Erano
   1.292 ordini; contando per data la quota in ritardo scende dall'8,1% al 6,8%.
2. **Il 54% mescolava due cose:** chi giudica la consegna e chi, senza pacco, giudica
   l'attesa. Le due ora sono separate.

Le correzioni stanno accanto ai numeri vecchi in `DATI-SPORCHI.md` (§4b e §16), non al
loro posto.

