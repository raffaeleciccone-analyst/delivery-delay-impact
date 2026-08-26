# Costruisce il modello semantico dell'analisi e lo scrive in TMDL.
#
# Non tocca i dati: legge le query M da power-query\*.m e monta tabelle,
# relazioni e misure con le API di Power BI. Alla fine rilegge quello che ha
# scritto, cosi' un errore di formato si vede qui e non aprendo il file.
#
# Uso:  powershell -ExecutionPolicy Bypass -File costruisci-modello.ps1

$ErrorActionPreference = "Stop"

$bin = "C:\Program Files\Microsoft Power BI Desktop\bin"
Add-Type -Path "$bin\Microsoft.PowerBI.Tabular.dll"

$radice   = "C:\dev\_powerbi"
$pq       = Join-Path $radice "power-query"
$cartella = Join-Path $radice "delivery-delay-impact.SemanticModel"

function Leggi-M($file) {
    $p = Join-Path $pq $file
    if (-not (Test-Path $p)) { throw "manca il file $p" }
    # via i commenti di intestazione: restano nel repo, non nel modello
    (Get-Content $p -Raw -Encoding UTF8).Trim()
}
function Tipo($nome) { [Enum]::Parse([Microsoft.AnalysisServices.Tabular.DataType], $nome) }

# ---------------------------------------------------------------- il contenitore
$db = New-Object Microsoft.AnalysisServices.Tabular.Database
$db.Name = "delivery-delay-impact"
$db.CompatibilityLevel = 1606
$db.Model = New-Object Microsoft.AnalysisServices.Tabular.Model
$mod = $db.Model
$mod.Name = "Model"
$mod.Culture = "it-IT"
# le date e i numeri dei file sono americani: lo diciamo al modello
$mod.SourceQueryCulture = "en-US"
# senza questa, il motore rifiuta il modello: accetta solo di salire di versione
$mod.DefaultPowerBIDataSourceVersion = [Microsoft.AnalysisServices.Tabular.PowerBIDataSourceVersion]::PowerBI_V3

# ------------------------------------------------- le query che NON sono tabelle
# Sono ingredienti: un percorso, e tre passaggi intermedi. Restano nell'editor
# ma non diventano tabelle del modello.
$espressioni = @(
    @{ Nome = "PercorsoDati";        File = "00-PercorsoDati.m" },
    @{ Nome = "OrdiniGrezzi";        File = "01-OrdiniGrezzi.m" },
    @{ Nome = "RecensioniPerOrdine"; File = "05-RecensioniPerOrdine.m" },
    @{ Nome = "CategorieTradotte";   File = "08-CategorieTradotte.m" }
)
foreach ($e in $espressioni) {
    $ne = New-Object Microsoft.AnalysisServices.Tabular.NamedExpression
    $ne.Name = $e.Nome
    $ne.Kind = [Microsoft.AnalysisServices.Tabular.ExpressionKind]::M
    $ne.Expression = (Leggi-M $e.File)
    $mod.Expressions.Add($ne)
}

# ------------------------------------------------------------------- le tabelle
function Aggiungi-Tabella($nome, $file, $colonne, $descrizione) {
    # PowerShell srotola un array di un solo elemento: se succede, lo riavvolgo
    if ($colonne.Count -gt 0 -and $colonne[0] -is [string]) { $colonne = @(, $colonne) }

    $t = New-Object Microsoft.AnalysisServices.Tabular.Table
    $t.Name = $nome
    if ($descrizione) { $t.Description = $descrizione }

    $p = New-Object Microsoft.AnalysisServices.Tabular.Partition
    $p.Name = $nome
    $p.Mode = [Microsoft.AnalysisServices.Tabular.ModeType]::Import
    $src = New-Object Microsoft.AnalysisServices.Tabular.MPartitionSource
    $src.Expression = (Leggi-M $file)
    $p.Source = $src
    $t.Partitions.Add($p)

    foreach ($c in $colonne) {
        $col = New-Object Microsoft.AnalysisServices.Tabular.DataColumn
        $col.Name = $c[0]
        $col.SourceColumn = $c[0]
        $col.DataType = (Tipo $c[1])
        if ($c.Count -ge 3 -and $c[2]) { $col.Description = $c[2] }
        # il quarto elemento e' il nome da mostrare, quando quello della
        # sorgente non e' presentabile; il quinto il formato del numero
        if ($c.Count -ge 4 -and $c[3]) { $col.Name = $c[3] }
        if ($c.Count -ge 5 -and $c[4]) { $col.FormatString = $c[4] }
        $t.Columns.Add($col)
    }
    $mod.Tables.Add($t)
    $t
}

