// Query: Calendario   -- dimensione data, CREATA, non derivata
//
// E' la trappola numero uno dell'handoff, e in questi dati e' viva: novembre 2016
// non ha nessun ordine (§11). Una tabella data derivata da una colonna dei fatti
// salterebbe quel mese, e la time intelligence sbaglierebbe in silenzio.
// Qui i giorni sono generati uno per uno dal 1 gennaio 2016 al 31 dicembre 2018:
// i buchi restano visibili come zeri, che e' il loro mestiere.
//
// Va poi marcata in Power BI come "tabella data" (Modellazione -> Contrassegna
// come tabella data, colonna Data): senza quella marcatura le funzioni di
// intelligenza temporale non hanno garanzie.
//
// Righe attese: 1.096 (2016 e' bisestile)
let
    Inizio = #date(2016, 1, 1),
    Fine = #date(2018, 12, 31),
    Giorni = List.Dates(Inizio, Duration.Days(Fine - Inizio) + 1, #duration(1, 0, 0, 0)),
    Tabella = Table.FromList(Giorni, Splitter.SplitByNothing(), {"Data"}),
    #"Tipo data" = Table.TransformColumnTypes(Tabella, {{"Data", type date}}, "en-US"),

    #"Anno" = Table.AddColumn(#"Tipo data", "Anno", each Date.Year([Data]), Int64.Type),
    #"Numero mese" = Table.AddColumn(#"Anno", "Numero mese", each Date.Month([Data]), Int64.Type),
    #"Mese" = Table.AddColumn(
        #"Numero mese", "Mese", each Date.ToText([Data], [Format = "MMMM", Culture = "it-IT"]), type text
    ),
    #"Anno-mese" = Table.AddColumn(
        #"Mese", "Anno-mese", each Date.ToText([Data], [Format = "yyyy-MM", Culture = "en-US"]), type text
    ),
    #"Trimestre" = Table.AddColumn(
        #"Anno-mese", "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Data])), type text
    ),

    // Il periodo utile e' gennaio 2017 - agosto 2018 (§11): il 2016 sono 329 ordini
    // in tutto e settembre-ottobre 2018 sono venti ordini di coda del dump.
    #"Marca il periodo utile" = Table.AddColumn(
        #"Trimestre",
        "periodo_utile",
        each [Data] >= #date(2017, 1, 1) and [Data] <= #date(2018, 8, 31),
        type logical
    ),

    // Il confronto anno su anno esiste solo su gennaio-agosto: e' l'unico
    // intervallo presente in tutti e due gli anni pieni.
    #"Marca i mesi confrontabili" = Table.AddColumn(
        #"Marca il periodo utile",
        "confrontabile",
        each Date.Month([Data]) <= 8,
        type logical
    ),

    // L'etichetta che finisce sull'asse dei grafici. "Anno-mese" e' "2017-01":
    // ordina bene e non si legge — nessuno pensa in yyyy-MM. Questa e' "gen 17",
    // e resta unica su tutto il periodo, che e' la condizione perche' Power BI
    // possa ordinarla per "Anno-mese" invece che alfabeticamente: "feb" da solo
    // comparirebbe due volte e i due febbrai finirebbero nella stessa categoria.
    #"Etichetta del mese" = Table.AddColumn(
        #"Marca i mesi confrontabili",
        "Etichetta mese",
        each Date.ToText([Data], [Format = "MMM yy", Culture = "it-IT"]),
        type text
    )
in
    #"Etichetta del mese"
