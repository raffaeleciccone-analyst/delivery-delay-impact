# Power BI — impianto

Scritto il **23 agosto 2026**, deciso di farlo prima della Premier. Questo documento
contiene **solo cio' che il codice non dice**: decisioni, motivi, ordine, trappole.

Ogni fatto misurato porta accanto il comando o il link che lo rimisura. Non fidarti
dei numeri scritti qui: sono di agosto 2026, e i piani gratuiti cambiano.

---

## Perche' questo prima della Premier

Tre motivi, in ordine di peso.

1. **Power BI, Power Query e Data Modeling sono gia' dichiarati sul CV** e non hanno
   niente dietro. E' l'unica competenza in quella condizione. Se in colloquio qualcuno
   chiede «mostrami», oggi non c'e' cosa.
2. **E' la parola chiave che filtra gli annunci italiani** da data analyst. La Premier
   non aggiunge nulla a quel filtro.
3. **Chiude l'ultimo buco rimasto.** Dopo il caso di mercato, l'unica obiezione ancora in
   piedi e' *«tutti i tuoi dati te li sei scelti tu»*. La Premier la **peggiora**: e'
   ancora calcio, ancora scelto da lui. Solo un dataset di business esterno la chiude.

Stimato **2-3 giorni**. La Premier ne costa 4-6 (vedi `C:\dev\_premier\HANDOFF.md`).

---

## Le tre decisioni

### 1. Dataset: Olist, e-commerce brasiliano

**Perche' lui e non un altro.** Tre requisiti, tutti necessari:

- **Un committente immaginabile.** Se non si riesce a dire *chi* ha commissionato
  l'analisi, la domanda non e' di business.
- **Dati sporchi.** Duplicati, resi, mancanti, categorie scritte in tre modi. E' meta'
  del mestiere e non lo mostra quasi nessuno.
- **Piu' tabelle collegate.** Serve per lo schema a stella. Un CSV piatto non permette
  di dimostrare che si sa modellare — ed e' proprio la modellazione la parte che
  distingue un cruscotto da un grafico.

Olist ha **nove tabelle collegate** (ordini, righe d'ordine, prodotti, clienti,
venditori, pagamenti, recensioni, geolocalizzazione, traduzione delle categorie) e circa
centomila ordini. Lo schema a stella viene da se'.

**Verificare prima di partire:** numero di tabelle e di righe, e soprattutto la
**licenza**, prima di ripubblicare dati o grafici.

**Da evitare:** Titanic, Iris, Superstore, il dataset Netflix. Puliti, usati da chiunque,
riconoscibili a colpo d'occhio come esercizio. Tolgono credibilita' invece di darne.

**Alternativa tenuta da parte:** Online Retail II (UCI), ~1M transazioni UK 2009-2011,
sporco per davvero — quantita' negative per i resi, cancellazioni, ID cliente mancanti.
Domanda: *quali clienti stanno per smettere di comprare e quanto vale trattenerli?*
Serve se Olist si rivela troppo pulito.

### 2. La domanda, prima del canvas

Il titolo del cruscotto e' **la decisione**, non l'argomento. Non «Sales Dashboard»:

> **I ritardi di consegna quanto ci costano in recensioni negative, e quali venditori
> li causano?**

Da li' discende tutto: quali tabelle servono, quali misure, cosa si filtra. Aprire Power
BI prima di aver scritto la domanda e' il modo piu' rapido di produrre il cruscotto di
tutti gli altri.

### 3. Il pannello «cosa questo cruscotto NON dice»

E' la firma. Ha scritto un modello di minaccia su NLDA, pubblica le verifiche fallite sul
Serie A, e sul caso di mercato ha messo in fondo che sommare i TPI e' un'approssimazione.
In un Power BI questa cosa non si vede quasi mai: e' cio' che lo rende riconoscibile come
suo invece che come il novantesimo cruscotto uguale.

Va progettato **insieme** al resto, non aggiunto alla fine.

---

## Il problema della registrazione — risolverlo per primo

**Il servizio online di Power BI vuole un indirizzo aziendale o scolastico. Con una gmail
la registrazione non passa.** Verificato come vincolo noto, da riverificare perche' le
regole cambiano.

Raffaele **non ha** un'email scolastica (chiesto il 23/08). Tre strade, in ordine:

1. **Chiedere all'ITS Agnesi** se rilascia un indirizzo di posta o un accesso Microsoft
   per studenti. Molti istituti lo fanno, e risolve tutto a costo zero. **Prima cosa da
   fare, e' una mail alla segreteria.**
2. **Power BI Desktop e' gratuito e non ha il problema.** Il piano B di consegna:
   `.pbix` scaricabile dal repo + schermate + una breve registrazione del giro.
   Per superare il filtro degli annunci basta.
