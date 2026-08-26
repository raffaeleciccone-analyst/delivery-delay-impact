# A che punto siamo

Aggiornato il **26 agosto 2026**. `HANDOFF.md` dice cosa fare e perche'; questo dice cosa
e' gia' fatto.

## Fatto

| Passo | Stato | Dove |
|---|---|---|
| 1. Mail all'ITS per l'account Microsoft | **bozza pronta, da inviare** | `mail-its.md` |
| 2. Scaricare e congelare il dataset | **fatto** | `dati_grezzi/` |
| 3. Scrivere la domanda | **fatto e verificato sui dati** | `DOMANDA.md` |
| 4. Esplorare e trovare lo sporco | **fatto** — 13 problemi | `DATI-SPORCHI.md` |
| 5. Power Query | **fatto** — 11 query in `power-query/` | `power-query/` |
| 6. Modello a stella | **fatto e verificato** | `costruisci-modello.ps1` |
| 7. Misure DAX | **fatte** — 39 misure | `costruisci-modello.ps1` |
| 8. La tela | **fatta** — 4 pagine, una di dettaglio, un riquadro al mouse, 160 visuali | `costruisci-report.py` |
| 9. Pannello «cosa NON dice» | **fatto** — e' la pagina 4 | `costruisci-report.py` |
| 10. Consegna: repo, README, schermate | repo e README **fatti**; schermate **da rifare** | `README.md` |

**Ambiente:** Power BI Desktop **2.157.879.0 (26.08)** x64, installato il 23/08 da winget
(`Microsoft.PowerBI`, sorgente `winget`). Non e' la versione dello Store: non si aggiorna
da sola, quindi il `.pbix` resta leggibile con la versione con cui e' stato scritto.

**Il dataset e' congelato** e il token Kaggle usato per scaricarlo e' stato revocato:
per lavorare non serve piu' niente da fuori.

## Dove si e' arrivati con Power Query (23/08, fine sessione)

In `power-query/` ci sono sei query pronte: `PercorsoDati`, `OrdiniGrezzi`, `Ordini`,
`ControlloStatiOrdine`, `RigheOrdine`, `RecensioniPerOrdine`. `ISTRUZIONI.md` dice come
si incollano.

**Cambio di disegno rispetto a `DOMANDA.md`:** il voto della recensione e' agganciato a
`Ordini` con un merge, invece di stare in una tabella collegata. `RecensioniPerOrdine` ha
gia' grana un-ordine, quindi una tabella separata avrebbe aggiunto una relazione
uno-a-uno senza guadagnarci niente — e cosi' **le due basi diventano una colonna
dichiarata** (`recensito`), che e' quello che i documenti chiedevano.

## Il modello e' costruito e verificato (23/08, sera)

**Due script, e il modello nasce da solo.**

- `costruisci-modello.ps1` — legge le undici query da `power-query\*.m`, monta tabelle,
  colonne, relazioni e 22 misure DAX con le API di Power BI, scrive tutto in TMDL sotto
  `delivery-delay-impact.SemanticModel\definition\` e **rilegge quello che ha scritto** per validarlo.
- `spingi-modello.ps1 <porta>` — scrive quel modello dentro un'istanza di Power BI Desktop
  aperta e vuota, e carica i dati. E' la strada degli strumenti esterni (Tabular Editor
  fa cosi'). Si rifiuta di scrivere se l'istanza contiene gia' delle tabelle.

**Verificato interrogando il modello con le sue misure:** tutti i numeri di
`RICONCILIAZIONE.md` tornano. Vedi li' la tabella completa.

**Cosa contiene:** 8 tabelle (Ordini, RigheOrdine, ControlloStatiOrdine, Clienti,
Venditori, Prodotti, Calendario, Misure), 4 query non caricate, 6 relazioni a stella —
compresa la seconda data (`data_consegna`) tenuta **inattiva** per USERELATIONSHIP — e
22 misure.

### Il giro completo, verificato il 23/08 alle 20:30

`costruisci-modello.ps1` -> riscrive `delivery-delay-impact.SemanticModel\definition\` -> si apre
`delivery-delay-impact.pbip` -> il modello e' dentro, con i dati e le misure che rispondono.
Provato togliendo e rigenerando il modello con Power BI chiuso: si riapre e funziona.

**Quindi il progetto si modifica scrivendo testo**, che era il punto: le query stanno in
`power-query\*.m`, il modello si rigenera da uno script, e il tutto sta in un repository
leggibile in un diff. Il `.pbix` si ottiene da qui con un Salva con nome.

**L'involucro del progetto lo ha scritto Power BI**, non lo script: `.platform`,
`definition.pbism`, la cartella `delivery-delay-impact.Report`. Lo script si rifiuta di partire se non
lo trova, e non prova a rifarlo — vedi sotto perche'.

### Perche' il `.pbip` generato a mano non si apriva

Confrontato con quello vero, mancavano tre cose:

- **`delivery-delay-impact.Report\definition\version.json`**, che non scrivevo affatto;
- gli **schemi JSON** erano vecchi di parecchie versioni (`report` 1.0.0 contro 3.3.0,
  `page` 1.0.0 contro 2.1.0, `pagesMetadata` 1.0.0 contro 1.1.0);
- il **tema** va anche come file dentro `StaticResources\SharedResources\BaseThemes\`,
  non solo nominato nel JSON.

Power BI apriva il progetto **vuoto senza dire niente**, il che rende la cosa costosa da
diagnosticare. La conclusione utile: quell'involucro e' roba di Power BI e cambia versione
con lui. Si fa generare una volta con Salva con nome e non si tocca.

### Storico: cosa NON funzionava

Il progetto viene scritto, ma Power BI Desktop lo apre **vuoto**, senza dire perche'.
Verificato per esclusione, leggendo le classi di `Microsoft.PowerBI.Packaging.dll`:

- `.pbip` e' registrato nel sistema come `PowerBI.Project`: il formato e' supportato;
- gli schemi e le versioni che scriviamo sono quelli che le classi dichiarano
  (`ArtifactShortcut` 1.0, `DatasetDefinition` 6.0, `ReportDefinition` 4.0);
- non e' un problema del modello: lo stesso modello, spinto nell'istanza, funziona.

Resta il contenuto della cartella del report (formato PBIR) o i file `.platform`, scritti
a intuito. **Per chiudere la questione serve un esempio vero**: da Power BI, con un file
aperto, `File -> Salva con nome -> Progetto Power BI (*.pbip)`. Sono venti secondi e
tolgono ogni dubbio.

Non e' bloccante: il modello si costruisce lo stesso, e da un `.pbix` salvato si puo'
sempre fare Salva con nome in `.pbip`.

## La disciplina di Power Query, per quando si rimette mano

1. Caricare i nove CSV da `dati_grezzi/csv/`, **dichiarando l'encoding UTF-8** almeno per
   `product_category_name_translation.csv`, che ha il BOM.
2. Applicare i passaggi di pulizia con i **nomi gia' decisi** in `DATI-SPORCHI.md`: sono
   in grassetto, uno per problema.
3. **Prima di disegnare qualsiasi cosa**, spuntare i venti numeri di
   `RICONCILIAZIONE.md`. Se non tornano, non si aggiusta il documento: si trova il
   passaggio che si comporta diversamente.

## La tela: tre pagine, uno script (23/08 sera, riconciliato il 26/08)

`costruisci-report.py` scrive le pagine in PBIR — un JSON per visuale — dentro
`delivery-delay-impact.Report\definition\pages\`. Non tocca l'involucro (`.platform`,
`definition.pbir`, `version.json`, il tema): quello e' roba di Power BI.

| Pagina | Titolo | Cosa fa |
|---|---|---|
| 1 | I ritardi di consegna quanto ci costano in recensioni negative? | Quattro riquadri, il dirupo per fascia di ritardo, la lettura accanto |
| 2 | In larga parte non sono i venditori. | Le due fasi della consegna, il ritardo per stato, la soglia dichiarata |
| 3 | Cosa questa analisi NON dice | Otto limiti misurati, la tabella degli ordini esclusi |

Il titolo e' deciso: **la seconda meta' e' caduta.** «Quali venditori li causano» prometteva
una classifica di colpevoli che i dati non danno — la pagina 2 dice perche', e lo dice come
risposta, non come scusa.

## Cosa e' stato riconciliato il 26/08

Il 23/08 alle 21:35 il progetto e' stato aperto in Power BI Desktop, e Desktop ha
risalvato tutto. Da li' modello, report e script si erano scollati in tre punti:

1. **La misura `% ritardo dello stato` era nello script del modello ma non nel modello.**
   `costruisci-modello.ps1` la scriveva dalla sera prima, ma non era mai stato rilanciato:
   il TMDL su disco ne aveva 26, lo script 27. La visuale che la usa era rotta.
2. **Toppata a mano in Desktop con `% ordini in ritardo`** — che pero' conta le righe di
   `Ordini`, e il filtro su `Venditori[stato]` non ci arriva: le relazioni vanno
   `Venditori 1 -> * RigheOrdine * -> 1 Ordini`, a senso unico. **Tutte le barre avrebbero
   mostrato lo stesso numero**, senza nessun errore. E' esattamente l'errore che il
   pannello dei limiti dichiara di sorvegliare, capitato in casa.
   `% ritardo dello stato` si appoggia a `DISTINCTCOUNT( RigheOrdine[order_id] )`, che al
   filtro risponde.
3. **Sette visuali mancavano** rispetto a quello che lo script genera: i quattro fili di
   colore sotto i riquadri della pagina 1 e i tre piedi di pagina.

Rimesse le cose a posto rilanciando i due script, che restano la sorgente:
`costruisci-modello.ps1` (27 misure, riletto senza errori) e `costruisci-report.py`
(3 pagine, 31 visuali). Dello schema JSON delle visuali si scrive ora la versione che
scrive Desktop, **2.12.0** invece di 2.7.0, cosi' un salvataggio non produce un diff.
Il titolo scritto a mano sulla pagina 2 e' stato **tenuto** — dice la lettura invece della
disciplina — e la soglia dei 100 ordini che stava li' e' scesa nel piede.

**La regola che ne esce:** quando si tocca qualcosa in Desktop, o si riporta nello script
o si perde. Desktop risalva tutto e non dice cosa ha cambiato.

## Il passaggio grafico (26/08)

La sostanza era giusta e la tela era basica. Rifatta seguendo il metodo che ha piu'
consenso fra chi fa questo mestiere — Few, Tufte, Knaflic, IBCS — che si riduce a poche
regole applicabili una per una.

**Il colore si calcola, non si sceglie.** Il grigio chiaro di prima, `#B4B2AB`, stava a
**2,1:1** di contrasto sulla carta bianca: sotto la soglia di 3:1, le barre «in orario»
erano quasi invisibili. Sostituito con `#8A8880`, che passa tutto — contrasto 3,3:1,
separazione dal rosso 8,4 in simulazione daltonica (l'obiettivo e' 8) e 18,7 a visione
normale. Verificato col validatore, non a occhio.

