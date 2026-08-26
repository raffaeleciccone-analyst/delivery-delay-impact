// Query: Ordini   -- tabella dei fatti, grana: un ordine consegnato
// I passaggi hanno i nomi decisi in DATI-SPORCHI.md.
//
// Righe attese: 96.470  (numero 3 di RICONCILIAZIONE.md)
// di cui recensito = true: 95.824  (numero 4)
let
    Origine = OrdiniGrezzi,

    // §1 - solo i consegnati. Gli altri 2.963 non hanno una data di consegna
    // perche' non sono mai arrivati. Quanti sono lo dice ControlloStatiOrdine.
    #"Tieni solo gli ordini consegnati" = Table.SelectRows(
        Origine, each [order_status] = "delivered"
    ),

    // §2 - otto ordini sono marcati consegnati ma non hanno la data.
    #"Scarta i consegnati senza data di consegna" = Table.SelectRows(
        #"Tieni solo gli ordini consegnati",
        each [order_delivered_customer_date] <> null
    ),

    // Il ritardo e' rispetto alla data PROMESSA, non a un tempo ragionevole (§4).
    #"Giorni di ritardo" = Table.AddColumn(
        #"Scarta i consegnati senza data di consegna",
        "giorni_ritardo",
        each Duration.TotalDays([order_delivered_customer_date] - [order_estimated_delivery_date]),
        type number
    ),
    #"In ritardo si o no" = Table.AddColumn(
        #"Giorni di ritardo", "in_ritardo", each [giorni_ritardo] > 0, type logical
    ),
    // la stessa cosa in parole: sui grafici "Vero/Falso" non dice niente a nessuno
    #"Esito della consegna" = Table.AddColumn(
        #"In ritardo si o no",
        "esito_consegna",
        each if [giorni_ritardo] > 0 then "Consegnati in ritardo" else "Consegnati in orario",
        type text
    ),

    // Le fasce servono a mostrare il DIRUPO (DATI-SPORCHI.md, ipotesi 1): il legame
    // fra ritardo e recensione non e' una pendenza, e un indicatore riassuntivo
    // direbbe il falso. Mostrando le fasce si vede dove succede davvero.
    // I tagli sono gli stessi dell'analisi: -10, -5, 0, 3, 7, 15, 30 giorni.
    #"Fascia di ritardo" = Table.AddColumn(
        #"Esito della consegna",
        "fascia_ritardo",
        each if [giorni_ritardo] <= -10 then "Oltre 10 gg in anticipo"
             else if [giorni_ritardo] <= -5 then "5-10 gg in anticipo"
             else if [giorni_ritardo] <= 0  then "0-5 gg in anticipo"
             else if [giorni_ritardo] <= 3  then "0-3 gg in ritardo"
             else if [giorni_ritardo] <= 7  then "3-7 gg di ritardo"
             else if [giorni_ritardo] <= 15 then "7-15 gg di ritardo"
             else if [giorni_ritardo] <= 30 then "15-30 gg di ritardo"
             else "Oltre 30 gg di ritardo",
        type text
    ),
    // l'ordine alfabetico non e' l'ordine giusto: serve una colonna per ordinarle
    #"Ordine della fascia" = Table.AddColumn(
        #"Fascia di ritardo",
        "fascia_ordine",
        each if [giorni_ritardo] <= -10 then 1
             else if [giorni_ritardo] <= -5 then 2
             else if [giorni_ritardo] <= 0  then 3
             else if [giorni_ritardo] <= 3  then 4
             else if [giorni_ritardo] <= 7  then 5
             else if [giorni_ritardo] <= 15 then 6
             else if [giorni_ritardo] <= 30 then 7
             else 8,
        Int64.Type
    ),

    // Le due fasi della sotto-domanda 5: quella del venditore e quella del corriere.
    #"Fase venditore" = Table.AddColumn(
        #"Ordine della fascia",
        "giorni_fase_venditore",
        each Duration.TotalDays([order_delivered_carrier_date] - [order_approved_at]),
        type number
    ),
    #"Fase logistica" = Table.AddColumn(
        #"Fase venditore",
        "giorni_fase_logistica",
        each Duration.TotalDays([order_delivered_customer_date] - [order_delivered_carrier_date]),
        type number
    ),

    // §3 - 1.359 ordini risultano partiti prima di essere approvati: su quelli
    // le fasi vengono negative. Si MARCANO, non si cancellano: restano nel
    // fatturato e nel conteggio, escono solo dalle misure di durata.
    // Righe con cronologia_ok = true attese: 95.082
    #"Marca la cronologia incoerente" = Table.AddColumn(
        #"Fase logistica",
        "cronologia_ok",
        each [giorni_fase_venditore] <> null
            and [giorni_fase_logistica] <> null
            and [giorni_fase_venditore] >= 0
            and [giorni_fase_logistica] >= 0,
        type logical
    ),

    // Due colonne data (senza ora) per agganciare il Calendario.
    // shipping_limit_date NON entra: e' una scadenza contrattuale, e arriva al 2020 (§12).
    #"Data di acquisto" = Table.AddColumn(
        #"Marca la cronologia incoerente",
        "data_acquisto",
        each DateTime.Date([order_purchase_timestamp]),
        type date
    ),
    #"Data di consegna" = Table.AddColumn(
        #"Data di acquisto",
        "data_consegna",
        each DateTime.Date([order_delivered_customer_date]),
        type date
    ),

    // Il voto sta qui e non in una tabella a parte, perche' RecensioniPerOrdine
    // ha gia' grana un-ordine (§5): tenerla separata aggiungerebbe una relazione
    // uno-a-uno senza guadagnarci niente.
    #"Aggancia il voto della recensione" = Table.NestedJoin(
        #"Data di consegna", {"order_id"},
        RecensioniPerOrdine, {"order_id"},
        "rec", JoinKind.LeftOuter
    ),
    #"Espandi il voto" = Table.ExpandTableColumn(
        #"Aggancia il voto della recensione",
        "rec",
        {"voto", "recensioni_sull_ordine", "voto_negativo"},
        {"voto", "recensioni_sull_ordine", "voto_negativo"}
    ),

    // LE DUE BASI, dichiarate come colonna invece che ricordate a memoria:
    // tempi e venditori -> tutti i 96.470;  voti -> i 95.824 con recensito = true.
    #"Segna se recensito" = Table.AddColumn(
        #"Espandi il voto", "recensito", each [voto] <> null, type logical
    )
in
    #"Segna se recensito"
