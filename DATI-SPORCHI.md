# Cosa e' rotto nei dati, e cosa se ne fa

Trovato il 23 agosto 2026 leggendo i CSV senza modificarli.
I file in `dati_grezzi/` restano come sono scaricati: ogni correzione qui elencata
diventa un passaggio con un nome in Power Query, e i nomi sono quelli in grassetto.

Il conteggio sta accanto a ogni problema. Sono i numeri di questo scaricamento: se il
dataset viene riscaricato vanno ricontati.

---

## 1. Gli ordini non consegnati (99.441 -> 96.478)

`order_status` ha otto valori. Solo `delivered` ha senso per una domanda sui tempi di
consegna: gli altri 2.963 sono ordini annullati, non disponibili, in lavorazione o
ancora dal corriere, non hanno una data di consegna perche' non sono mai arrivati.

Passaggio: `Tieni solo gli ordini consegnati`. Ma prima:
`Conta gli scartati per stato`, e il numero finisce nel pannello dei limiti. Buttare
via righe senza dire quante e' il modo silenzioso di far mentire un cruscotto.

| stato | ordini | |
|---|---:|---|
| delivered | 96.478 | gli unici che restano |
| shipped | 1.107 | partiti, mai registrati come consegnati |
| canceled | 625 | |
| unavailable | 609 | |
| invoiced | 314 | |
| processing | 301 | |
| created | 5 | |
| approved | 2 | |

## 2. Otto ordini «consegnati» senza data di consegna

Il caso peggiore: stato `delivered`, `order_delivered_customer_date` vuota. Sono 8. Piu'
14 consegnati senza data di approvazione e 2 senza data di partenza.

Non sono un problema di volume, sono un problema di fiducia: dicono che lo stato e i
timestamp non sono sempre d'accordo. Se si filtra per stato e si assume che la data ci
sia, il calcolo del ritardo produce vuoti che si propagano nelle medie senza avvisare.

**Passaggio: `Scarta i consegnati senza data di consegna` (8 righe).**

## 3. Cronologia impossibile, 1.388 ordini

Ricontato sulla base dell'analisi (i 96.470 consegnati con data di consegna), perche' la
prima stesura diceva 1.359 e il modello ne escludeva 1.388: il documento contava una sola
delle quattro cause, e su una base leggermente diversa. Il numero giusto e' quello del
modello, ed e' la somma di queste righe.

- **1.350** ordini risultano affidati al corriere prima di essere approvati.
- **23** risultano consegnati al cliente prima di essere affidati al corriere.
- **14** non hanno la data di approvazione.
- **1** non ha la data di affidamento al corriere.
- In totale **1.388**, cioe' 96.470 meno i 95.082 a cronologia sana. Nessuna riga cade in
  due casi insieme.
- Nessun ordine e' approvato prima dell'acquisto, e nessuno e' consegnato prima
  dell'acquisto: le due catene reggono agli estremi ma non in mezzo.

Conta perche' la sotto-domanda 5 divide il tempo di consegna in fase-venditore e
fase-logistica: su queste righe le fasi vengono negative, e una durata negativa in
una media la tira giu' senza dare errore.

Passaggio: `Marca la cronologia incoerente`, una colonna `cronologia_ok`, non una
cancellazione. Restano nel conteggio degli ordini e nel fatturato, escono solo dalle
misure di durata per fase, che le dichiarano.

## 4. La data stimata e' larga, e questo cambia la lettura

Non e' un difetto dei dati, e' una proprieta' da dichiarare: **quando un ordine arriva in
orario, arriva 13 giorni prima della data promessa** (mediana, contando per data). La stima di Olist e'
molto prudente.

Quindi «in ritardo» qui significa *in ritardo rispetto a una promessa gia' generosa*, il
che rende il ritardo un fatto piu' grave, non meno. Va scritto nel pannello: chi legge
assume che la stima sia una previsione, e non lo e'.

**Corretto il 2/10: con le date il margine e' 13 giorni.** Vedi §4b.

## 4b. La promessa e' un giorno, la consegna un istante

Trovato il 2 ottobre 2026, in una revisione esterna del progetto. `order_estimated_delivery_date`
sta sempre alla mezzanotte: e' un giorno, non un'ora. `order_delivered_customer_date` ha
l'ora. Sottraendo i due istanti, un pacco consegnato alle 14 del giorno promesso risultava
in ritardo di 0,6 giorni.

