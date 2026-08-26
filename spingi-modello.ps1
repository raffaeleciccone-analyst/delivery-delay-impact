# Spinge il modello TMDL dentro un'istanza di Power BI Desktop gia' aperta.
#
# E' la stessa strada che usano gli strumenti esterni (Tabular Editor & co.):
# ci si collega al motore locale del file aperto e si scrive il modello.
# Serve quando il progetto .pbip non si apre: il modello e' lo stesso.
#
# Uso:  powershell -ExecutionPolicy Bypass -File spingi-modello.ps1 <porta>
#
# ATTENZIONE: scrive nell'istanza indicata. Puntarla su una finestra VUOTA,
# non su un file con del lavoro dentro.

param([Parameter(Mandatory = $true)][string]$Porta)

$ErrorActionPreference = "Stop"
$bin = "C:\Program Files\Microsoft Power BI Desktop\bin"
Add-Type -Path "$bin\Microsoft.PowerBI.Tabular.dll"

$def = "C:\dev\_powerbi\delivery-delay-impact.SemanticModel\definition"
if (-not (Test-Path $def)) { throw "manca $def - lancia prima costruisci-modello.ps1" }

# il modello gia' costruito e validato
$mio = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($def)
Write-Output ("modello letto: " + $mio.Model.Tables.Count + " tabelle, " + $mio.Model.Relationships.Count + " relazioni")

$srv = New-Object Microsoft.AnalysisServices.Tabular.Server
$srv.Connect("Data Source=localhost:$Porta")
Write-Output ("collegato a localhost:$Porta - database presenti: " + $srv.Databases.Count)
if ($srv.Databases.Count -eq 0) { throw "nessun database nell'istanza" }

$vivo = $srv.Databases[0]
Write-Output ("database bersaglio: " + $vivo.Name + " - tabelle attuali: " + $vivo.Model.Tables.Count)
if ($vivo.Model.Tables.Count -gt 0) {
    throw "l'istanza NON e' vuota (" + (($vivo.Model.Tables | ForEach-Object { $_.Name }) -join ", ") + "). Mi fermo per non sovrascrivere del lavoro."
}

# si copia il modello dentro quello vivo, oggetto per oggetto
$mio.Model.CopyTo($vivo.Model)
$vivo.Model.SaveChanges() | Out-Null
Write-Output "modello scritto nell'istanza"

# e si carica i dati
$vivo.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
$vivo.Model.SaveChanges() | Out-Null
Write-Output "dati caricati"

$srv.Disconnect()
Write-Output "fatto"