**Tre grafici, tre forme sbagliate.**

- **Il dirupo** era a colonne *affiancate* con due misure di cui una sempre vuota: ogni
  barra si ritirava in meta' del suo posto, lasciando accanto il vuoto dell'altra serie.
  Ora sono colonne **impilate**: la barra e' larga quanto la fascia.
- **Le due fasi della consegna** erano affiancate. Sono i due pezzi di una sola durata:
  **impilate** si legge anche il totale, che affiancate spariva.
- **Il ritardo per stato** era a colonne verticali, con le sigle degli stati ruotate.
  E' una classifica: **barre orizzontali ordinate**, etichette diritte.

**Una griglia vera.** Dodici colonne da 130, gronda 24, margine 48. Prima le larghezze
erano 432-432-432-456: quel 456 era un residuo. Ora ogni visuale comincia e finisce su
una colonna, e `verifica-tela.py` lo controlla.

**I quattro fili colorati sotto i riquadri sono spariti**, ed erano decorazione: tre grigi
e uno rosso per dire quale numero conta. Al loro posto il riquadro-perno ha il fondo
appena rosato e il numero piu' grande — si riconosce da lontano senza fregi — e sotto
ogni riquadro c'e' una **didascalia che dichiara la base** di quel numero. Lo spazio che
prima decorava adesso dice una cosa.

**La testata e' una fascia di carta** con il filo rosso sopra e un righello sotto, invece
di testo che galleggiava sul fondo. Con l'indicatore di pagina a destra, le tre pagine si
riconoscono come lo stesso documento.

**La pagina 3 non e' piu' due muri di testo alti 840 pixel**, ma otto schede su una
griglia 4x2, ognuna con un limite. Stessa sostanza, ma si trova il limite che si cerca.
Due limiti vicini — «non e' una pendenza» e «legame, non causa» — sono diventati una
scheda sola.

Le schede di testo usano ora **la stessa intestazione dei grafici** (il titolo del
contenitore, non un paragrafo in grassetto): la pagina si legge come una cosa sola.

### `verifica-tela.py`

Power BI non dice niente quando una visuale esce dalla pagina, quando due si
sovrappongono, o quando una misura non esiste: **mostra il vuoto**. E' esattamente il
modo in cui e' passato inosservato il guasto del 23/08. Lo script controlla le tre cose
scrivendo testo, e va lanciato dopo ogni `costruisci-report.py`:

```
python costruisci-report.py && python verifica-tela.py
```

Oggi passa: 49 visuali, ogni misura e ogni colonna citata esistono nel modello, niente
esce dalla tela, niente si sovrappone, tutto sta sulla griglia.

### Il testo, riscritto (26/08, secondo giro)

Prima revisione con Raffaele davanti al file aperto: la tela sembrava simile a prima, e
**il testo si riconosceva come scritto da una macchina**. Contate, in tre pagine: 17
costruzioni «non X, ma Y» e 14 trattini lunghi. E' quello il rumore.

Riscritto tutto in italiano piatto. I trattini lunghi sono zero, le antitesi sono sei e
solo dove dicono davvero qualcosa. I titoli affermano invece di negare:

