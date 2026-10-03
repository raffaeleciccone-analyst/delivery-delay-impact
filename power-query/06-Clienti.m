// Query: Clienti   -- dimensione, grana: un cliente-ordine
//
// ATTENZIONE (§6): customer_id NON è la persona. Ci sono 99.441 customer_id
// distinti, esattamente quanti gli ordini, contro 96.096 customer_unique_id.
// La persona è customer_unique_id, e solo il 3,1% compra più di una volta.
// La chiave della relazione con Ordini è customer_id.
//
// Righe attese: 99.441
let
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\olist_customers_dataset.csv"),
        [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {
            {"customer_id", type text},
            {"customer_unique_id", type text},
            {"customer_zip_code_prefix", Int64.Type},
            {"customer_city", type text},
            {"customer_state", type text}
        },
        "en-US"
    ),

    // §8 - le città sono scritte in più modi: "sao paulo", "sao paulo - sp",
    // "sao paulo / sao paulo". Si taglia dopo il primo separatore.
    // Resta comunque vero che il raggruppamento affidabile è lo STATO, non la città.
    #"Normalizza le città" = Table.AddColumn(
        #"Tipi dichiarati in en-US",
        "citta",
        each Text.Proper(
            Text.Trim(
                List.First(
                    Text.Split(Text.Replace(Text.Replace([customer_city], " - ", "/"), " / ", "/"), "/")
                )
            )
        ),
        type text
    ),
    #"Tieni le colonne utili" = Table.SelectColumns(
        #"Normalizza le città",
        {"customer_id", "customer_unique_id", "customer_zip_code_prefix", "citta", "customer_state"}
    ),
    #"Rinomina in italiano" = Table.RenameColumns(
        #"Tieni le colonne utili",
        {{"customer_zip_code_prefix", "cap"}, {"customer_state", "stato"}}
    )
in
    #"Rinomina in italiano"
