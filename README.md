# I ritardi di consegna quanto costano in recensioni negative

Analisi in Power BI sul marketplace brasiliano Olist: 96.470 ordini consegnati fra
settembre 2016 e ottobre 2018. I dati sono il dump pubblico che Olist ha rilasciato su
Kaggle, licenza CC BY-NC-SA 4.0, e non sono nel repository: come scaricarli sta più sotto.

La domanda è stata scritta prima di aprire Power BI, in `DOMANDA.md`, e il cruscotto
risponde a quella e a nient'altro.

---

## Cosa dicono i dati

**Il ritardo è raro e costa molto.** L'8,1% degli ordini arriva dopo la data promessa al
cliente. Su quelli il voto medio scende da 4,29 a 2,57 e le recensioni negative passano
dal 9,2% al **54,0%**.

**Il legame non è una pendenza, è un dirupo.** Fra dieci giorni di anticipo e la consegna
appena in orario le recensioni negative passano dall'8,9% all'11,0%. Fra 3 e 7 giorni di
ritardo sono già il 61,3%. Un coefficiente di correlazione su tutti gli ordini varrebbe
−0,18, cioè «legame debole»: è schiacciato dal 92% di consegne in anticipo. Per questo nel
cruscotto non c'è nessuna correlazione, ci sono le fasce.

**Il ritardo non si forma dal venditore.** Spezzando il tempo di consegna nei due
intervalli che i dati registrano: sugli ordini in ritardo il venditore impiega 1,2 giorni
in più del solito, la logistica ne impiega **17**. E non esiste una manciata di colpevoli:
1.390 venditori su 2.970 producono almeno un ritardo, e i venti peggiori spiegano il 24%
del totale.

**Sta peggiorando, a picchi.** Gennaio-agosto 2018 contro lo stesso periodo 2017: dal 4,2%
al 9,4% di consegne oltre la promessa. Ma per quasi tutto il 2017 il ritardo sta sotto il
4%, poi novembre 2017 fa 14,3% e marzo 2018 fa 21,4%, e giugno 2018 torna all'1,4%.

Messe insieme, le ultime due cambiano cosa si propone: un problema di capacità nei mesi di
punta, non venditori da sospendere.

---

## Le pagine

![La domanda](schermate/01-la-domanda.png)

![Di chi è il ritardo](schermate/02-di-chi-e-il-ritardo.png)

![Come cambia](schermate/03-come-cambia.png)

![Dentro un mese](schermate/04-dentro-un-mese.png)

![Cosa non dice](schermate/05-cosa-non-dice.png)

La quarta pagina si apre anche col tasto destro su un mese del grafico della terza, e mostra
per quel mese quanto era lungo il ritardo e da quale delle due fasi arrivava. Passando il
mouse su una fascia della prima pagina si apre un riquadro con gli ordini, il voto e il
fatturato di quella fascia.

L'ultima pagina non è un'appendice: è stata progettata insieme alle altre, prima di
costruirle. Elenca cosa l'analisi **non** può dire — che la recensione misura la
percezione e non il danno, che «in ritardo» è rispetto a una promessa e non a un tempo
ragionevole, che manca il costo di rimediare e quindi il cruscotto informa chi decide ma
non decide.

---

## Il modello

![Il modello](schermate/06-modello.svg)

Schema a stella: due tabelle dei fatti a grana diversa (l'ordine e la riga d'ordine),
quattro dimensioni, una tabella di sole misure e una tabella di controllo con il conteggio
degli stati dell'ordine.

Le decisioni che sono costate qualcosa:

- **Il fatturato sta nelle righe, il ritardo sta negli ordini.** Ogni misura dichiara da
  quale delle due scende, altrimenti «fatturato degli ordini in ritardo» è ambiguo.
- **Le recensioni non sono una tabella.** 547 ordini hanno più di una recensione e 789
  `review_id` compaiono su più ordini: la chiave dichiarata non è una chiave. Il voto per
  ordine è una media, calcolata in Power Query. Il prezzo è misurato: la media delle medie
  vale 4,1562 contro 4,1557 delle recensioni una per una, cioè 0,0005.