$null = Aggiungi-Tabella "Ordini" "02-Ordini.m" @(
    @("order_id", "String", "chiave dell'ordine"),
    @("customer_id", "String", "chiave cliente-ordine, NON la persona (vedi Clienti)"),
    @("order_status", "String"),
    @("order_purchase_timestamp", "DateTime"),
    @("order_approved_at", "DateTime"),
    @("order_delivered_carrier_date", "DateTime"),
    @("order_delivered_customer_date", "DateTime"),
    @("order_estimated_delivery_date", "DateTime", "data PROMESSA al cliente, non una previsione"),
    @("giorni_ritardo", "Double", "positivo = in ritardo; negativo = margine di anticipo"),
    @("in_ritardo", "Boolean"),
    @("esito_consegna", "String", "in orario / in ritardo, in parole invece che Vero-Falso"),
    @("fascia_ritardo", "String", "serve a mostrare il dirupo: il legame non e' una pendenza"),
    @("fascia_ordine", "Int64", "ordina le fasce; l'ordine alfabetico sarebbe sbagliato"),
    @("giorni_fase_venditore", "Double", "approvazione -> affidamento al corriere"),
    @("giorni_fase_logistica", "Double", "affidamento al corriere -> consegna"),
    @("cronologia_ok", "Boolean", "falso su 1.388 ordini con timestamp incoerenti: escono dalle misure di durata"),
    @("data_acquisto", "DateTime"),
    @("data_consegna", "DateTime"),
    @("voto", "Double", "media dei punteggi quando l'ordine ha piu' di una recensione"),
    @("recensioni_sull_ordine", "Int64"),
    @("voto_negativo", "Boolean", "voto <= 2"),
    @("recensito", "Boolean", "distingue le due basi: 96.470 consegnati, 95.824 recensiti")
) "Un ordine consegnato. Base dei tempi e dei venditori."

$null = Aggiungi-Tabella "RigheOrdine" "04-RigheOrdine.m" @(
    @("order_id", "String"),
    @("order_item_id", "Int64"),
    @("product_id", "String"),
    @("seller_id", "String"),
    @("shipping_limit_date", "DateTime", "scadenza contrattuale, arriva al 2020: NON collegata al calendario"),
    @("price", "Double"),
    @("freight_value", "Double"),
    @("valore_riga", "Double", "price + freight_value")
) "Una riga d'ordine. Qui sta il fatturato."

# I nomi della sorgente finiscono sotto gli occhi di chi legge, perche' questa
# tabella si mostra tal quale: "order_status" e un 96478 senza punto delle
# migliaia dicono che il file non e' stato finito.
$null = Aggiungi-Tabella "ControlloStatiOrdine" "03-ControlloStatiOrdine.m" @(
    @("order_status", "String", $null, "Stato dell'ordine"),
    @("ordini", "Int64", $null, "Ordini", "#,0"),
    @("nell_analisi", "Boolean")
) "Conta gli ordini esclusi per stato. NON collegata di proposito: deve mostrare sempre tutti gli 8 stati, anche quando l'analisi e' filtrata."

$null = Aggiungi-Tabella "Clienti" "06-Clienti.m" @(
    @("customer_id", "String", "chiave: una per ordine"),
    @("customer_unique_id", "String", "la persona: 96.096 contro 99.441 ordini"),
    @("cap", "Int64"),
    @("citta", "String", "normalizzata; per raggruppare e' piu' affidabile lo stato"),
    @("stato", "String")
) "Dimensione cliente."

