# Come si incollano queste query

Power BI Desktop e' in italiano; i nomi dei comandi sono quelli della versione 26.08.

## Una volta sola, prima di cominciare

1. **Salva subito il file** come `C:\dev\_powerbi\delivery-delay-impact.pbix`, cosi' non si lavora su
   qualcosa senza nome.
2. Apri **Home -> Trasforma dati** (si apre l'editor di Power Query).
3. Non serve toccare le impostazioni internazionali: **ogni query dichiara `"en-US"` da
   sola** dove converte i tipi. E' piu' sicuro che cambiare un'opzione globale, perche' il
   file resta corretto anche aperto su un altro computer.

## Per ogni query, sempre lo stesso giro

1. Nell'editor: **Home -> Nuova origine -> Query vuota**.
2. **Home -> Editor avanzato**.
3. Cancella tutto quello che c'e' dentro e incolla il contenuto del file `.m`.
4. **Fine**.
5. Rinomina la query nel pannello a sinistra: **il nome deve essere esattamente quello
   scritto nella prima riga del file** (`PercorsoDati`, `OrdiniGrezzi`, ...), altrimenti le
   query che la richiamano non la trovano.

**L'ordine conta.** `PercorsoDati` per prima, poi `OrdiniGrezzi`, poi le altre.

## I file di questo primo blocco, in ordine

**L'ordine e' questo, e non e' quello dei numeri nei nomi dei file.** Ogni query puo'
richiamare solo quelle create prima: `Ordini` richiama `RecensioniPerOrdine`, quindi
quella va creata per prima.

| # | File | Nome della query | Righe attese | Nel modello? |
|---:|---|---|---:|---|
| 1 | `00-PercorsoDati.m` | `PercorsoDati` | — (e' un testo) | **no** |
| 2 | `01-OrdiniGrezzi.m` | `OrdiniGrezzi` | 99.441 | **no** |
| 3 | `05-RecensioniPerOrdine.m` | `RecensioniPerOrdine` | 98.673 | **no** |
| 4 | `02-Ordini.m` | `Ordini` | 96.470 | si |
| 5 | `03-ControlloStatiOrdine.m` | `ControlloStatiOrdine` | 8 | si |
| 6 | `04-RigheOrdine.m` | `RigheOrdine` | 112.650 | si |

Se hai gia' incollato `Ordini` e ti da' *«Il nome 'RecensioniPerOrdine' non e' stato
riconosciuto»*: non cancellare niente. Crea `RecensioniPerOrdine` con lo stesso giro, e
l'errore su `Ordini` sparisce da solo appena la query esiste.

**Tre query non vanno caricate nel modello** — `PercorsoDati`, `OrdiniGrezzi` e
`RecensioniPerOrdine`: tasto destro sulla query -> togli la spunta a **Abilita
caricamento**. Sono ingredienti delle altre, non tabelle. Restano nell'editor e
continuano a funzionare.

## Alla prima esecuzione

Power BI chiedera' i **livelli di privacy** per l'accesso ai file: scegli **Pubblico**.
E' un dataset scaricato, non c'e' niente da proteggere, e lasciare la domanda in sospeso
blocca l'aggiornamento.

## Come si legge il numero delle righe

In fondo all'editor, sotto l'anteprima, c'e' la barra di stato: *«N righe, M colonne»*.
Se dice **«anteprima scaricata alle ...»** senza il conteggio, clicca sul passaggio finale
nel pannello di destra e aspetta che finisca di contare.

## I due controlli che non vanno saltati

- **Recensioni deve avere 99.224 righe prima del raggruppamento.** Clicca sul passaggio
  `Tipi dichiarati in en-US` e guarda il conteggio. Se sono **104.719**, `QuoteStyle` non
  ha funzionato e il file si e' spezzato sugli a capo dentro i commenti.
- **In RigheOrdine, `price` deve mostrare `58,90` e non `5890`.** Se e' il secondo, la
  conversione ha ereditato le impostazioni italiane e il fatturato e' cento volte troppo.

Quando questi cinque caricano con le righe giuste, si passa al blocco seguente
(dimensioni, calendario) e poi alla riconciliazione di `RICONCILIAZIONE.md`.
