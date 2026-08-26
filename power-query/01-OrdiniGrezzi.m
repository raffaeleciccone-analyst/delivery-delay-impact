// Query: OrdiniGrezzi
// Gli ordini come stanno nel file, senza nessun filtro.
// NON va caricata nel modello: serve solo a due cose, Ordini e ControlloStatiOrdine.
// (tasto destro sulla query -> togliere la spunta a "Abilita caricamento")
//
// Righe attese: 99.441
let
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\olist_orders_dataset.csv"),
        [Delimiter = ",", Columns = 8, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),

    // "en-US" non e' un vezzo: senza, il punto decimale dei prezzi e le date
    // vengono lette con le impostazioni italiane e sbagliano in silenzio.
    // Vedi DATI-SPORCHI.md §15.
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {
            {"order_id", type text},
            {"customer_id", type text},
            {"order_status", type text},
            {"order_purchase_timestamp", type datetime},
            {"order_approved_at", type datetime},
            {"order_delivered_carrier_date", type datetime},
            {"order_delivered_customer_date", type datetime},
            {"order_estimated_delivery_date", type datetime}
        },
        "en-US"
    )
in
    #"Tipi dichiarati in en-US"