| Prima | Adesso |
|---|---|
| In larga parte non sono i venditori. | Il ritardo si forma quasi tutto dopo il venditore. |
| Non e' una pendenza, e' un dirupo | Il salto sta nei primi giorni di ritardo |
| La soglia e' una scelta, non un dato | Perche' la soglia sta a 30 ordini |
| LA RISPOSTA SCOMODA | DI CHI E' IL RITARDO |
| Legame, non pendenza — e non causa | Correlazione e causa |

Le chiuse a effetto in fondo a ogni paragrafo sono cadute. I numeri stanno all'inizio
della frase, dove si leggono.

### Il carattere e la testata

La tela era corretta e anonima: Segoe UI dappertutto e' Power BI appena installato.

- **Le parole in grazie, i numeri in bastoni.** Georgia per i titoli e le intestazioni
  dei riquadri, Segoe UI per etichette, assi, legende e i numeri dei riquadri. E' la
  coppia dei quotidiani, ed e' la cosa che cambia di piu' l'impressione a colpo d'occhio.
- **La testata e' scura**, chiusa sotto da un filo rosso, con il titolo bianco in Georgia
  a 27pt e l'occhiello rosso sopra. Prima era una fascia bianca su fondo quasi bianco, e
  non si vedeva.

Georgia sta su Windows e su Mac senza installare niente, quindi il file si apre uguale
anche altrove.

### Margini interni e la tabella che scorreva (26/08, terzo giro)

Seconda revisione col file aperto. Due difetti, tutti e due di quelli che si vedono solo
guardando.

**Il testo toccava il bordo dei riquadri.** Power BI non da' nessun margine interno alle
caselle di testo: quello che scrivi arriva fino al bordo. Non c'e' una proprieta' per
sistemarlo, quindi `scheda()` adesso emette **due visuali invece di una**: la carta
(fondo, bordo, ombra) e sopra il testo, rientrato di 20 pixel ai lati e 18 in cima. Per
lo stesso motivo il titolo della scheda e' tornato a essere il primo paragrafo invece del
titolo del contenitore, cosi' rientra insieme al resto.

**La tabella degli ordini esclusi scorreva.** Ha otto righe e ne stava in 268 pixel poco
piu' di sei: le ultime due si raggiungevano solo trascinando. Le schede dei limiti si
sono strette da 252 a 226 e la tabella e' salita a 320, che le bastano. Una tabella che
scorre dentro un cruscotto e' una tabella che nessuno legge fino in fondo.

**Quinto controllo in `verifica-tela.py`: la stima dell'ingombro del testo.** Power BI
taglia in silenzio quello che non ci sta, ed e' l'ultima cosa che restava invisibile.
Il controllo e' una stima, non una misura, e avvisa sopra il 95% di riempimento. La
casella piu' piena adesso sta all'89%; `p3-l1` era al 94% e il suo paragrafo e' stato
accorciato.

### Quarto giro (26/08): i riquadri, la tabella, le barre di scorrimento

**Le etichette dei quattro riquadri di pagina 1 stavano nell'angolo, il numero al centro.**
Erano il titolo del contenitore e il valore della carta: due cose su assi diversi, senza
margine sopra. `riquadro()` adesso emette **tre visuali** — la carta, l'etichetta e il
numero — con l'etichetta che ha la sua fascia da 38 pixel a 18 dal bordo, e il numero
sotto. Tutti e due centrati sulla stessa mezzeria, insieme alla didascalia. I riquadri
crescono da 150 a 196 pixel, che e' lo spazio che serviva all'etichetta.

**Due barre di scorrimento, tutte e due inutili.**

- La scheda della soglia a pagina 2 ci stava per un pelo, e Power BI la barra la mette
  lo stesso. I riquadri sopra scendono da 170 a 150 e la scheda guadagna venti pixel,
  piu' una frase piu' corta.
- La tabella degli otto stati scorreva anche a 320 pixel: le righe di `tableEx` sono piu'
  alte di quanto stimavo. Invece di stringere ancora le schede dei limiti, **la tabella e'
  passata nella colonna di destra** e prende l'altezza di due file, 512 pixel, con la
  spaziatura delle righe da 6 a 3. Pagina 3 diventa tre schede per fila invece di quattro,
  con le ultime due che scendono nella fascia in basso accanto alla nota.

**La soglia dell'avviso in `verifica-tela.py` scende dal 95% all'85%.** La scheda della
soglia mostrava la barra a un riempimento stimato dell'89%: la stima e' ottimista, quindi
il margine si allarga. La casella piu' piena adesso e' all'80%.

**Il grafico di pagina 1 perde 42 pixel di altezza** (da 616 a 574), e le etichette delle
otto fasce scendono a 10pt: a 11pt una etichetta come «Oltre 10 gg in anticipo» chiedeva
piu' spazio di quanto ne lasci una fascia larga 151 pixel. E' un ritocco: se lo spazio
vuoto si vede ancora, la mossa vera e' girare il grafico a barre orizzontali, dove otto
etichette lunghe si leggono diritte e il riquadro si riempie. E' una parola nello script
(`forma="classifica"`), non un rifacimento.

### Quinto giro (26/08): visto sul file aperto

Le schermate hanno mostrato tre cose che dallo script non si vedevano.

**Power BI si scrive il sottotitolo da solo**, e ci mette dentro il nome grezzo della
colonna: sotto «Recensioni negative per fascia di ritardo» compariva *«% negative
(consegne in orario) e % negative (consegne in ritardo) per fascia_ritardo»*. Adesso
`_riquadro()` spegne `subTitle` su ogni contenitore.

**Il grafico del dirupo era girato per il verso sbagliato.** Otto fasce con etichette
lunghe: le etichette andavano su due righe sotto colonne strette, e sopra il disegno
restavano il sottotitolo e una legenda su due righe. Fra le due, centotrenta pixel su
cinquecentosettantaquattro spesi prima di arrivare alle barre.

Adesso e' a **barre orizzontali**: le etichette si leggono diritte a sinistra e le barre
riempiono la larghezza. La legenda e' sparita perche' non serviva: le tre barre grigie
sono le tre fasce «in anticipo» e le cinque rosse quelle «in ritardo», e lo dicono le
etichette. Il colore non e' l'unica cosa che distingue le due serie, quindi la legenda
era inchiostro in piu'. Quello che diceva sta nel titolo.

**La tabella degli stati era finita male.** Occupava 512 pixel per riempirne 320, le
intestazioni erano `order_status` e `ordini`, il numero degli ordini consegnati diceva
`96478` senza punto delle migliaia, e l'ordinamento era alfabetico. Correzioni:

- nel modello, `Aggiungi-Tabella` accetta ora **un nome da mostrare e un formato**, quarto
  e quinto elemento della colonna. Le due colonne diventano «Stato dell'ordine» e
  «Ordini», con formato `#,0`;
- la tabella si ordina per numero di ordini, decrescente;
- il titolo diceva «gli ordini che questa analisi non guarda» mentre la prima riga era
  `delivered` con 96.478. Adesso dice **«Ordini per stato: entra nell'analisi solo
  delivered»**, che e' quello che la tabella mostra davvero.

