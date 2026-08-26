# La domanda, scritta prima di aprire Power BI

Finche' questo file non e' deciso, Power BI resta chiuso.

Scritto prima di scaricare i dati. **Verificato il 23/08 sui dati veri**: le ipotesi che
erano marcate `[V]` sono state controllate una per una, e i risultati stanno in
`DATI-SPORCHI.md`. Dove la verifica ha cambiato qualcosa, il testo qui sotto e' stato
riscritto e la modifica e' segnata `[verificato]`.

---

## La domanda

> **I ritardi di consegna quanto ci costano in recensioni negative, e quali venditori
> li causano?**

E' il titolo del cruscotto. Non «Sales Dashboard», non «Olist Analytics».

**Il committente immaginabile:** chi in Olist decide se sospendere un venditore dal
marketplace. La domanda ha senso solo se la risposta cambia una decisione: *quali
venditori valgono un intervento, e quanto vale intervenire*.

## Le sotto-domande

Erano cinque, e sono le uniche a cui il cruscotto deve saper rispondere. Se una visualizzazione non
serve a una di queste, non entra nella tela.

1. **Quanti ordini arrivano dopo la data promessa al cliente**, e di quanti giorni.
   `order_delivered_customer_date` contro `order_estimated_delivery_date`.
2. **Come cambia il punteggio della recensione al crescere del ritardo.** E' il legame
   che regge tutto il cruscotto. `[verificato]` **Regge, e non e' una pendenza: e' un
   dirupo.** In orario voto 4,29 e 9% di recensioni negative; in ritardo voto 2,57 e
   **54%** negative. Ma tutto succede nei primi giorni oltre la promessa, e il numero
   riassuntivo (correlazione -0,18) direbbe il contrario del vero: **si mostrano le
   fasce, mai il coefficiente.**
3. **Quanto fatturato passa da ordini consegnati in ritardo** — l'ordine di grandezza
   che dice se la cosa merita un intervento. Prezzo piu' spedizione delle righe d'ordine.
4. **Quali venditori concentrano il ritardo**, normalizzato per volume e con una soglia
   minima di ordini dichiarata. Un venditore con 3 ordini e il 100% di ritardo non e' un
   problema, e' rumore.
5. **Di chi e' il ritardo.** La parte che distingue questo cruscotto da una classifica:
   spezzare il tempo di consegna in tre pezzi separati e vedere quale pesa.
   - *approvazione → affidamento al corriere* (`order_approved_at` →
     `order_delivered_carrier_date`): il pezzo che dipende dal **venditore**.
   - *affidamento → consegna* (`order_delivered_carrier_date` →
     `order_delivered_customer_date`): il pezzo che dipende dalla **logistica**.
   - *distanza* venditore-cliente, per CAP (serve la tabella geolocalizzazione, che va
     prima ridotta a un punto per CAP — vedi `DATI-SPORCHI.md` §9): quanto del ritardo
     e' semplicemente geografia e non colpa di nessuno.

   Senza questa scomposizione, «quali venditori li causano» e' una domanda a cui si
   risponde male: si finisce per punire chi spedisce lontano.

   `[verificato]` **Ed e' la sotto-domanda che ha cambiato il cruscotto.** Il venditore
   ci mette 1,2 giorni in piu' sugli ordini in ritardo; la logistica ne mette **17** in
   piu' (mediana da 6,9 a 23,9 giorni). Nessuna manciata di colpevoli: 1.390 venditori su
   2.970 producono almeno un ritardo, e i venti peggiori spiegano solo il 24% dei ritardi.
   **La seconda meta' del titolo ha una risposta scomoda: in larga parte non sono i
   venditori.** La pagina 2 smette di essere una classifica e diventa una scomposizione
   della responsabilita' — e la cosa si scrive in cima a quella pagina, non nel pannello
   dei limiti. Un cruscotto che proponesse di sospendere venditori per un problema di
   corrieri sarebbe peggio di nessun cruscotto.

6. **Sta migliorando o peggiorando?** `[aggiunta il 26/08]` Non era fra le cinque, ed e'
   un buco: le altre cinque guardano tutto il periodo insieme, e chi deve decidere se
   intervenire chiede prima di tutto se la cosa stia crescendo. Il `Calendario` per
   rispondere c'era gia'.

   `[verificato]` **Il ritardo e' piu' che raddoppiato.** Gennaio-agosto 2018 contro lo
   stesso periodo 2017: dal **4,2%** al **9,4%** di consegne oltre la promessa, e le
   recensioni negative dal **10,5%** al **13,3%**. Ma non e' una deriva costante: per
   quasi tutto il 2017 sta sotto il 4%, poi novembre 2017 fa **14,3%** e marzo 2018 fa
   **21,4%**, e giugno 2018 torna all'**1,4%**. Sono picchi.

   **E cambia di nuovo cosa si propone.** Un problema che si concentra in pochi mesi e'
   un problema di capacita' nei mesi di punta, non di venditori da sospendere: la stessa
   direzione della sotto-domanda 5, per una strada diversa. Il confronto vive solo su
   gennaio-agosto, che sono gli unici mesi presenti in tutti e due gli anni pieni.