Erano **1.292 ordini** consegnati nel giorno promesso e contati in ritardo. Con il
confronto fra date:

| | prima (istanti) | dopo (date) |
|---|---:|---:|
| ordini in ritardo | 7.826 (8,1%) | **6.534 (6,8%)** |
| ritardo mediano | 5,8 giorni | 7 giorni |
| anticipo mediano in orario | 12,3 giorni | 13 giorni |
| quota del fatturato in ritardo | 8,8% | 7,5% |

Passaggio: `Giorni di ritardo` ora sottrae `DateTime.Date` da `DateTime.Date` e da' giorni
interi. Le fasce cambiano etichetta per dire gli estremi veri («4-7 gg» invece di «3-7»).

## 5. Le recensioni non sono una per ordine

- 99.224 righe, **98.410** `review_id` distinti, 98.673 `order_id` distinti.
- **547 ordini** hanno piu' di una recensione.
- **789 `review_id`** compaiono su piu' di un ordine, la chiave non e' una chiave.
- Titolo mancante nell'**88%** dei casi, testo nel 59%.

Questa e' la ragione per cui `Recensioni` non puo' essere trattata come un attributo
dell'ordine senza una scelta esplicita.

Passaggio: `Una recensione per ordine (media dei punteggi)`, e la scelta va scritta
in chiaro: su 547 ordini il punteggio mostrato e' una media, non un voto dato da qualcuno.
Il campo `review_id` non entra nel modello come chiave.

## 6. `customer_id` non e' il cliente

99.441 `customer_id` distinti, esattamente quanti gli ordini, contro **96.096**
`customer_unique_id`. Il primo e' una chiave per ordine; la persona e' il secondo.

Solo il **3,1%** delle persone ordina piu' di una volta (massimo: 17 ordini).

Passaggio: `Distingui cliente-ordine da persona`. E' anche il fatto che regge un
punto del pannello: con il 97% di clienti da un solo acquisto, da questi dati non si
puo' misurare se una recensione negativa fa perdere il cliente. Non c'e' un dopo.

## 7. Categorie prodotto: mancanti, non tradotte, e un refuso

- **610 prodotti senza categoria.**
- 73 categorie nei prodotti, **71** nella tabella di traduzione: `pc_gamer` e
  `portateis_cozinha_e_preparadores_de_alimentos` non hanno traduzione. Un merge
  ingenuo le trasforma in vuoti e le fa sparire dai grafici per categoria.
- Il file di traduzione ha un **BOM UTF-8**: encoding da dichiarare in lettura, o la
  prima colonna prende un nome sporco e la relazione non aggancia.
- Due colonne hanno un refuso nel nome alla fonte: `product_name_lenght`,
  `product_description_lenght` (*lenght* per *length*). Non servono alla domanda, ma
  rinominarle e' il tipo di cosa che si nota.

**Passaggi: `Leggi le traduzioni dichiarando UTF-8`, `Traduci le categorie tenendo le
non tradotte`, `Categoria mancante -> (non indicata)`.** Mai lasciare che un merge
mancato diventi un vuoto silenzioso.

## 8. Le citta' scritte in piu' modi

611 citta' venditore distinte, ma alcune sono la stessa scritta in modi diversi:

`sao paulo` (694) · `sao paulo - sp` (3) · `sao paulo / sao paulo` (1) · `sp` (4) ·
`sp / sp` · `rio de janeiro / rio de janeiro` · `carapicuiba / sao paulo` ·
`mogi das cruzes / sp` · `lages - sc` · `cariacica / es` · `jacarei / sao paulo` ·
`ribeirao preto / sao paulo`

Passaggio: `Normalizza le citta' (taglia dopo / e -)`. Lo stato non ha il problema:
27 sigle per i clienti, 23 per i venditori, tutte pulite. Se serve un raggruppamento
geografico affidabile, si usa lo stato, non la citta', e si dice perche'.

## 9. La geolocalizzazione non e' una dimensione

1.000.163 righe per **19.015** prefissi di CAP: mediana 29 righe per prefisso, massimo
1.146. Piu' 261.831 duplicati esatti e 47 punti fuori dai confini del Brasile.

