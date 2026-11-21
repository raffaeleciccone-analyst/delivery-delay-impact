// Query: CoordinateCAP   -- NON caricata nel modello (serve alla distanza di Ordini)
//
// La geolocalizzazione non è una dimensione (DATI-SPORCHI.md §9): 1.000.163 righe per
// 19.015 prefissi di CAP. Qui diventa un punto per CAP.
// Confini del Brasile: gli stessi quattro numeri di tests/riferimento.py (PIANO.md §3).
//
// Righe attese: un CAP per riga. Restano senza punto 158 CAP di clienti e 7 di venditori.
let
    Origine = Csv.Document(
        File.Contents(PercorsoDati & "\olist_geolocation_dataset.csv"),
        [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Intestazioni promosse" = Table.PromoteHeaders(Origine, [PromoteAllScalars = true]),
    #"Tipi dichiarati in en-US" = Table.TransformColumnTypes(
        #"Intestazioni promosse",
        {
            {"geolocation_zip_code_prefix", Int64.Type},
            {"geolocation_lat", type number},
            {"geolocation_lng", type number}
        },
        "en-US"
    ),

    // §9 - 42 punti stanno fuori dal Brasile (in mare, in Europa): si scartano prima
    #"Scarta i punti fuori dal Brasile" = Table.SelectRows(
        #"Tipi dichiarati in en-US",
        each [geolocation_lat] >= -33.75 and [geolocation_lat] <= 5.27
            and [geolocation_lng] >= -73.99 and [geolocation_lng] <= -34.79
    ),

    // La mediana e non la media: un punto sbagliato sposta la media, non la mediana
    #"Un punto per CAP (mediana di lat/lng)" = Table.Group(
        #"Scarta i punti fuori dal Brasile",
        {"geolocation_zip_code_prefix"},
        {
            {"lat", each List.Median([geolocation_lat]), type number},
            {"lng", each List.Median([geolocation_lng]), type number}
        }
    ),
    #"Rinomina in italiano" = Table.RenameColumns(
        #"Un punto per CAP (mediana di lat/lng)", {{"geolocation_zip_code_prefix", "cap"}}
    )
in
    #"Rinomina in italiano"