## Il modello

Schema a stella. Questa e' la tabella del modello **costruito**: la prima stesura ne
prevedeva otto tabelle, e due non sono entrate. Le righe qui sotto sono quelle che stanno
nel `.SemanticModel`.

| Tabella | Tipo | Grana |
|---|---|---|
| `Ordini` | fatti | un ordine consegnato |
| `RigheOrdine` | fatti | una riga d'ordine (prodotto x venditore x ordine) |
| `Calendario` | dimensione | un giorno |
| `Clienti` | dimensione | un cliente-ordine |
| `Venditori` | dimensione | un venditore |
| `Prodotti` | dimensione | un prodotto (categoria gia' tradotta) |
| `ControlloStatiOrdine` | verbale | uno stato dell'ordine |
| `Misure` | contenitore | nessuna riga |

**`Pagamenti` e' fuori.** Nessuna delle cinque sotto-domande tocca il metodo o le rate di
pagamento. Caricarla avrebbe aggiunto una terza grana da tenere separata nelle misure in
cambio di niente.

**`Recensioni` e' fuori come tabella, e questa e' la scelta che vale la pena spiegare.**
`[verificato]` **547 ordini hanno piu' di una recensione, e 789 `review_id` compaiono su
piu' di un ordine**: la chiave dichiarata non e' una chiave. La prima stesura ne faceva
una tabella dei fatti a se'. Il modello costruito fa un passo prima: le recensioni sono
aggregate **in Power Query** (`RecensioniPerOrdine`, che non viene caricata) e quello che
entra in `Ordini` e' una colonna `voto`, cioe' la media dei punteggi di quell'ordine, piu'
`recensioni_sull_ordine` per ritrovare i 547.

Il motivo: nessuna misura del cruscotto interroga la singola recensione — servono il voto
per ordine e la percentuale di ordini con voto basso. Una tabella dei fatti in piu' avrebbe
solo aggiunto una grana da dichiarare in ogni misura.

Il prezzo, misurato invece che temuto: `Voto medio` e' una **media di medie**. Sui 95.824
ordini consegnati e recensiti vale **4,1562**, contro **4,1557** se si mediassero le 96.353
recensioni una per una. Lo scarto e' **0,0005**, cioe' niente alla seconda cifra. Su 547
ordini resta vero che il voto mostrato non e' un voto che qualcuno ha dato.

**Due relazioni verso il `Calendario`, una sola attiva.** Quella attiva e' su
`data_acquisto`: la pagina 3 legge la serie mensile per mese d'acquisto, ed e' scritto nel
piede della pagina. Quella su `data_consegna` resta **inattiva e non usata**: nessuna
misura la attiva con `USERELATIONSHIP`. E' li' per un'analisi per mese di consegna che non
e' stata fatta, e finche' non la fa qualcuno e' una scelta dichiarata, non una funzione.

**Il fatturato sta nelle righe, il ritardo sta negli ordini.** Ogni misura deve dichiarare
da quale delle due tabelle scende, altrimenti «fatturato degli ordini in ritardo» diventa
ambiguo.

**`Calendario` va creata a parte**, non derivata da una colonna dei fatti, e marcata come
tabella data: e' la trappola numero uno, e in questi dati e' viva.

## Le misure

Tutte in una tabella di misure dedicata, nessuna sparsa nelle tabelle dei fatti.

- Ordini consegnati; % consegnati in ritardo; giorni medi e mediani di ritardo.
- Punteggio medio recensione; % recensioni da 1 e 2 stelle.
- Fatturato; fatturato degli ordini consegnati in ritardo; la sua quota sul totale.
- Le tre durate del punto 5, medie e mediane.
- Confronti anno su anno con time intelligence. `[costruito]` `SAMEPERIODLASTYEAR`
  sulla serie mensile della pagina 3, piu' quattro misure a finestra fissa su
  gennaio-agosto. Funziona perche' `Calendario` e' contrassegnata come tabella
  data: e' quella marcatura a togliere dal calcolo il filtro di `Anno-mese` che
  arriva dall'asse del grafico.

**Media o mediana:** `[verificato]` **la coda c'e': ritardo medio 9,6 giorni, mediano
5,8, massimo 189.** La media la segue, la mediana no. Sui giorni si mostra la mediana e
si dice che e' la mediana. Sui voti la media va bene: e' una scala da 1 a 5, non ha coda.

## Il pannello «cosa questo cruscotto NON dice»

Progettato adesso, non aggiunto alla fine. Rivisto il 23/08 con i dati in mano: i numeri
qui sotto sono misurati, non stimati.

- **Il legame non e' una pendenza, e' un dirupo.** Fra dieci giorni di anticipo e la
  consegna appena in orario non succede quasi niente; fra 3 e 7 giorni di ritardo la
  maggioranza delle recensioni e' gia' negativa. Un indicatore riassuntivo su tutti gli
  ordini vale -0,18 e direbbe che il legame e' debole: e' il 92% di consegne in anticipo
  che schiaccia il numero. **Per questo qui non c'e' nessuna correlazione in vista.**
- **La recensione misura la percezione, non il danno.** Da questi dati non si puo' sapere
  se un cliente con una stella ha smesso di comprare: **96.096 persone per 99.441
  ordini**, il 97% compra una volta sola. Non c'e' un dopo da guardare.
- **Legame, non causa.** Ritardo e recensione bassa possono avere la stessa origine —
  un venditore lento puo' essere anche un venditore scadente. Il cruscotto misura che
  vanno insieme, non che uno produce l'altro.
- **«In ritardo» significa in ritardo rispetto a una promessa**, non rispetto a un tempo
  ragionevole. La stima la genera la piattaforma ed e' prudente: **quando un ordine arriva
  in orario, arriva 12,3 giorni prima della data promessa** (mediana). Allargare la stima
  farebbe sparire il ritardo senza consegnare prima — e il cruscotto non se ne
  accorgerebbe.
- **La colpa si divide solo fin dove arrivano i timestamp.** Quello che succede dentro il
  corriere non e' nei dati. E su **1.388 ordini** i timestamp stessi sono incoerenti
  (partiti prima di essere approvati): quelli escono dalle misure per fase, e sono
  contati.
- **1.278 ordini hanno piu' di un venditore.** Il ritardo e' dell'ordine, il venditore e'
  della riga: attribuirlo a tutti li conta piu' volte. Sono l'1,3%, ma la scelta e'
  dichiarata.
- **Il pezzo mancante e' il costo di rimediare.** Il cruscotto dice quanto fatturato passa
  di li', non quanto costerebbe evitarlo: senza quello non decide, informa chi decide.
- **Dati 2016-2018, un solo marketplace, Brasile.** Non sono un riferimento per nessun
  altro. E il periodo utile e' **gennaio 2017 - agosto 2018**: il 2016 sono 329 ordini in
  tutto, **novembre 2016 non esiste**, e settembre-ottobre 2018 sono venti ordini di coda
  del dump. Il confronto anno su anno vive solo su gennaio-agosto.
- **2.963 ordini non consegnati sono esclusi** (annullati, non disponibili, ancora in
  viaggio), piu' 8 ordini marcati come consegnati ma senza data di consegna. Il cruscotto
  parla dei 96.470 arrivati: **degli annullati non dice niente**, e un venditore che fa
  annullare invece di consegnare tardi qui sembra migliore.
- **La soglia minima per venditore e' 30 ordini consegnati**, ed e' una scelta, non un
  dato: tiene 627 venditori sui 2.970 con almeno una consegna — il 21% di loro, ma l'83,5%
  degli ordini. Sotto quella soglia le percentuali sono rumore, e i 2.343 venditori
  esclusi non sono «a posto»: sono **non misurabili**.
- **Due basi diverse convivono nel cruscotto:** i 96.470 ordini consegnati e i 95.824
  consegnati *e recensiti*. Le misure sui tempi girano sulla prima, quelle sui voti sulla
  seconda, e ogni numero dice quale usa. Confonderle e' un errore che non da' errore.
- **Le citta' sono scritte in piu' modi** (`sao paulo`, `sao paulo - sp`, `sp`,
  `sao paulo / sao paulo`). Normalizzate, ma il raggruppamento affidabile e' lo **stato**.
  E per **278 CAP di clienti** e 7 di venditori non esiste una coordinata: quegli ordini
  non entrano in nessun calcolo di distanza.

## Cosa NON si costruisce

- Nessuna ciambella, nessuna mappa di calore decorativa, nessun contatore che non risponde
  a una delle cinque domande.
- Nessuna pagina «panoramica vendite»: e' il cruscotto di tutti gli altri.
- Nessuna previsione. I dati finiscono nel 2018 e non c'e' niente da prevedere.