Non e' una tabella di anagrafica, e' un elenco di rilevazioni. Usata com'e' in una
relazione, moltiplica le righe dei fatti.

Passaggio: `Un punto per CAP (mediana di lat/lng)`, dopo
`Scarta i punti fuori dal Brasile`. La mediana e non la media, perche' un punto
sbagliato sposta la media e non la mediana.

Restano **278** CAP di clienti e 7 di venditori senza corrispondenza: la distanza per
quegli ordini non si calcola, e vanno contati, non nascosti.

## 10. Ordini senza righe, senza recensione, senza pagamento

- **775** ordini non hanno nessuna riga d'ordine, esistono, ma non contengono niente.
- **768** ordini non hanno recensione; fra i soli consegnati, 646.
- **1** ordine non ha pagamento.
- Nel verso opposto e' tutto pulito: nessuna riga d'ordine, recensione o pagamento
  orfana; nessun prodotto, venditore o cliente citato e mancante dall'anagrafica.

Passaggio: `Conta gli ordini senza righe / senza recensione`. Un ordine senza
recensione non e' un ordine con voto zero: sparisce dalle misure sulle recensioni ma
resta nel fatturato, e le due basi vanno dette.

## 11. Il 2016 e le due code non sono mesi

| | ordini |
|---|---:|
| set 2016 | 4 |
| ott 2016 | 324 |
| **nov 2016** | **0, il mese non esiste** |
| dic 2016 | 1 |
| gen 2017 -> ago 2018 | da 800 a 7.544 al mese |
| set 2018 | 16 |
| ott 2018 | 4 |

E' la trappola annunciata. Novembre 2016 non ha nessun ordine: senza
tabella calendario separata e marcata come tale, la time intelligence salta il mese e i
confronti anno su anno lo fanno in silenzio.

**Il periodo utile e' gennaio 2017 - agosto 2018.** Il resto non e' poco, e' una coda di
avvio e una di troncamento del dump. Il confronto anno su anno esiste solo su
gennaio-agosto: e' l'unico intervallo presente in entrambi gli anni.

**Passaggi: `Calendario continuo 2016-2018` (creato a parte, non derivato) e
`Marca il periodo utile`.**

## 12. Altre tre, minori

- **`shipping_limit_date` arriva al 9 aprile 2020**, un anno e mezzo oltre l'ultimo
  ordine del dump. E' una scadenza contrattuale, non un fatto avvenuto: non e' una data
  da collegare al calendario.
- **383 righe con spedizione a 0** e nessuna con prezzo a 0. Spedizione gratis e'
  plausibile, ma va deciso se entra nel fatturato esposto.
- **9 pagamenti da 0**, 3 con `payment_type` = `not_defined`, 2 con rate a 0.
  Non toccano la domanda, ma se si mostra il fatturato dai pagamenti invece che dalle
  righe i totali non tornano, e sono due strade diverse per lo stesso numero.

## 13. Un ordine, piu' venditori

**1.278 ordini** contengono prodotti di venditori diversi. Il ritardo e' dell'ordine, il
venditore e' della riga: attribuire il ritardo a ciascun venditore dell'ordine conta lo
stesso ritardo piu' volte.