$null = Aggiungi-Tabella "Venditori" "07-Venditori.m" @(
    @("seller_id", "String"),
    @("cap", "Int64"),
    @("citta", "String"),
    @("stato", "String")
) "Dimensione venditore. La soglia dei 30 ordini sta nelle misure, non qui."

$null = Aggiungi-Tabella "Prodotti" "09-Prodotti.m" @(
    @("product_id", "String"),
    @("categoria", "String", "tradotta dove possibile; '(non indicata)' per i 610 senza"),
    @("categoria_tradotta", "Boolean", "falso per pc_gamer e portateis_cozinha_...: non hanno traduzione"),
    @("categoria_originale", "String"),
    @("peso_g", "Int64")
) "Dimensione prodotto."

$cal = Aggiungi-Tabella "Calendario" "10-Calendario.m" @(
    @("Data", "DateTime"),
    @("Anno", "Int64"),
    @("Numero mese", "Int64"),
    @("Mese", "String"),
    @("Anno-mese", "String"),
    @("Trimestre", "String"),
    @("periodo_utile", "Boolean", "gennaio 2017 - agosto 2018"),
    @("confrontabile", "Boolean", "mesi presenti in entrambi gli anni pieni: gennaio-agosto"),
    @("Etichetta mese", "String", "quella che va sull'asse: gen 17, feb 17, ...")
) "Tabella data creata, non derivata. Novembre 2016 non ha ordini e deve restare visibile."

# marcata come tabella data: senza, l'intelligenza temporale non ha garanzie
$cal.DataCategory = "Time"
$cal.Columns["Data"].IsKey = $true

# l'etichetta si ordina per "Anno-mese" ("2017-01"), non alfabeticamente:
# altrimenti sull'asse "ago 17" verrebbe prima di "gen 17"
$cal.Columns["Etichetta mese"].SortByColumn = $cal.Columns["Anno-mese"]

# le fasce si ordinano per la colonna apposita, non alfabeticamente
$ord = $mod.Tables["Ordini"]
$ord.Columns["fascia_ritardo"].SortByColumn = $ord.Columns["fascia_ordine"]
$ord.Columns["fascia_ordine"].IsHidden = $true

# tabella-contenitore per le misure: una colonna sola, nascosta
$mis = Aggiungi-Tabella "Misure" "99-Misure.m" @(
    @("segnaposto", "String")
) "Contiene solo misure."
$mis.Columns["segnaposto"].IsHidden = $true

# --------------------------------------------------------------- le relazioni
function Aggiungi-Relazione($daTab, $daCol, $aTab, $aCol, $attiva) {
    $r = New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship
    # un nome leggibile: il modello si legge anche in un diff, non solo a schermo
    $r.Name = "$daTab.$daCol -> $aTab.$aCol"
    $r.FromColumn = $mod.Tables[$daTab].Columns[$daCol]
    $r.ToColumn   = $mod.Tables[$aTab].Columns[$aCol]
    $r.FromCardinality = [Microsoft.AnalysisServices.Tabular.RelationshipEndCardinality]::Many
    $r.ToCardinality   = [Microsoft.AnalysisServices.Tabular.RelationshipEndCardinality]::One
    $r.IsActive = $attiva
    $mod.Relationships.Add($r)
}

# schema a stella: i fatti puntano alle dimensioni, mai il contrario
Aggiungi-Relazione "RigheOrdine" "order_id"   "Ordini"     "order_id"    $true
Aggiungi-Relazione "Ordini"      "customer_id" "Clienti"   "customer_id" $true
Aggiungi-Relazione "RigheOrdine" "seller_id"  "Venditori"  "seller_id"   $true
Aggiungi-Relazione "RigheOrdine" "product_id" "Prodotti"   "product_id"  $true

# due date sullo stesso calendario: acquisto attiva, consegna in panchina.
# La seconda si accende con USERELATIONSHIP dove serve.
Aggiungi-Relazione "Ordini" "data_acquisto" "Calendario" "Data" $true
Aggiungi-Relazione "Ordini" "data_consegna" "Calendario" "Data" $false