- **Il calendario è creato, non derivato** da una colonna dei fatti, e contrassegnato come
  tabella data. Serve perché novembre 2016 non ha nessun ordine: un calendario derivato
  salterebbe quel mese e l'intelligenza temporale sbaglierebbe in silenzio.
- **Due basi convivono:** 96.470 ordini consegnati per i tempi, 95.824 anche recensiti per
  i voti. Ogni misura dice quale usa. Confonderle produce numeri plausibili e sbagliati.
- **Soglie dichiarate:** un venditore sotto i 30 ordini consegnati non entra nei conteggi
  per venditore, uno stato sotto i 100 non entra nel grafico per stato. Non sono «a posto»:
  sono non misurabili.
- **Gli importi sono in euro**, convertiti dai reais alla media dei cambi mensili BCE del
  periodo pesata per il fatturato. Il tasso è una misura del modello, non un numero scritto
  in una nota. Convertire mese per mese sposterebbe il totale dello 0,02%; usare il cambio
  di un anno solo lo sposterebbe del 9%.

---

## Com'è costruito

Il progetto è in formato `.pbip`, quindi modello e report sono file di testo sotto
controllo di versione. Nessuno dei due è disegnato a mano:

| File | Cosa fa |
|---|---|
| `power-query/*.m` | le query, una per tabella, con i controlli di riga attesi nei commenti |
| `costruisci-modello.ps1` | monta tabelle, relazioni e 39 misure DAX e scrive il TMDL |
| `costruisci-report.py` | scrive le pagine in PBIR, un JSON per visuale: quattro pagine, una di dettaglio e un riquadro al mouse |
| `verifica-tela.py` | otto controlli sulla tela, senza aprire Power BI |
| `diagramma-modello.py` | disegna il diagramma leggendo il TMDL, non fotografando lo schermo |

`verifica-tela.py` controlla che ogni misura e ogni colonna citata esista, che niente esca
dalla tela o si sovrapponga, che tutto stia sulla griglia a dodici colonne, che il testo e
i numeri ci stiano nelle loro caselle (Power BI il testo di troppo non lo taglia: ci mette
una barra di scorrimento) e che nessuna misura del modello giri a vuoto.

Il diagramma è disegnato dal TMDL invece che catturato dalla vista Modello: se il modello
cambia, il disegno cambia con lui.

---

## Rifarlo

I dati non sono nel repository: sono il dump pubblico
[Brazilian E-Commerce di Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
su Kaggle, licenza CC BY-NC-SA 4.0, 164 MB. Vanno scaricati e scompattati in
`dati_grezzi/csv/`; il percorso compare in un punto solo,
`power-query/00-PercorsoDati.m`.

```
powershell -ExecutionPolicy Bypass -File costruisci-modello.ps1
python costruisci-report.py
python verifica-tela.py
```

Poi si apre `delivery-delay-impact.pbip` con Power BI Desktop e si aggiornano i dati.
Il modello viene riletto dallo script stesso appena scritto, così un errore di formato si
vede lì e non aprendo il file.

---

## I documenti

Il lavoro è documentato mentre si faceva, non dopo:

| File | Cosa contiene |
|---|---|
| `DOMANDA.md` | la domanda e le sei sotto-domande, scritte prima di aprire Power BI, poi verificate una per una sui dati |
| `DATI-SPORCHI.md` | tredici problemi trovati esplorando i CSV, con il passaggio di Power Query che li tratta |
| `RICONCILIAZIONE.md` | i numeri che il modello deve riprodurre, e il loro esito |
| `STATO.md` | il diario: cosa è stato fatto, cosa è stato sbagliato e come se n'è usciti |

Il criterio in `RICONCILIAZIONE.md`: se il cruscotto e i documenti dicono numeri diversi,
mentono i documenti. Ogni scarto trovato è stato risolto correggendo il documento e
tenendo il valore misurato dal motore.

---

Dati Olist (Kaggle, CC BY-NC-SA 4.0), scaricati e congelati il 23 agosto 2026.
Cambi BCE, serie `EXR.M.BRL.EUR.SP00.A`.