**Pagina 3 rimisurata sui numeri veri**: griglia 3x3 di schede a sinistra (gli otto
limiti piu' la nota) e una colonna a destra con la tabella alta 320 e i due riquadri.

I valori degli stati restano in inglese perche' sono i codici della sorgente. Tradurli
vuol dire aggiungere una colonna alla query M e rinfrescare i dati: si fa, ma e' una
scelta, non una svista.

### Sesto giro (26/08): il fondo e la tabella, di nuovo

**Il fondo scende da `#F4F3F0` a `#EDECE8`.** Un gradino, quanto basta perche' la carta
bianca dei riquadri stacchi invece di confondersi. Con il fondo piu' scuro il grigio dei
piedi e delle didascalie e' finito a **4,4:1**, appena sotto la soglia di 4,5 per il
testo piccolo, quindi e' sceso da `#6E6C66` a `#67655F` e adesso sta a 4,9:1. E' il
genere di cosa che si vede solo calcolandola.

**La tabella scorreva di nuovo, e la colpa era del titolo che le avevo dato.** «Ordini
per stato: entra nell'analisi solo delivered» sono 52 caratteri, e a 14pt in 398 pixel
ce ne stanno una quarantina: andava a capo, e quella seconda riga erano i 28 pixel che
rimettevano la barra. Tre correzioni insieme:

- il titolo torna a **«Ordini per stato»**, sedici caratteri, una riga sola;
- il riquadro sale da 320 a **344 pixel**, e i due riquadri sotto si riadattano a 214;
- la **spaziatura delle righe passa da 3 a 5**, cosi' le otto righe si distribuiscono
  invece di lasciare il fondo vuoto.

Che solo `delivered` entri nell'analisi lo dice la scheda accanto, che e' il posto giusto:
un titolo non e' una nota a pie' di pagina.

### Settimo giro (26/08): le colonne della tabella

Sulla schermata si e' visto che le due colonne stavano larghe quanto il testo e lasciavano
vuota meta' del riquadro a destra. E' l'**auto-dimensionamento** della tabella: Power BI
stringe le colonne sul contenuto e lo spazio che avanza resta bianco.

`tabella()` accetta ora un parametro `larghezze`: spegne `autoSizeColumnWidth` e assegna
i pixel colonna per colonna. **216 e 132.** Al primo tentativo erano 264 e 142, e la barra
di scorrimento e' ricomparsa in orizzontale: dentro una carta larga 438 lo spazio per le
colonne e' circa 350, non 438. Il resto se lo prendono il margine interno della tabella e
la banda dove la barra verticale comparirebbe. Misurato sulla schermata, contando i pixel
fra il bordo della carta e l'inizio dell'intestazione.

Il riquadro sale ancora da 344 a **376 pixel** — la barra di scorrimento restava per una
manciata di pixel, con tutte e otto le righe gia' visibili — e la spaziatura delle righe
passa da 5 a 6. I due riquadri sotto scendono a 198, con il secondo ancorato al fondo.

### Le pagine intere, viste per la prima volta (26/08)

L'export in PDF ha permesso di guardare le tre pagine per intero invece che a pezzi.
`schermate.py` converte il PDF in PNG a 2952x1692. Tre difetti, tutti nel modo in cui
Power BI rende le cose: **i numeri erano giusti, la resa no.**

**I riquadri usavano la carta nuova (`cardVisual`), che e' una scelta sbagliata.**
Scriveva il nome della misura sopra il valore — «% ordini in ritardo» sopra «8,1%» —
allineato a sinistra, e `categoryLabels: show = false` non lo spegneva. Peggio: sceglieva
da sola le unita' di misura. **2.970 venditori diventavano «3K», 97.811 coppie «98K», il
fatturato «1Mln».** Numeri esatti resi inservibili.

Adesso i riquadri usano la carta classica (`card`): il nome lo spegne davvero, centra il
valore, e con `labelDisplayUnits` a 1 lascia stare le unita'.

**Il grafico degli stati era azzurro.** Il selettore per misura sul colore funziona quando
le serie sono due; con una sola Power BI lo ignora e usa il blu del tema. In mezzo a una
tavolozza di due colori validati, la sola cosa che si vedeva era un blu che non c'entrava.
Con una serie sola il colore va scritto senza selettore.

**Il grafico delle fasi aveva due barre in 396 pixel** e stavano in mezzo a un riquadro
mezzo vuoto. Scende a 240, e i 156 pixel liberati vanno al grafico degli stati, che di
righe ne ha quattordici.

Riconciliato con `RICONCILIAZIONE.md`: 8,1% di ordini in ritardo (7.826), 9,2% e 54,0% di
recensioni negative, 2.970 venditori, 627 sopra soglia, 97.811 coppie, 2.963 esclusi.
Tutti a posto: il difetto era solo di formattazione.

Le tre pagine, per il resto, funzionano: la griglia 3x3 di pagina 3 si legge, la tabella
riempie la sua larghezza senza barre, l'ordine delle otto fasce e' giusto (l'anticipo in
cima), e nessun testo e' tagliato.

**Le PNG in `schermate/` sono ancora quelle vecchie**: vanno rifatte esportando di nuovo
il PDF dopo queste correzioni.

### «Stato» voleva dire due cose

Il titolo della tabella di pagina 3, «Ordini per stato», non si capiva. La causa non era
il titolo: **in questo report la parola «stato» ha due significati.** A pagina 2 e' lo
stato brasiliano del venditore (MA, SP, RJ); a pagina 3 e' lo stato dell'ordine. Chi
legge le pagine in ordine incontra il secondo dopo il primo e capisce la geografia.

Il titolo diventa **«Cosa entra nell'analisi»**, che non usa la parola ambigua e dice al
lettore che cosa sta guardando. La tabella risponde da sola: `delivered` in cima con
96.478, tutto il resto sotto.

A pagina 2 «stato del venditore» resta, perche' li' sotto ci sono le sigle e l'equivoco
non si pone.

**Un controllo in piu' in `verifica-tela.py`: il titolo che va a capo.** Un titolo su due
righe si prende una ventina di pixel, e sono quelli che mancano al contenuto: e' cosi'
che nella tabella di pagina 3 e' ricomparsa due volte la barra di scorrimento. Il
controllo stima la larghezza e avvisa gia' all'85%. Il primo titolo che avevo scelto,
«Solo i consegnati entrano nell'analisi», stava al 93%: dentro per trenta pixel, cioe'
dentro per caso. Quello nuovo sta al 56%.

### Il secondo giro di schermate (26/08)

Il PDF rifatto dopo le correzioni mostra che i tre difetti sono chiusi: i riquadri dicono
**8,1% · 9,2% · 54,0% · 1.351.625** e **2.970 · 627 · 2.963 · 97.811** invece di «3K» e
«1Mln», e le barre degli stati sono rosse. Pagina 3 e' a posto: griglia leggibile,
tabella piena senza barre, «Cosa entra nell'analisi» in cima.

**Restava la legenda, e la causa era un valore inventato.** Scrivevo `position: TopLeft`,
che **non e' un valore valido** in Power BI: i validi sono `Top`, `Bottom`, `Left`,
`Right` e le varianti Center. Power BI ripiegava su un valore suo e impilava le due voci
una sopra l'altra, prendendosi il doppio dell'altezza. E' il tipo di errore che non da'
nessun errore: si vede solo guardando.

Con `Top` la legenda sta in fila. Il grafico delle due fasi guadagna anche `innerPadding`
a 12: con poche categorie Power BI tiene le barre sottili e le incolla in cima, lasciando
bianco il fondo del riquadro.

**Il controllo dell'ingombro ha ripagato il costo di scriverlo.** Stringendo la fascia di
pagina 2 da 240 a 200 pixel, ha segnalato che il testo di `p2-lettura` sarebbe finito
fuori: 174 pixel stimati in 166 disponibili. L'altezza e' tornata a 240 e il paragrafo
dei conti si e' accorciato di una riga.

### Le schermate sono fatte (26/08)

`schermate/` contiene le quattro immagini della consegna, tutte a 3200 pixel di larghezza.

| File | Come nasce |
|---|---|
| `01-la-domanda.png` | `schermate.py`, dal PDF esportato da Power BI |
| `02-di-chi-e-il-ritardo.png` | idem |
| `03-cosa-non-dice.png` | idem |
| `06-modello.png` | `diagramma-modello.py`, **letto dal TMDL** |
| `06-modello.svg` | lo stesso, vettoriale, per il README |

**Le tre pagine vengono dall'export in PDF, non da catture a mano.** L'export rende la
pagina a piena risoluzione e senza le tre icone che Power BI mostra sopra ogni visuale
quando il mouse ci passa. `schermate.py` converte il PDF in PNG.

**Il diagramma del modello e' disegnato, non fotografato.** La strada ovvia era catturare
la vista Modello di Power BI. `diagramma-modello.py` legge invece
`delivery-delay-impact.SemanticModel/definition`: tabelle, colonne, relazioni, e quale
relazione e' inattiva. Due vantaggi: **se il modello cambia, il disegno cambia con lui**
invece di restare una vecchia fotografia, e il disegno puo' dire cose che la vista
Modello non dice. Quali tabelle sono i fatti e quali le dimensioni, perche' una relazione
e' tratteggiata, e perche' `ControlloStatiOrdine` sta sotto un righello a parte.

Tre difetti trovati solo guardando il file generato, e corretti:

1. la relazione tratteggiata **non toccava nessuna delle due tabelle**: la spostavo in
   verticale dopo aver tagliato il bordo, e per una linea ripida il punto finiva fuori.
   Adesso si sposta il centro da cui si taglia, cosi' il punto resta sul bordo;
2. le due etichette verso il Calendario **si scrivevano una sopra l'altra**, perche'
   stavano tutte e due a meta' della loro linea. Adesso scorrono lungo la linea;
3. le linee **passavano dentro il testo delle etichette**. Adesso l'etichetta si scosta
   perpendicolarmente alla linea, che per una diagonale e' diverso da «piu' in alto».

### Cosa resta da guardare a occhio

Il validatore controlla il colore, non l'impaginato. Da confermare aprendo il file:

- che Georgia venga applicato davvero ai titoli, e che a 27pt il titolo di pagina 1 non
  vada a capo male sulla testata scura;
- che l'indicatore «PAGINA 1 DI 3» sia allineato a destra;
- che nelle schede il testo non venga tagliato in fondo (la stima dice di no, ma resta
  una stima: la casella piu' piena e' `p2-soglia` all'89%);
- che nella classifica per stato restino solo gli stati sopra i 100 ordini.

## Il giro del 26/08: da poster a cruscotto

Il file era corretto e non era interattivo. Contati sul PBIR prima di questo giro: 62
caselle di testo, 8 riquadri, 4 grafici, **zero filtri**. Aperto da chi valuta, il primo
clic non faceva niente — o peggio, faceva la cosa sbagliata: le interazioni predefinite
sono accese, quindi cliccare una fascia del grafico cambiava i numeri dei riquadri in
alto mentre il testo scritto accanto restava quello di prima. **La pagina si contraddiceva
da sola al primo clic.**

Quattro cose, in quest'ordine.

### 1. I filtri, e quali non si possono mettere

Una fascia sotto la testata, su pagina 1, 2 e 3: **anno d'acquisto** (`Calendario[Anno]`)
e **stato del cliente** (`Clienti[stato]`), a discesa, sincronizzati fra le pagine con
`syncGroup` — senza, si torna indietro di una pagina e il filtro e' sparito.

Quali colonne possono stare li' **non e' una scelta di gusto**. Il filtro deve arrivare a
tutte le misure della pagina, e scende dal lato «uno» al lato «molti»: `Calendario` e
`Clienti` stanno sopra `Ordini`, che sta sopra `RigheOrdine`, quindi arrivano dappertutto.
`Venditori` e `Prodotti` stanno sopra `RigheOrdine` ma **non** sopra `Ordini`: un filtro
sul venditore lascerebbe ferme le mediane per fase, che scendono dagli ordini, e la pagina
mostrerebbe due popolazioni diverse fingendo che siano la stessa. **E' lo stesso motivo
per cui `% ritardo dello stato` si appoggia alle righe d'ordine.** Per questo il filtro
geografico e' sullo stato del cliente e non su quello del venditore, ed e' scritto nel
piede della pagina 2.

La fascia sta sul fondo chiaro e non dentro la testata scura: un menu a discesa bianco su
nero va riverniciato tutto a mano. Costa ottanta pixel di grafico e non costa nessun
rischio.

### 2. Le interazioni spente, dichiarate una per una

`pagina()` prende ora un parametro `spegni`, e scrive `visualInteractions` nel
`page.json` (tipo `NoFilter`). Ventinove righe in tutto. La regola e' una sola: **i
riquadri sono la cornice fissa della pagina**, si muovono con i filtri in alto e non con i
clic sui grafici. Cosi' il numero grande e il testo che lo spiega non possono divergere.

Un caso vale da solo: sulla pagina 2 il clic su uno stato **non** filtra il grafico delle
fasi, perche' non ci arriverebbe (vedi sopra). Lasciarlo acceso avrebbe prodotto un
grafico che non si muove, cioe' un grafico che sembra dire «nessuna differenza».

### 3. La pagina 3, che mancava

Le prime due pagine dicono quanto costa il ritardo e da dove viene, tutte e due su tutto
il periodo insieme. Nessuna delle due rispondeva alla prima domanda che fa chi deve
decidere. Ora e' la sesta sotto-domanda di `DOMANDA.md`, ed e' misurata:

> **il ritardo e' piu' che raddoppiato** — gennaio-agosto 2018 contro lo stesso periodo
> 2017, dal 4,2% al 9,4%; le recensioni negative dal 10,5% al 13,3%. E sono **picchi**,
> non una deriva: novembre 2017 fa 14,3%, marzo 2018 fa 21,4%, giugno 2018 fa 1,4%.

Due grafici a linee (`% ordini in ritardo` e `% recensioni negative`, ciascuno con la
propria serie dell'anno prima) e quattro riquadri a finestra fissa su gennaio-agosto.

Le misure nuove usano `SAMEPERIODLASTYEAR`, e funzionano **perche' `Calendario` e'
contrassegnata come tabella data**: e' quella marcatura a togliere dal calcolo il filtro
di `Anno-mese` che arriva dall'asse, e a sostituirlo con le date spostate di un anno.
Senza, i due filtri si intersecherebbero e la serie sarebbe vuota dappertutto. La
marcatura era gia' li' dal 23/08 e fino a oggi non serviva a niente.

Su questa pagina **non c'e' il filtro dell'anno**: i quattro riquadri sono un confronto fra
due anni fissi, e un filtro che non li tocca sarebbe un comando che sembra fare qualcosa e
non fa niente.

### 4. I numeri battuti a mano che sono diventati misure

Erano nel modello e non comparivano da nessuna parte, oppure comparivano solo dentro una
casella di testo — cioe' scritti a mano, che e' esattamente quello che la pagina dei
limiti rimprovera a chi legge.

| Adesso e' un riquadro | Misura | Dove |
|---|---|---|
| Voto medio in orario / in ritardo (4,29 / 2,57) | `Voto medio in orario`, `... in ritardo` | pagina 1 |
| Ritardo mediano (5,8 giorni) | `Giorni di ritardo (mediana)` | pagina 2 |
| Anticipo mediano (12,3 giorni) | `Margine di consegna (mediana)` | pagina 2 |
| Quota del fatturato in ritardo | `% fatturato in ritardo` | pagina 1, sotto il valore assoluto |

Il quarto riquadro di pagina 1 portava `1.351.625` senza valuta e senza denominatore: un
valore assoluto da solo non dice se sia molto o poco. Adesso ha **`R$` nel formato della
misura** — nel modello, non in una nota — e sotto la sua quota, presa dal modello.

Da 27 misure a **37**, da 31 visuali a **121**, da 8 riquadri a **17**.

### Cosa resta da guardare a occhio, di questo giro

Il validatore controlla riferimenti, ingombri e griglia, non l'aspetto. Da confermare
aprendo il file:

- ~~i menu a discesa~~ **trovato e corretto**: nei 56 pixel della fascia ci stava il
  titolo del contenitore e mezzo menu, e il resto finiva sotto una barra di scorrimento.
  La fascia sale a **78 pixel**, e i 22 in piu' li paga la fila dei riquadri (da 190 a 168):
  cosi' tutto quello che sta sotto non si muove di un pixel;
- **la serie grigia della pagina 3**: sui mesi del 2017 deve essere **vuota**, non zero.
  Se e' vuota anche sul 2018, la marcatura come tabella data non sta funzionando;
- che sull'asse della pagina 3 compaiano **venti mesi** (gennaio 2017 - agosto 2018) e non
  trentasei: fuori dal periodo utile le misure tornano vuote e il mese deve sparire;
- il clic su una fascia di pagina 1: **i riquadri in alto non devono muoversi**;
- nessuna casella resta sopra l'85% di riempimento stimato. **Il metro pero' era
  sbagliato**: `verifica-tela.py` misurava il carattere a 0,50 em nei bastoni e 0,52 nelle
  grazie, e sul file aperto le caselle che dava intorno al 90% scorrevano davvero. I due
  numeri sono saliti a **0,54 e 0,56**, calibrati contro quel render. Con il metro nuovo
  traboccavano tre schede e andavano a capo tre etichette: le schede si sono accorciate
  togliendo i numeri che adesso stanno nei riquadri, e la fascia dell'etichetta e' passata
  da 38 a 46 pixel.

  **Power BI il testo di troppo non lo taglia: ci mette una barra di scorrimento.** Dentro
  un cruscotto e' peggio, perche' sembra che il contenuto ci stia. Nessun visuale di
  questo file deve scorrere.

### Due difetti trovati aprendo il file, e cosa hanno lasciato

**I numeri di pagina 2 erano tagliati.** I quattro riquadri stavano in 132 pixel: tolti il
margine e la fascia dell'etichetta, al numero da 30pt ne restavano 52 e ne servono 56.
Power BI un numero troppo grande non lo rimpicciolisce e non lo fa scorrere: gli taglia la
pancia, e a colpo d'occhio sembra un numero.

Il rimedio non e' aver spostato quei pixel (riquadri a 140, fascia dell'etichetta da 46 a
40, adesso che ogni etichetta sta su una riga sola). Il rimedio e' il **controllo 7 di
`verifica-tela.py`**: per ogni scheda numerica calcola l'altezza che serve al corpo del
carattere (circa 1,4 volte) e la confronta con la casella. E' un errore, non un avviso.
Senza, la prossima volta che un riquadro si stringe di dieci pixel non lo dice nessuno.

**Le date sull'asse erano `2017-01`.** Era il nome grezzo della colonna `Anno-mese`, che
serve a ordinare e non a leggere. Il `Calendario` ha adesso una colonna **`Etichetta
mese`** — `gen 17`, `feb 17` — ordinata **per** `Anno-mese`.

L'etichetta porta l'anno di proposito. Il solo `gen` sarebbe piu' corto, ma comparirebbe
due volte sul periodo e Power BI fonderebbe i due gennai nella stessa categoria: due punti
diventerebbero uno, senza avvisare. Una colonna d'ordinamento vuole una corrispondenza
uno a uno con l'etichetta, e `gen 17` ce l'ha.

> **Serve un aggiornamento dei dati.** `Etichetta mese` e' una colonna nuova: aprendo il
> `.pbip` va aggiornata la tabella `Calendario`, altrimenti l'asse resta vuoto.

### Perche' i grafici non rispondevano, e cosa risponde adesso

La domanda giusta: con i filtri in alto e le interazioni spente, un clic su un grafico non
faceva piu' niente. Il motivo, guardato caso per caso invece che in generale:

| Clic | Cosa succederebbe | Verdetto |
|---|---|---|
| fascia di pagina 1 -> riquadri | i riquadri sono la cornice fissa e il testo accanto non li segue | resta spento |
| stato -> **riquadri sui venditori** | il filtro arriva ai venditori: 2.970 e 627 diventano quelli di quello stato | **acceso** |
| stato -> mediane per fase | il filtro non arriva agli ordini: i numeri resterebbero fermi | resta spento |
| stato -> grafico delle fasi | stesso motivo | resta spento |
| fasi -> grafico degli stati | filtrando i soli ritardi ogni stato farebbe 100% | resta spento |
| mese -> l'altro grafico del tempo | l'altro si ridurrebbe a un punto solo | resta spento |

Quindi uno si accende: **il clic su uno stato muove i due riquadri sui venditori**, ed e'
scritto nella nota dei filtri di quella pagina, insieme a cosa NON muove e perche'.

Per il resto la risposta non e' accendere interazioni sbagliate, e' **dare al puntatore un
posto dove andare**. `dettaglio-fascia` e' una pagina da 320x288, nascosta, di tipo
`Tooltip`: compare sotto il mouse sul grafico delle fasce, con addosso il filtro della
fascia puntata, e mostra ordini, voto medio, recensioni negative e fatturato **di quella
fascia**. Le quattro voci scendono tutte da `Ordini` o da `RigheOrdine`, cioe' da dove il
filtro della fascia arriva davvero: nessuna resta ferma fingendo di aver risposto.

`verifica-tela.py` adesso riconosce le pagine di dettaglio: prende i limiti dal `page.json`
invece che dare per scontato 1920x1080, e non pretende che stiano sulla griglia da dodici
colonne, che e' della tela grande.

### Il fatturato e' in euro, e il tasso e' una misura

`R$ 1.351.625` non dice niente a un lettore italiano. Il riquadro adesso e' in euro.

Il tasso e' **3,95 reais per euro**, cioe' la media dei cambi mensili BCE del periodo
**pesata per il fatturato di ogni mese** (serie `EXR.M.BRL.EUR.SP00.A`, presa il
26/08/2026): 15.418.395 R$ diviso i 3.902.588 EUR della conversione mese per mese.

La semplificazione e' misurata prima di essere accettata: convertire a tasso unico invece
che mese per mese sposta il fatturato consegnato dello **0,02%** e quello in ritardo dello
**0,5%**. Una tabella dei cambi mensili, con la sua grana da tenere allineata, per mezzo
punto percentuale non vale.

Quello che invece sarebbe stato sbagliato e' prendere il cambio di **un** anno: il 2017
medio (3,6054) gonfia il totale del **9,6%**, il 2018 medio (4,3085) lo sgonfia dell'
**8,3%**. Il real si e' svalutato dentro il periodo dei dati, e i due anni non sono
intercambiabili.

Il tasso non e' sepolto in una formula: e' la misura `Cambio reais per euro`, e sta scritto
nel piede della pagina 1.

### Il repository esiste (26/08, sera)

`git init`, `.gitignore`, primo commit locale — **mai pushato**, e non va pushato finche'
le schermate non sono rifatte.

Cosa resta fuori dal repository, e perche':

- **`dati_grezzi/`**: 164 MB, e sono di Kaggle con licenza CC BY-NC-SA 4.0. Ridistribuirli
  e' una scelta che non tocca a me. Il README dice come scaricarli.
- **`delivery-delay-impact.pbix`**: e' un duplicato binario del `.pbip`, che e' la sorgente
  vera. 26 MB che invecchiano da soli e che in un diff non dicono niente. **Va rigenerato o
  cancellato**: quello su disco e' delle 13:08 e non contiene niente di quello che e' stato
  fatto dopo.
- **`mail-its.md`**: nome, indirizzo e istituto. Roba mia, non del progetto, e un
  repository puo' sempre diventare pubblico.
- **`schermate/superate/`**: le tre pagine della versione a tre pagine, spostate li' perche'
  non finiscano in un README per sbaglio.

Il README non prova a convincere nessuno: dice cosa dicono i dati, cosa c'e' nel modello,
cosa costano le scelte fatte e come si rifa' tutto. **Contiene quattro immagini che ancora
non esistono** — sono i nomi che l'export produrra'. E' voluto: finche' quelle immagini
mancano, il README e' visibilmente incompleto e non si e' tentati di mandarlo a nessuno.

> Da trimmare prima di rendere pubblico il repo: in `HANDOFF.md` la sezione sull'account
> Microsoft parla di me e non dell'analisi.

### Due difetti di sostanza chiusi

**La misura orfana e' stata tolta.** `% ritardo del venditore (sopra soglia)` era scritta
per la classifica dei venditori di pagina 2, e quella pagina ha smesso di essere una
classifica quando i dati hanno detto che i venditori non sono il problema. E' rimasta tre
giorni a girare a vuoto. **La soglia dei 30 ordini non e' sparita con lei**: vive nel
riquadro da 627 e nella soglia dei 100 di `% ritardo dello stato`.

**Il tasso di cambio non e' piu' battuto a mano.** Il piede di pagina 1 scriveva «3,95»
come testo mentre la misura `Cambio reais per euro` stava nel modello: cambiando la misura,
il piede avrebbe raccontato il cambio di ieri. Adesso il numero sul piede scende dal
modello, come quello dei riquadri.

E il **controllo 8** di `verifica-tela.py` impedisce che la prima cosa ricapiti: ogni
misura del modello deve stare su un visuale, o essere citata da un'altra misura, o essere
marcata `isHidden` come `Fatturato consegnato e recensito`, che serve solo a rifare i
controlli di `RICONCILIAZIONE.md`. Altrimenti e' un errore, non un avviso.

Il diagramma del modello e' stato rigenerato dal TMDL nuovo e rinumerato in
`06-modello`, perche' il 04 adesso e' la pagina dei limiti.

### Il drillthrough: dentro un mese (26/08, sera)

La pagina 3 dice che marzo 2018 fa il 21,4% e giugno l'1,4%, e la domanda successiva era
sempre la stessa — **e allora cosa e' successo a marzo?** Fino a oggi non c'era modo di
chiederlo.

`dentro-un-mese` si apre col tasto destro su un mese del grafico della pagina 3. Power BI
deposita il mese scelto nel filtro d'ingresso, che sta **sulla pagina** e non su una
visuale: ci cascano dentro tutti i visuali insieme. Mostra due cose, e sono le due che
servono a decidere:

- **quanto era lungo il ritardo** in quel mese (ordini per fascia): molti ritardi corti e
  pochi ritardi lunghi sono due problemi diversi;
- **da quale fase arrivava** (le stesse due mediane della pagina 2, ristrette al mese): se
  in un mese cattivo si allunga solo la logistica, quel mese non e' un problema di
  venditori.

**La pagina non e' nascosta, ed e' una scelta.** Una pagina di drillthrough nascosta ha un
solo modo di uscire, il pulsante Indietro, che Power BI mette da se' solo quando la pagina
la costruisci nell'interfaccia: scrivendo il JSON non c'e', e chi entra resta chiuso
dentro. Lasciandola visibile si esce dalla linguetta, e aperta da li' mostra tutto il
periodo — una lettura che ha senso lo stesso.

Trovato correggendo: `verifica-tela.py` saltava il controllo della griglia su **tutte** le
pagine con un tipo, e quindi anche su questa, che invece e' a tela piena e la griglia la
deve rispettare. Adesso salta solo il riquadro al mouse, che e' l'unico fuori misura.

### Segnalibri, parametri di campo, RLS: no, e il motivo

Erano nella stessa lista del drillthrough. Non li ho fatti, e non per fretta:

- **un segnalibro** serve a mettere due viste sotto lo stesso spazio. Qui le due viste che
  varrebbe la pena alternare — ritardo e recensioni negative nel tempo — stanno gia' una
  accanto all'altra sulla pagina 3, e un segnalibro le nasconderebbe a turno per far vedere
  che so usare i segnalibri;
- **un parametro di campo** e' la stessa cosa con una tabella calcolata in piu' da tenere
  allineata;
- **la RLS** vuole dei ruoli. Qui non c'e' nessuno da separare da nessun altro: dovrei
  inventarmi un «responsabile di regione» che nei dati non esiste.

Sono tre cose che si mettono in un cruscotto perche' servono a chi lo legge, non perche'
compaiono in un annuncio di lavoro. Se un colloquio le chiede, la risposta e' questa.

### Il .pbix superato

Rinominato in `SUPERATO-delivery-delay-impact-13-08.pbix`. Era delle 13:08 e la sorgente e'
di sei ore dopo: due artefatti, uno solo vero, e nessuna indicazione di quale. Adesso
l'indicazione e' nel nome. Va rigenerato con Salva con nome o cancellato.

### Il file aperto, finalmente (26/08, 18:04)

Le tre cose che aspettavo di vedere funzionano: **i filtri a discesa ci stanno** nei 78
pixel, sull'asse della pagina 3 ci sono **venti mesi** da `gen 17` ad `ago 18`, e la
**serie grigia dell'anno prima e' vuota sul 2017 e piena dal 2018** — la marcatura come
tabella data fa quello che deve. Il drillthrough apre la pagina 5.

Ma il PDF ha mostrato due cose che nessun controllo vedeva.

**Le schede numeriche piccole restano bianche.** La quota del fatturato sotto il quarto
riquadro e il tasso di cambio nel piede: etichetta stampata, numero assente. Non e' un
errore di misura o di formato — **sotto una certa taglia Power BI la scheda non la disegna
proprio**, e non lo dice. Le due che sono uscite vuote erano 88x30 e 118x30; quelle che
funzionano in questo file sono 260x66 e piu' grandi.

Il rapporto col corpo del carattere, che era il criterio del controllo 7, **non discrimina
niente**: la scheda da 78 pixel con il numero da 40pt (rapporto 1,47) si vede benissimo,
quella da 30 pixel con il numero da 13pt (rapporto 1,73) e' vuota. Conta la taglia
assoluta. Il controllo adesso pretende **150x56** e la fascia di avviso graduata e' sparita,
perche' inventava una precisione che non ho.

Le due caselle sono state risolte in modo diverso, ed e' la parte che conta:

- la **quota del fatturato** e' un numero che si calcola sui dati, quindi resta una scheda:
  e' cresciuta a 150x60;
- il **tasso di cambio** e' una costante, e non ha bisogno di una scheda. `costante()` lo
  legge dal TMDL **mentre si genera la tela** e lo mette nel testo del piede. Il numero non
  e' battuto a mano lo stesso — se qualcuno cambia la misura, il piede cambia alla prossima
  generazione — e non dipende da quanto e' grande una casella.

**Le etichette delle barre erano abbreviate.** Sulla pagina 5 l'ultima fascia diceva `0K`
invece di 360 ordini: un arrotondamento che cancella il dato. `labelDisplayUnits` a 1, come
gia' era sui riquadri e non sui grafici.

### Lo script delle schermate ha convertito il PDF sbagliato

`trova_pdf()` prendeva il PDF piu' recente fra progetto, Download, Desktop e Documenti. Il
piu' recente era un **CV**, e lo script ne ha convertito la prima pagina salvandola come
`01-la-domanda.png`. Il controllo sul numero di pagine c'era e ha stampato l'avviso — poi
ha scritto lo stesso.

Due correzioni: il nome del PDF deve contenere `delivery-delay-impact`, e se le pagine non
sono cinque lo script **esce** invece di avvisare. Meglio nessuna schermata che la
schermata di un altro documento. Aggiunta anche la cartella temporanea dei lavori di stampa
di Power BI ai posti dove cercare: se invece di Esporta si usa Stampa, il PDF finisce li'.

### Le pagine 4 e 5 si scambiano di posto

`Dentro un mese` diventa la **4**, `Cosa NON dice` la **5**. Due motivi, e sono tutti e due
di lettura: il pannello dei limiti e' la chiusura del discorso e non un capitolo in mezzo,
e la pagina di dettaglio si raggiunge dalla 3, quindi le sta naturale accanto.

Lo scambio non e' solo nell'indice: sono stati scambiati anche i **prefissi dei visuali**
(`p4-` e `p5-`) e l'ordine dei due blocchi dentro `costruisci-report.py`. Lasciare il
codice che chiama `p4` la quinta pagina sarebbe stato un piccolo debito che costa ogni
volta che qualcuno ci torna sopra.

Le testate adesso contano cinque pagine — `PAGINA 4 DI 5` sostituisce il `DA UN MESE DELLA
PAGINA 3` che stava nell'angolo del dettaglio, e come ci si arriva resta scritto nel
sottotitolo. `schermate.py` segue il nuovo ordine.

### Il 8,8% si perdeva

Il numero della didascalia stava a 13pt accanto a un grigio chiaro da 9: si leggeva come
una nota a pie' di pagina, non come un dato. Sale a **20pt** e le parole accanto passano da
9 a 10 e da grigio chiaro a grigio scuro. La casella e' gia' 150x60, sopra la soglia sotto
la quale Power BI non disegna.

### Le schermate sono vecchie

`schermate/` contiene ancora le tre pagine del 26/08 mattina, senza filtri e senza la
pagina della tendenza. **Vanno rifatte**: export in PDF da Power BI Desktop, poi
`schermate.py`. Il nome dei file cambia, perche' le pagine adesso sono quattro e la terza
non e' piu' quella dei limiti.

## La prossima cosa, in concreto

**Tutto quello che restava e' fatto tranne la prima riga, e la prima riga vale per due.**

1. **Aprire `delivery-delay-impact.pbip`, aggiornare i dati e guardare le quattro pagine.**
   L'aggiornamento serve: `Etichetta mese` e' una colonna nuova. La lista di cosa
   controllare sta qui sopra. Niente di quello che e' stato fatto dopo le 13:08 e' mai
   comparso su uno schermo.
2. **Rifare le schermate**: export in PDF, poi `schermate.py`. Quattro pagine — i nomi che
   servono al README sono `01-la-domanda`, `02-di-chi-e-il-ritardo`, `03-come-cambia`,
   `04-cosa-non-dice`.
3. **Decidere del `.pbix`**: rigenerarlo con Salva con nome, o cancellarlo. Non lasciarlo
   li' vecchio di mezza giornata accanto alla sorgente.
4. **Secondo commit** con le schermate, e solo allora un `remote` e un push.
5. **La quarta card sul sito**, che nell'ordine di lavoro viene per ultima e ha bisogno di
   un repository pubblico a cui puntare.

## Una cosa ancora da decidere

- **La distanza geografica** (terza gamba della sotto-domanda 5) e' il pezzo piu' caro:
  un milione di righe da ridurre a un punto per CAP. **E' la prima cosa da tagliare** se
  i due-tre giorni si stringono.

## Cosa non e' stato fatto e perche'

- **Niente e' stato pulito fuori da Power Query.** L'esplorazione e' stata fatta in Python
  in sola lettura: nessun file di `dati_grezzi/` e' stato modificato, non esiste nessun
  CSV «pulito».
- **Il repository non e' ancora stato creato:** `C:\dev\_powerbi` non e' sotto git, non
  c'e' un README, e il lavoro non e' visibile a nessuno da fuori.
- **Nessuna analisi per mese di consegna.** La relazione fra `Ordini[data_consegna]` e il
  `Calendario` esiste ma resta inattiva: nessuna misura la attiva con `USERELATIONSHIP`.
  La pagina 3 ragiona per mese d'acquisto, e lo dichiara nel piede.
