// Query: RigheOrdine   -- tabella dei fatti, grana: una riga d'ordine
// Qui sta il fatturato. Il ritardo sta in Ordini: le due grane sono diverse
// e ogni misura deve dichiarare da quale delle due scende.
//
// Righe attese: 112.650
let
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\olist_order_items_dataset.csv"),
        [Delimiter = ",", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),

    // Il prezzo e' scritto 58.90 col punto: senza "en-US" diventa 5890 (§15).
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {
            {"order_id", type text},
            {"order_item_id", Int64.Type},
            {"product_id", type text},
            {"seller_id", type text},
            {"shipping_limit_date", type datetime},
            {"price", type number},
            {"freight_value", type number}
        },
        "en-US"
    ),

    // Prezzo + spedizione: e' la definizione di fatturato usata in tutti i documenti.
    // 383 righe hanno spedizione a 0 (§12): spedizione gratis, non un dato mancante.
    #"Valore della riga" = Table.AddColumn(
        #"Tipi dichiarati in en-US",
        "valore_riga",
        each [price] + [freight_value],
        type number
    )
in
    #"Valore della riga"