# ------------------------------------------------------------------ le misure
function Aggiungi-Misura($nome, $dax, $formato, $descrizione) {
    $ms = New-Object Microsoft.AnalysisServices.Tabular.Measure
    $ms.Name = $nome
    $ms.Expression = $dax.Trim()
    if ($formato) { $ms.FormatString = $formato }
    if ($descrizione) { $ms.Description = $descrizione }
    $mod.Tables["Misure"].Measures.Add($ms)
}

Aggiungi-Misura "Ordini consegnati" "COUNTROWS( Ordini )" "#,0" `
    "Base dei tempi e dei venditori: 96.470."
Aggiungi-Misura "Ordini recensiti" "CALCULATE( [Ordini consegnati], Ordini[recensito] = TRUE() )" "#,0" `
    "Base dei voti: 95.824. Non e' la stessa dei tempi."
Aggiungi-Misura "Ordini in ritardo" "CALCULATE( [Ordini consegnati], Ordini[in_ritardo] = TRUE() )" "#,0" $null
Aggiungi-Misura "% ordini in ritardo" "DIVIDE( [Ordini in ritardo], [Ordini consegnati] )" "0.0%" $null

Aggiungi-Misura "Giorni di ritardo (mediana)" `
    "MEDIANX( FILTER( Ordini, Ordini[in_ritardo] = TRUE() ), Ordini[giorni_ritardo] )" "0.0" `
    "Mediana e non media: la coda arriva a 189 giorni e la media la segue."
Aggiungi-Misura "Margine di consegna (mediana)" `
    "- MEDIANX( FILTER( Ordini, Ordini[in_ritardo] = FALSE() ), Ordini[giorni_ritardo] )" "0.0" `
    "Quanti giorni prima della data promessa arrivano gli ordini in orario: 12,3."

Aggiungi-Misura "Voto medio" "AVERAGE( Ordini[voto] )" "0.00" $null
Aggiungi-Misura "% recensioni negative" `
    "DIVIDE( CALCULATE( [Ordini consegnati], Ordini[voto_negativo] = TRUE() ), [Ordini recensiti] )" "0.0%" `
    "Negativa = 1 o 2 stelle. La soglia e' una scelta."

Aggiungi-Misura "% recensioni negative in orario" `
    "CALCULATE( [% recensioni negative], Ordini[in_ritardo] = FALSE() )" "0.0%" `
    "9,2%. Serve accanto a quella in ritardo: da sola non dice niente."
Aggiungi-Misura "% recensioni negative in ritardo" `
    "CALCULATE( [% recensioni negative], Ordini[in_ritardo] = TRUE() )" "0.0%" `
    "54,0%. Quasi sei volte l'altra: e' il numero che regge tutto il lavoro."

Aggiungi-Misura "% negative (consegne in orario)" `
    "IF( SELECTEDVALUE( Ordini[fascia_ordine] ) <= 3, [% recensioni negative] )" "0.0%" `
    "La stessa misura, ristretta alle fasce prima della data promessa: sul grafico e' il contesto grigio."
Aggiungi-Misura "% negative (consegne in ritardo)" `
    "IF( SELECTEDVALUE( Ordini[fascia_ordine] ) >= 4, [% recensioni negative] )" "0.0%" `
    "La stessa misura, ristretta alle fasce oltre la data promessa: sul grafico e' l'accento rosso."

Aggiungi-Misura "Fatturato" "CALCULATE( SUM( RigheOrdine[valore_riga] ), Ordini )" '"R$" #,0' `
    "Prezzo + spedizione, sui soli ordini consegnati."
Aggiungi-Misura "Fatturato consegnato e recensito" `
    "CALCULATE( SUM( RigheOrdine[valore_riga] ), Ordini[recensito] = TRUE() )" '"R$" #,0' `
    "R$ 15.289.974 - la base su cui sono calcolate le quote dei documenti."
Aggiungi-Misura "Fatturato in ritardo" `
    "CALCULATE( SUM( RigheOrdine[valore_riga] ), Ordini[in_ritardo] = TRUE() )" '"R$" #,0' $null
