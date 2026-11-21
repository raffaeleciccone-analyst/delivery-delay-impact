# Ritardi di consegna — SPEC (cosa e perché)

> Questo file dice COSA deve fare il cruscotto, non COME. Il come sta in PIANO.md.
> La domanda e il ragionamento completo sono in `DOMANDA.md`, che resta il documento di partenza:
> questa spec ne ricava funzioni e criteri controllabili.
> Stato: **APPROVATA il 21/11/2026**, ricostruita da un progetto già esistente. Domande aperte risolte.

## 1. Problema
Su un marketplace (Olist) chi decide se sospendere un venditore vuole sapere **quanto costano i ritardi
di consegna in recensioni negative, e di chi è la colpa**. Senza una risposta misurata si rischia di
punire i venditori per un problema che è dei corrieri.

## 2. Uso principale
- U1. Chi decide apre il cruscotto e in pochi secondi vede quanti ordini arrivano in ritardo, quanto
  peggiorano le recensioni e se la colpa è del venditore o del trasporto.
- U2. Un selezionatore o un docente apre il repository e capisce domanda, risultati e limiti, e può
  rifare tutto da zero con i dati pubblici.

## 3. Cosa fa
- F1. Conta gli ordini consegnati dopo la data promessa, e di quanti giorni (mediana).
- F2. Mostra come cambiano le recensioni negative per **fasce di ritardo**, non con una correlazione.
- F3. Separa le recensioni scritte **prima** di ricevere il pacco da quelle scritte **dopo**.
- F4. Dice quanto fatturato passa da ordini in ritardo, e che quota del totale è.
- F5. Divide il tempo di consegna in fase del venditore e fase del corriere, per dire di chi è il ritardo.
- F6. Confronta i venditori solo sopra una soglia minima di ordini, per non scambiare il rumore per un problema.
- F7. Mostra l'andamento mese per mese e il confronto gennaio-agosto 2017 contro 2018.
- F8. Ha una pagina "cosa non dice" con i limiti dell'analisi.
- F9. Si ricostruisce da zero con script (modello e report generati, non disegnati a mano) e si
  controlla senza aprire Power BI.
- F10. *(aggiunta il 21/11)* Misura la **distanza** fra venditore e cliente e mostra quanto del ritardo
  si spiega con la geografia: un pacco che fa 3.000 km ci mette di più senza che sia colpa di nessuno.
- F11. *(aggiunta il 21/11)* Controlla i numeri anche **dentro Power BI**: con il report aperto, legge il
  valore delle misure dal motore e lo confronta con quello atteso, al posto del controllo a mano dal PDF.

## 3b. Da dove arrivano i dati
- D1. Dump pubblico Olist su Kaggle (CC BY-NC-SA 4.0), scaricato e congelato il 23/08/2026. Non è nel
  repository: si scarica in `dati_grezzi/csv/` (confermato).
- D2. Cambio reais → euro: media dei cambi mensili BCE, pesata per fatturato (3,95) (confermato).

## 4. Cosa NON fa
- Nessuna previsione: i dati finiscono nel 2018.
- Nessuna pagina "panoramica vendite", nessun grafico che non risponda a una delle sotto-domande.
- Non dice se un cliente ha smesso di comprare (il 97% compra una volta sola).
- Non dimostra una causa: misura che ritardo e recensione negativa vanno insieme.
- Non calcola il costo per rimediare: informa chi decide, non decide.
- Non analizza gli ordini annullati o non consegnati (2.963 esclusi).
- Non misura la distanza su strada né i tempi del corriere: la distanza è in linea d'aria fra i centri
  dei CAP. *(proposta di Claude)*

## 5. Criteri di controllo
Ogni criterio diventa un test automatico. "Finito" = tutti i test passano.
I numeri attesi sono quelli di `RICONCILIAZIONE.md` (ricontati il 2/10), calcolati dai CSV.

**Numeri (dai CSV, rifacendo i passaggi di Power Query)**
- C1 (F1). Con i CSV del 23/08 → ordini consegnati con data = **96.470**, di cui recensiti **95.824**.
- C2 (F1). Ordini in ritardo = **6.534 (6,8%)**; ritardo mediano **7** giorni.
- C3 (F2, F3). Recensioni negative: **9,2%** sugli ordini in orario; sui ritardi scritte prima del pacco
  il **70,1%** (4.476 su 6.381), negative **80,6%**; negative dopo il pacco **19,4%** (su 1.905).
- C4 (F4). Quota di fatturato in ritardo = **7,5%**.
- C5 (F5). Fase venditore mediana 1,79 giorni in orario / 3,07 in ritardo; fase corriere 6,96 / 26,20.
  Gli **1.388** ordini con date incoerenti (partiti prima di essere approvati) sono esclusi dalle fasi.
- C6 (F6). Venditori con almeno una consegna = **2.970**; sopra la soglia di 30 ordini = **627**.
- C7 (F7). Ritardi gennaio-agosto: **3,5%** nel 2017, **7,7%** nel 2018.
- C8 (F1). Casi limite: un ordine consegnato **nel giorno promesso** non è in ritardo; un ordine
  "consegnato" **senza data di consegna** è escluso (sono 8); un ordine con **più recensioni** conta una
  volta, con la media dei voti.