Passaggio: `Marca gli ordini multi-venditore`. Nelle misure per venditore la scelta
va dichiarata (sono l'1,3% degli ordini, qualunque scelta cambia poco, ma va detta).

## 14. I commenti delle recensioni contengono a capo

`olist_order_reviews_dataset.csv` ha **104.720 righe fisiche** ma 99.224 record: 5.496
a capo stanno dentro i commenti, protetti dalle virgolette.

Letto senza dichiarare le virgolette, il file si spezza in righe fantasma: `review_score`
si riempie di testo, i tipi saltano, e il conteggio degli ordini recensiti cambia senza
che niente dia errore.

Passaggio: leggere con `QuoteStyle = QuoteStyle.Csv`, l'impostazione che Power Query
non sceglie da sola quando si incolla il codice a mano. Il controllo che lo verifica:
dopo il caricamento le righe devono essere 99.224, non 104.719.

## 15. Il punto decimale contro le impostazioni italiane

I prezzi sono scritti `58.90`, le date `2017-09-19 09:45:35`. Windows in italiano usa la
virgola come separatore decimale: una conversione di tipo che eredita la cultura di
sistema legge `58.90` come **5890**, oppure fallisce.

Non e' un difetto del file: e' l'incontro fra un file americano e un computer italiano, ed
e' l'errore piu' silenzioso di tutti, perche' moltiplica il fatturato per cento senza
lamentarsi.

Passaggio: ogni conversione di tipo dichiara `"en-US"`, in tutte le query. Il
controllo: il fatturato deve fare R$ 15.289.974, non un numero con troppi zeri.

---

## 16. Sui ritardi la recensione arriva prima del pacco

Trovato il 2 ottobre 2026, insieme al §4b. `review_creation_date` e' il giorno in cui
Olist manda il questionario, `review_answer_timestamp` quello in cui il cliente risponde.

- Se il pacco arriva in orario, il questionario parte **il giorno dopo la consegna**
  (97% dei casi).
- Se il pacco e' in ritardo, Olist **non lo aspetta**: il questionario parte **due giorni
  dopo la data promessa** (4.460 recensioni su 6.409), pacco arrivato o no.

Il risultato: sui 6.381 ordini in ritardo e recensiti, **4.476 (70,1%) hanno la risposta
prima della consegna**. Quelle recensioni giudicano l'attesa, non il pacco, e l'**80,6%**
e' negativo. Sugli ordini in orario la stessa cosa succede nello 0,3% dei casi.

Il 54% di recensioni negative in ritardo, il numero di testa del progetto fino a oggi,
mescolava quindi due cose diverse:

| ordini in ritardo, recensiti | ordini | % negative |
|---|---:|---:|
| risposta **prima** di ricevere il pacco | 4.476 | **80,6%** |
| risposta **dopo** averlo ricevuto | 1.905 | **19,4%** |
| in orario, per confronto | 89.443 | 9,2% |

**Il confronto equo.** Chi risponde dopo la consegna ha avuto, per costruzione, ritardi
brevi: tre su quattro stanno fra 1 e 3 giorni. Allora il 19,4% va guardato dentro la
stessa fascia di ritardo, dove i due gruppi sono comparabili:

| fascia di ritardo | dopo il pacco | % negative | prima del pacco | % negative |
|---|---:|---:|---:|---:|
| 1-3 giorni | 1.434 | **18,6%** | 418 | 78,7% |
| 4-7 giorni | 395 | **20,3%** | 1.353 | 81,4% |
| 8-15 giorni | 57 | 26,3% | 1.544 | 81,9% |

Anche con 1-3 giorni di ritardo le negative col pacco in mano sono il doppio del 9,2% in
orario. Sopra i 7 giorni i gruppi «dopo il pacco» sono troppo piccoli per dire altro.

Un limite da dichiarare: sui 547 ordini con piu' di una recensione il voto e' una media
(§5), mentre il momento e' quello della PRIMA risposta. Sono lo 0,6% degli ordini.

Passaggio: `RecensioniPerOrdine` tiene anche `prima_risposta` (il minimo di
`review_answer_timestamp`); `Ordini` ne ricava `recensione_prima_del_pacco` e
`momento_recensione`, poi butta via l'istante.

---

# Le tre ipotesi di `DOMANDA.md`, verificate

Numeri del 2 ottobre 2026: ritardo contato per data (§4b), recensioni separate per
momento (§16). Le versioni precedenti stanno in `CHANGELOG.md`.

## `[V]` Il legame ritardo -> recensione: **c'e', ed e' netto**

| fascia | ordini recensiti | % 1-2 stelle | di cui scritte prima del pacco |
|---|---:|---:|---:|
| 10 gg o piu' in anticipo | 61.523 | 8,9% | 0% |
| 5-9 gg in anticipo | 20.032 | 9,6% | 0% |
| 0-4 gg in anticipo | 7.888 | 11,3% | 0,1 punti |
| **1-3 gg di ritardo** | 1.852 | **32,2%** | 17,8 punti |
| **4-7 gg** | 1.748 | **67,6%** | 63,0 punti |
| 8-15 gg | 1.601 | 80,0% | 79,0 punti |
| 16-30 gg | 851 | 82,1% | 81,7 punti |
| oltre 30 gg | 329 | 67,8% | 66,6 punti |

Non e' una pendenza, e' un dirupo: fra dieci giorni di anticipo e la consegna nel giorno
promesso non succede quasi niente, e da 4 giorni di ritardo in su la barra e' fatta quasi
solo di recensioni scritte mentre il pacco non c'e'. Per questo la correlazione di
Spearman su tutti gli ordini vale solo -0,176: il 92% arriva in anticipo e schiaccia il
coefficiente. Si mostrano le fasce.

Chi il pacco lo riceve in ritardo boccia nel **19,4%** dei casi, contro il 9,2% in orario.
Regge nei confronti equi:
- dentro la stessa fascia di ritardo (§16): 18,6% con 1-3 giorni, 20,3% con 4-7;
- a parita' di stato del cliente: 19,4% contro 9,3% degli ordini in orario dello stesso
  stato (media pesata sui ritardi);
- a parita' di mese d'acquisto: 19,4% contro 9,4%.

E' un'associazione: Olist non ha assegnato i ritardi a caso, e resta possibile che chi
ha un ritardo abbia anche altro che non va (§ «Cosa NON dice» nel cruscotto).

L'ultima fascia si abbassa (67,8% contro 82,1%): 329 ordini, pochi, e chi aspetta piu' di
un mese forse e' gia' stato rimborsato. Non e' un risultato, e' un avviso a non leggere la
coda.

## `[V]` Il fatturato esposto: **R$ 1,15 milioni, il 7,5%**

Sulla base di tutti i 96.470 consegnati (R$ 15.418.395), gli ordini in ritardo pesano
R$ 1.150.892, il **7,5%**, contro il 6,8% degli ordini: non sono sistematicamente piu'
grandi o piu' piccoli degli altri. La base e' quella dei consegnati, non dei recensiti:
un ordine costa e incassa che sia stato recensito o no.

## `[V]` Dove si accumula il ritardo: **nella fase di trasporto**

Giorni mediani per fase, sui 95.082 ordini a cronologia coerente (§3):

| fase | ordini in orario | ordini in ritardo |
|---|---:|---:|
| approvazione -> corriere (venditore) | 1,8 | 3,1 |
| corriere -> cliente (trasporto) | 7,0 | **26,2** |

Sugli ordini in ritardo i giorni in piu' stanno quasi tutti nella fase di trasporto
(+19,2 contro +1,3). E' una descrizione di dove si accumula il tempo, non un'attribuzione
di colpa: la fase «trasporto» comprende tutto quello che succede dopo l'affidamento al
corriere, e i dati non dicono perche'. Le mediane non si sommano: i due numeri si leggono
uno accanto all'altro, non come pezzi di un conto.

**I venditori, normalizzati per volume.** 1.274 venditori su 2.970 fanno almeno un
ritardo. I venti con piu' ritardi ne producono il 24,6%, ma gestiscono anche il 20,5%
degli ordini: il loro tasso di ritardo e' 8,0% contro il 6,7% di tutti. Sono grandi, non
anomali. Sopra la soglia di 30 ordini il tasso mediano e' 5,5%, e il 90° percentile
12,6%.

Questo cambia la tela: la pagina sui venditori non puo' essere una classifica dei
cattivi, altrimenti il cruscotto propone di sospendere venditori per un problema che si
vede nella fase di trasporto.

**La soglia scelta: 30 ordini consegnati.** Tiene 627 venditori, il 21,1% di loro, ma
l'83,5% degli ordini. Sotto quella soglia le percentuali sono rumore.

La base e' «tutti i consegnati», non «i consegnati e recensiti»: per sapere se un ordine
e' arrivato tardi la recensione non serve. E il conteggio va per ordine-venditore, non
per ordine: le righe venditore-ordine sono **97.811** contro 96.470 ordini, per via dei
1.278 ordini multi-venditore (§13). Sommare i «ritardi per venditore» non da' il numero
dei ritardi.

---

## Cosa cambia in `DOMANDA.md`

Tre cose, gia' riportate:

1. Il pannello dei limiti guadagna il punto sul dirupo: il legame non e' lineare, e
   il numero riassuntivo (la correlazione) direbbe il contrario del vero.
2. Il punto «il 97% dei clienti compra una volta sola» non e' piu' un'ipotesi: e' 96.096
   persone su 99.441 ordini, misurato.
3. La pagina sui venditori cambia mestiere: da classifica a **scomposizione della
   responsabilita'**.