Aggiungi-Misura "% fatturato in ritardo" "DIVIDE( [Fatturato in ritardo], [Fatturato] )" "0.0%" $null

Aggiungi-Misura "Fase venditore (mediana)" `
    "MEDIANX( FILTER( Ordini, Ordini[cronologia_ok] = TRUE() ), Ordini[giorni_fase_venditore] )" "0.0" `
    "Dall'approvazione all'affidamento al corriere. Esclude i 1.388 ordini a cronologia rotta."
Aggiungi-Misura "Fase logistica (mediana)" `
    "MEDIANX( FILTER( Ordini, Ordini[cronologia_ok] = TRUE() ), Ordini[giorni_fase_logistica] )" "0.0" `
    "Dall'affidamento al corriere alla consegna."

Aggiungi-Misura "Venditori misurati" `
    "CALCULATE( DISTINCTCOUNT( RigheOrdine[seller_id] ), Ordini )" "#,0" `
    "Venditori con almeno un ordine consegnato: 2.970."
Aggiungi-Misura "Ordini del venditore" `
    "CALCULATE( DISTINCTCOUNT( RigheOrdine[order_id] ), Ordini )" "#,0" `
    "Ordini consegnati che contengono almeno una riga del venditore."
Aggiungi-Misura "Ordini in ritardo del venditore" `
    "CALCULATE( DISTINCTCOUNT( RigheOrdine[order_id] ), Ordini[in_ritardo] = TRUE() )" "#,0" $null
Aggiungi-Misura "% ritardo del venditore" `
    "DIVIDE( [Ordini in ritardo del venditore], [Ordini del venditore] )" "0.0%" $null
# Qui stava "% ritardo del venditore (sopra soglia)", tolta il 26/08.
# Era scritta per la classifica dei venditori di pagina 2, e quella pagina ha
# smesso di essere una classifica quando i dati hanno detto che i venditori non
# sono il problema. La misura e' rimasta a girare a vuoto per tre giorni: nessun
# visuale la usava, e un modello che espone una misura che nessuno usa promette
# una risposta che non da'.
# La soglia dei 30 ordini NON e' sparita con lei: vive in "Venditori sopra
# soglia" (il riquadro da 627) e nella soglia dei 100 ordini di "% ritardo dello
# stato". La disciplina e' applicata dove serve, non dichiarata e basta.
Aggiungi-Misura "Venditori sopra soglia" `
    "SUMX( VALUES( Venditori[seller_id] ), IF( [Ordini del venditore] >= 30, 1, 0 ) )" "#,0" `
    "627 venditori: il 21% di quelli misurati, ma l'83,5% degli ordini."

Aggiungi-Misura "% ritardo dello stato" `
    "IF( [Ordini del venditore] >= 100, [% ritardo del venditore] )" "0.0%" `
    "Ritardo per stato del venditore. Sotto i 100 ordini consegnati resta vuota: stessa disciplina della soglia sui venditori. NB: si appoggia alle righe d'ordine, perche' il filtro dello stato non risale fino agli ordini."

Aggiungi-Misura "Coppie venditore-ordine" `
    "CALCULATE( COUNTROWS( SUMMARIZE( RigheOrdine, RigheOrdine[order_id], RigheOrdine[seller_id] ) ), Ordini )" "#,0" `
    "97.811 contro 96.470 ordini: 1.278 ordini hanno piu' di un venditore."

Aggiungi-Misura "Ordini esclusi dall'analisi" `
    "CALCULATE( SUM( ControlloStatiOrdine[ordini] ), ControlloStatiOrdine[nell_analisi] = FALSE() )" "#,0" `
    "2.963. Sta nel pannello dei limiti e non e' battuto a mano."

# --- il crollo del voto: era il numero che regge il lavoro, e non stava da nessuna
#     parte nel cruscotto. Adesso sono due riquadri di pagina 1.
Aggiungi-Misura "Voto medio in orario" `
    "CALCULATE( [Voto medio], Ordini[in_ritardo] = FALSE() )" "0.00" `
    "4,29. Il voto quando la consegna rispetta la promessa."