3. **Tableau Public** solo come ripiego se serve davvero l'interattivita' pubblica
   gratis. E' un'altra parola chiave, quindi e' un'altra cosa: non farlo *invece*.

**Non aspettare la risposta dell'ITS per cominciare.** Il lavoro si fa in Desktop
comunque; la pubblicazione e' l'ultimo passo.

---

## L'ordine delle operazioni

1. **Mandare la mail all'ITS** sull'account Microsoft. Costa due minuti e la risposta
   arriva mentre si lavora.
2. **Scaricare il dataset e congelarlo.** Una volta sola, poi sotto versione. Se la
   fonte cambia sotto i piedi, i numeri smettono di essere riproducibili — e' la stessa
   disciplina di `_premier\HANDOFF.md`.
3. **Scrivere la domanda per esteso**, prima di aprire Power BI. Una frase, quella del
   titolo.
4. **Esplorare i dati e trovare lo sporco.** Annotare cosa e' rotto *mentre* si trova,
   non dopo: serve per il passo 5 e per il pannello finale.
5. **Power Query: pulire, documentando ogni passaggio.** Ogni passaggio prende un nome
   che dice cosa fa. Sono le note che diventano la sezione «dati sporchi dichiarati».
6. **Costruire il modello**: schema a stella, **tabella data separata** creata a parte
   (non derivata da una colonna dei fatti), relazioni uno-a-molti verificate una per una.
7. **Misure DAX**, con time intelligence e confronti anno su anno. Le misure stanno in
   una tabella di misure dedicata, non sparse nelle tabelle dei fatti.
8. **La tela**, per ultima. Se la domanda del passo 3 e' buona, il layout quasi si
   scrive da solo.
9. **Il pannello «cosa NON dice»**.
10. **Consegna**: repository con `.pbix`, schermate, README che riporta la domanda e le
    scelte di modellazione. Pubblicazione online se il passo 1 l'ha sbloccata.

---

## Le trappole

**Il cruscotto templato e' il rischio numero uno.** Il novanta per cento delle dashboard
da portfolio e' lo stesso dataset con le stesse ciambelle. Sarebbe l'artefatto piu'
banale del suo portfolio, l'opposto di tutto il resto. Le quattro cose che lo rendono
suo: la domanda al posto del titolo, il modello mostrato, i dati sporchi dichiarati, il
pannello dei limiti.

**Una sola dashboard, non due.** Deciso il 22/08. Due cruscotti non leggono come due
competenze, leggono come «fa cruscotti»: il tool e' segnale a buon mercato, la domanda a
cui risponde e' quello caro. E raddoppiare l'artefatto significa due cose mediocri, che
e' peggio di una fatta bene — un cruscotto e' l'oggetto piu' confrontabile che esista.

**Niente cruscotto di calcio.** Esiste gia' ed e' migliore: `dashboard_serie_a.html` ha
filtri, cinque contesti, confronto testa a testa, venti pagine squadra ed export CSV del
filtrato. Una versione Power BI sarebbe una copia peggiore di una cosa gia' online, e non
toccherebbe il buco vero.

**La tabella data va creata, non derivata.** Senza una tabella calendario separata e
marcata come tale, la time intelligence in DAX da' risultati sbagliati in silenzio nei
mesi senza vendite. E' l'errore piu' comune e non da' nessun errore.

**Congelare i dati grezzi prima di toccarli.** Vedi passo 2.

---

## Cosa non fare

- **Non aprire Power BI prima di aver scritto la domanda.**
- **Non dichiarare Power BI come competenza acquisita finche' questo non e' finito.**
  Sul CV c'e' gia' e viene dall'ITS: e' legittimo, ma resta l'unica voce senza prova.
- **Non mettere mai co-autori o firme di strumenti nei commit**, in nessun repo.

---

## Quando questo e' finito

**La certificazione PL-300 (Microsoft Certified: Power BI Data Analyst)** costa circa
150 euro — verificare — ed e' la spesa col miglior rapporto fra costo e risultato che ha
a disposizione: mette una credenziale verificabile accanto a una parola chiave che a quel
punto avra' anche un artefatto dietro. Molto meglio di una laurea telematica, per lo
stesso obiettivo e a un centesimo del prezzo.

---

## Riferimenti

- Piano completo del portfolio: `C:\dev\portfolio\PORTFOLIO-HANDOFF.md`
- Il lavoro dopo questo: `C:\dev\_premier\HANDOFF.md`
- Corso ITS di riferimento: <https://www.itsagnesi.it/corso-data-analyst/>
  (Statistica, Python, Power BI, SQL, Data Visualization, Machine Learning,
  Data Engineering, Data Governance — 1.080 ore d'aula, 720 di stage)
