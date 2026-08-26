// Query: CategorieTradotte   -- NON caricata nel modello (serve al merge di Prodotti)
//
// §7 - questo file ha un BOM UTF-8 in testa. Letto senza dichiarare l'encoding,
// la prima colonna prende un nome sporco e il merge con Prodotti non aggancia
// piu' niente, senza dare nessun errore.
//
// Righe attese: 71, contro 73 categorie nei prodotti: due non hanno traduzione.
let
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\product_category_name_translation.csv"),
        [Delimiter = ",", Columns = 2, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {{"product_category_name", type text}, {"product_category_name_english", type text}},
        "en-US"
    )
in
    #"Tipi dichiarati in en-US"
