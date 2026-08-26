// Query: RecensioniPerOrdine   -- NON caricata nel modello (serve al merge di Ordini)
//
// Il file ha 99.224 recensioni per 98.673 ordini: 547 ordini ne hanno piu' d'una,
// e 789 review_id compaiono su piu' ordini, la chiave dichiarata non e' una chiave
// (§5). Quindi review_id non entra nel modello, e il voto per ordine e' una MEDIA.
// Su 547 ordini il voto mostrato non e' un voto che qualcuno ha dato: sta scritto
// nel pannello dei limiti, e la colonna recensioni_sull_ordine permette di trovarli.
//
// Righe attese dopo il raggruppamento: 98.673
let
    // QuoteStyle.Csv e' obbligatorio: 5.496 a capo stanno DENTRO i commenti (§14).
    // Senza, il file si spezza in 104.719 righe e i tipi saltano.
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\olist_order_reviews_dataset.csv"),
        [Delimiter = ",", Columns = 7, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),

    // Controllo: qui le righe devono essere 99.224. Se sono 104.719, QuoteStyle e' saltato.
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {
            {"review_id", type text},
            {"order_id", type text},
            {"review_score", Int64.Type},
            {"review_comment_title", type text},
            {"review_comment_message", type text},
            {"review_creation_date", type datetime},
            {"review_answer_timestamp", type datetime}
        },
        "en-US"
    ),

    // I commenti non servono alla domanda e pesano: titolo mancante nell'88% dei casi,
    // testo nel 59%. Si tengono solo come conteggio, non come testo.
    #"Segna se c'e' un commento" = Table.AddColumn(
        #"Tipi dichiarati in en-US",
        "ha_commento",
        each [review_comment_message] <> null,
        type logical
    ),

    #"Una recensione per ordine (media dei punteggi)" = Table.Group(
        #"Segna se c'e' un commento",
        {"order_id"},
        {
            {"voto", each List.Average([review_score]), type number},
            {"recensioni_sull_ordine", each Table.RowCount(_), Int64.Type},
            {"con_commento", each List.Count(List.Select([ha_commento], each _ = true)), Int64.Type},
            {"prima_recensione", each List.Min([review_creation_date]), type datetime}
        }
    ),

    // Negativa = 1 o 2 stelle. La soglia e' una scelta e va detta.
    #"Voto negativo" = Table.AddColumn(
        #"Una recensione per ordine (media dei punteggi)",
        "voto_negativo",
        each [voto] <= 2,
        type logical
    )
in
    #"Voto negativo"