Aggiungi-Misura "Voto medio in ritardo" `
    "CALCULATE( [Voto medio], Ordini[in_ritardo] = TRUE() )" "0.00" `
    "2,57. Lo stesso voto quando la promessa salta. Base: i 95.824 recensiti."

# --- la serie nel tempo (pagina 3).
#
# Le due misure "(mese)" restano vuote fuori dal periodo utile, e un mese in cui
# tutte le misure sono vuote sparisce dall'asse: e' il modo di non mostrare
# l'1,1% di 265 ordini di ottobre 2016 come se fosse un mese come gli altri.
#
# Le due "(anno prec.)" funzionano SOLO perche' Calendario e' contrassegnata come
# tabella data (dataCategory Time). E' quella marcatura a far togliere a
# SAMEPERIODLASTYEAR il filtro di Anno-mese che arriva dall'asse del grafico, e a
# sostituirlo con le date spostate di un anno. Senza, i due filtri si
# intersecherebbero e la serie sarebbe vuota dappertutto.
# Il secondo filtro tiene fuori il 2016: sui mesi del 2017 la serie dell'anno
# prima resta vuota di proposito, perche' il 2016 non e' un anno confrontabile.
Aggiungi-Misura "% ordini in ritardo (mese)" `
    "IF( SELECTEDVALUE( Calendario[periodo_utile] ) = TRUE(), [% ordini in ritardo] )" "0.0%" `
    "La serie mensile vive solo su gennaio 2017 - agosto 2018."
Aggiungi-Misura "% ordini in ritardo (anno prec.)" @'
IF(
    SELECTEDVALUE( Calendario[periodo_utile] ) = TRUE(),
    CALCULATE(
        [% ordini in ritardo],
        SAMEPERIODLASTYEAR( Calendario[Data] ),
        Calendario[periodo_utile] = TRUE()
    )
)
'@ "0.0%" "Lo stesso mese dell'anno prima. Sui mesi del 2017 resta vuota: il 2016 non e' confrontabile."

Aggiungi-Misura "% recensioni negative (mese)" `
    "IF( SELECTEDVALUE( Calendario[periodo_utile] ) = TRUE(), [% recensioni negative] )" "0.0%" `
    "Come sopra, sulla base dei recensiti."
Aggiungi-Misura "% recensioni negative (anno prec.)" @'
IF(
    SELECTEDVALUE( Calendario[periodo_utile] ) = TRUE(),
    CALCULATE(
        [% recensioni negative],
        SAMEPERIODLASTYEAR( Calendario[Data] ),
        Calendario[periodo_utile] = TRUE()
    )
)
'@ "0.0%" "Come sopra."

# --- i quattro riquadri di pagina 3: due finestre fisse, gennaio-agosto, che
#     sono gli unici mesi presenti in tutti e due gli anni pieni.
#     Non risentono di un filtro sull'anno, ed e' il motivo per cui su quella
#     pagina il filtro dell'anno non c'e'.
Aggiungi-Misura "% ordini in ritardo gen-ago 2018" `
    "CALCULATE( [% ordini in ritardo], Calendario[Anno] = 2018, Calendario[confrontabile] = TRUE() )" "0.0%" `
    "9,4%. Piu' del doppio dello stesso periodo dell'anno prima."
Aggiungi-Misura "% ordini in ritardo gen-ago 2017" `
    "CALCULATE( [% ordini in ritardo], Calendario[Anno] = 2017, Calendario[confrontabile] = TRUE() )" "0.0%" `
    "4,2%. La finestra di confronto."
Aggiungi-Misura "% recensioni negative gen-ago 2018" `
    "CALCULATE( [% recensioni negative], Calendario[Anno] = 2018, Calendario[confrontabile] = TRUE() )" "0.0%" `
    "13,3%. Stessa finestra, base dei recensiti."
Aggiungi-Misura "% recensioni negative gen-ago 2017" `
    "CALCULATE( [% recensioni negative], Calendario[Anno] = 2017, Calendario[confrontabile] = TRUE() )" "0.0%" `
    "10,5%. Stessa finestra, base dei recensiti."

