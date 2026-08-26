// Query: ControlloStatiOrdine   -- 8 righe, serve al pannello «cosa NON dice»
//
// Buttare via 2.963 ordini senza dire quanti e' il modo silenzioso di far mentire
// un'analisi. Questa tabella li conta, e il pannello dei limiti legge DA QUI
// invece di avere il numero battuto a mano in una casella di testo.
// Se un giorno i dati cambiano, il pannello si aggiorna da solo.
let
    Origine = OrdiniGrezzi,
    #"Conta gli scartati per stato" = Table.Group(
        Origine,
        {"order_status"},
        {{"ordini", each Table.RowCount(_), Int64.Type}}
    ),
    #"Segna quali entrano nell'analisi" = Table.AddColumn(
        #"Conta gli scartati per stato",
        "nell_analisi",
        each [order_status] = "delivered",
        type logical
    ),
    #"Ordina per numero" = Table.Sort(
        #"Segna quali entrano nell'analisi", {{"ordini", Order.Descending}}
    )
in
    #"Ordina per numero"