**Modello e report (senza aprire Power BI)**
- C9 (F9). Ogni misura e colonna usata da un grafico esiste nel modello.
- C10 (F9). Nessun grafico esce dalla pagina o si sovrappone a un altro; tutto sta sulla griglia a 12 colonne.
- C11 (F9). Nessuna misura del modello è inutilizzata (o è nascosta perché serve solo ai controlli).
- C12 (F8). Esiste la pagina "cosa non dice", e il report ha le pagine di F1-F7.
- C13 (F9). Rigenerare il report con lo script produce esattamente i file salvati nel repository.

**Distanza (F10)** — i valori attesi si fissano dopo il primo calcolo e da lì non si muovono
- C15 (F10). Due CAP con coordinate note → distanza in linea d'aria corretta (es. San Paolo centro –
  Rio de Janeiro centro ≈ 360 km, con tolleranza di 5 km); stesso CAP → 0 km.
- C16 (F10). Un CAP con più punti nella tabella delle coordinate conta come **un solo punto** (il centro).
- C17 (F10). Ordini con un CAP senza coordinate (158 CAP di clienti, cioè 279 clienti, e 7 di venditori)
  restano fuori dai calcoli sulla distanza, e il report dice quanti sono. *(corretto il 21/11:
  DATI-SPORCHI §9 diceva "278 CAP", ma 278 erano i clienti, non i CAP)*
- C18 (F10). Le fasce di distanza insieme agli esclusi danno il totale degli ordini consegnati (96.470):
  nessun ordine perso o contato due volte. Valori fissati il 21/11: sotto 100 km 17.794 (4,5% in ritardo),
  100-500 km 36.964 (6,1%), 500-1.000 km 25.841 (7,1%), 1.000-2.000 km 9.765 (9,5%), oltre 2.000 km 5.625
  (12,0%), distanza non calcolabile 481.
- C19 (F10). Un ordine con più venditori usa la distanza del venditore più lontano. *(proposta di Claude)*
- C21 (F10). La pagina 2 contiene il grafico "% in ritardo per fascia di distanza", con le cinque fasce
  in ordine (sotto 100 km → oltre 2.000 km).

**Dentro Power BI (F11)** — girano solo con il report aperto in Power BI Desktop, altrimenti si saltano
- C20 (F11). Le misure del modello danno gli stessi valori di C2-C7 (con l'arrotondamento mostrato nel report).

**Documenti**
- C14 (U2). I numeri citati nel README coincidono con quelli dei criteri C1-C7.

## 5b. Regole di calcolo
*(aggiunte il 21/11/2026 dopo una ricostruzione alla cieca: un agente che aveva solo i documenti ha
riprodotto tutti i numeri, ma su questi punti ha dovuto scegliere da solo.)*

- R1. **Ritardo:** si confrontano due date (giorno di consegna contro giorno promesso), §4b.
  **Fasi** venditore e corriere: differenze fra istanti, in giorni con i decimali.
- R2. **Cronologia incoerente:** affidato al corriere *strettamente* prima dell'approvazione, o consegnato
  strettamente prima dell'affidamento, o una delle due date mancante.
- R3. **Recensione negativa:** media dei voti dell'ordine ≤ 2. Un ordine con media 2,5 non è negativo.
  "Prima del pacco" = la prima risposta è precedente all'istante di consegna.
- R4. **Fasce di ritardo:** giorni interi, estremi compresi come dicono le etichette (−10 o meno; −9..−5;
  −4..0; 1..3; 4..7; 8..15; 16..30; oltre 30).
- R5. **Distanza:** se il cliente o anche un solo venditore dell'ordine non ha coordinate, la distanza
  dell'ordine è vuota. In tutto sono 481 ordini; di questi, 4 hanno più venditori e solo alcuni senza
  coordinate (è il caso che la regola decide).
- R5b. **Coordinate:** il CAP è il prefisso a 5 cifre **come numero intero**, come nel file (1000, non
  "01000"). Le righe duplicate del file di geolocalizzazione **restano** prima della mediana: un CAP rilevato
  più volte nello stesso punto pesa di più. Confini del Brasile estremi compresi.
- R6. **CAP senza coordinate (C17):** contati sui prefissi distinti di tutta l'anagrafica clienti e
  venditori, non solo degli ordini consegnati.
- R7. **Centri per C15:** San Paolo −23,5505 / −46,6333; Rio de Janeiro −22,9068 / −43,1729.
- R8. Le 547 recensioni multiple sono sull'intero file; dentro i 96.470 consegnati sono 525.

## 6. Vincoli
- Power BI Desktop in formato `.pbip` (modello e report come file di testo).
- I controlli devono girare senza Power BI, con Python, anche in CI su GitHub.
- I dati non si ridistribuiscono: i test sui numeri (C1-C8) girano solo se i CSV sono presenti in locale,
  altrimenti vengono saltati e lo dicono.

## 7. Domande aperte
- ~~Q1~~ Risolta il 21/11: i numeri si controllano due volte, dai CSV (sempre) e dentro Power BI (F11, C20).
- ~~Q2~~ Risolta il 21/11: la distanza si aggiunge (F10).
- ~~Q3~~ Risolta il 21/11: un grafico in più nella pagina 2 "Di chi è il ritardo", con la % di ordini in
  ritardo per fascia di distanza (sotto 100 km, 100-500, 500-1.000, 1.000-2.000, oltre 2.000 km).
