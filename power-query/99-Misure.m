// Query: Misure   -- tabella vuota che tiene solo le misure DAX
//
// Le misure stanno tutte qui e non sparse nelle tabelle dei fatti: chi apre il
// modello le trova in un posto solo, e nessuna tabella dei fatti finisce per
// sembrare il posto dove "vivono" i numeri.
// Una colonna sola, nascosta, e nessuna riga.
let
    Origine = #table({"segnaposto"}, {})
in
    Origine