# --- la valuta: reais convertiti in euro a un tasso unico, dichiarato
#
# Il tasso e' la media dei cambi mensili BCE del periodo, pesata per il fatturato
# di ogni mese: 15.418.395 R$ diviso i 3.902.588 EUR che si ottengono convertendo
# mese per mese fanno 3,9508.
#
# Un tasso unico e' una semplificazione, e il suo prezzo e' misurato: sul
# fatturato consegnato sbaglia dello 0,02% rispetto alla conversione mensile, e
# sul fatturato in ritardo dello 0,5%. Una tabella dei cambi mensili in cambio di
# mezzo punto percentuale non vale la grana in piu' da tenere allineata.
# Sbagliato sarebbe prendere il cambio di UN anno: il 2017 medio (3,6054) gonfia
# il totale del 9,6%, il 2018 medio (4,3085) lo sgonfia dell'8,3%. Il real si e'
# svalutato in mezzo ai dati, e i due anni non sono intercambiabili.
#
# Fonte: BCE, tassi di riferimento mensili BRL/EUR, serie EXR.M.BRL.EUR.SP00.A,
# scaricati il 26/08/2026.
$euro = '"' + [char]0x20AC + '" #,0'

Aggiungi-Misura "Cambio reais per euro" "3.95" "0.00" `
    "Media dei cambi mensili BCE 2016-2018 pesata per il fatturato. Il tasso sta qui e in un posto solo."
Aggiungi-Misura "Fatturato (EUR)" `
    "DIVIDE( [Fatturato], [Cambio reais per euro] )" $euro `
    "Lo stesso fatturato in euro. La conversione e' una scelta, e il tasso e' una misura visibile."
Aggiungi-Misura "Fatturato in ritardo (EUR)" `
    "DIVIDE( [Fatturato in ritardo], [Cambio reais per euro] )" $euro `
    "EUR 342.000 circa. E' il numero che sta sul riquadro di pagina 1."

# "Fatturato consegnato e recensito" non sta su nessuna pagina e nessun'altra
# misura la cita: serve solo alle righe 10 e 11 di RICONCILIAZIONE.md, per poter
# rifare quel controllo. E' un attrezzo, non un campo del cruscotto, e come tale
# si nasconde: chi apre l'elenco dei campi non deve chiedersi a cosa serva.
$mod.Tables["Misure"].Measures["Fatturato consegnato e recensito"].IsHidden = $true

# ------------------------------------------------------------------ si scrive
#
# Si riscrive SOLO la cartella definition\ — il modello, che e' roba nostra.
# Tutto il resto del progetto (.platform, definition.pbism, .pbi\, il report)
# lo scrive Power BI col Salva con nome, ed e' roba sua: sovrascriverlo a mano
# significa indovinare schemi e versioni, che e' gia' costato un pomeriggio.
$def = Join-Path $cartella "definition"

if (-not (Test-Path (Join-Path $cartella "definition.pbism"))) {
    throw @"
Manca l'involucro del progetto in $cartella
Non lo genero a mano: va creato una volta da Power BI Desktop, con
  File -> Salva con nome -> Progetto Power BI (*.pbip)
salvando come 'delivery-delay-impact' in C:\dev\_powerbi.
Poi questo script riscrive solo il modello, lasciando intatto il resto.
"@
}

if (Test-Path $def) { Remove-Item $def -Recurse -Force }
[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::SerializeDatabaseToFolder($db, $def)
Write-Output "modello scritto in $def (involucro del progetto lasciato intatto)"


# ------------------------------------------------------- e si rilegge, per prova
$verifica = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($def)
$v = $verifica.Model
Write-Output ""
Write-Output "riletto senza errori:"
Write-Output ("  tabelle    : " + $v.Tables.Count + "  (" + (($v.Tables | ForEach-Object { $_.Name }) -join ", ") + ")")
Write-Output ("  espressioni: " + $v.Expressions.Count)
Write-Output ("  relazioni  : " + $v.Relationships.Count)
Write-Output ("  misure     : " + $v.Tables["Misure"].Measures.Count)
