# Legge il valore delle misure dal Power BI Desktop aperto (F11 di SPEC.md).
#
# Power BI Desktop, quando ha un file aperto, fa girare un motore locale: lo stesso
# a cui si collegano DAX Studio e Tabular Editor. Questo script ci si collega e
# chiede il valore di ogni misura, così i numeri del report si confrontano con
# quelli attesi senza leggerli a mano dal PDF.
#
# Uso:  powershell -ExecutionPolicy Bypass -File leggi-misure.ps1 "[Misura 1]" "CALCULATE([Misura 2], ...)" ...
# Ogni argomento è un'espressione DAX: di solito una misura fra parentesi quadre,
# oppure una misura con un filtro (es. la fase del venditore sui soli ordini in orario).
# Esce in JSON: {"porta": 12345, "misure": {"[Misura 1]": 0.068, ...}}
# Se non trova un Power BI aperto (o ne trova più di uno) esce con {"errore": "..."}.

$ErrorActionPreference = "Stop"
$misure = $args

function Esci($oggetto) { $oggetto | ConvertTo-Json -Compress -Depth 4; exit 0 }

$bin = "C:\Program Files\Microsoft Power BI Desktop\bin"
$dll = Join-Path $bin "Microsoft.PowerBI.AdomdClient.dll"
if (-not (Test-Path $dll)) { Esci @{ errore = "Power BI Desktop non installato in $bin" } }

# il motore scrive la sua porta in un file, uno per ogni finestra aperta
$cartella = Join-Path $env:LOCALAPPDATA "Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"
$porte = @()
if (Test-Path $cartella) {
    $porte = Get-ChildItem $cartella -Recurse -Filter "msmdsrv.port.txt" -ErrorAction SilentlyContinue |
        ForEach-Object { ([IO.File]::ReadAllText($_.FullName, [Text.Encoding]::Unicode)).Trim() } |
        Where-Object { $_ -match '^\d+$' }
}
# restano i file delle finestre chiuse: si tengono solo le porte che rispondono
$vive = @($porte | Where-Object {
    $c = New-Object Net.Sockets.TcpClient
    try { $c.Connect("localhost", [int]$_); $true } catch { $false } finally { $c.Close() }
})
if ($vive.Count -eq 0) { Esci @{ errore = "nessun Power BI Desktop aperto" } }
if ($vive.Count -gt 1) { Esci @{ errore = "più di un Power BI Desktop aperto: lasciane aperto uno solo" } }

Add-Type -Path $dll
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$($vive[0])")
$conn.Open()
$valori = @{}
foreach ($m in $misure) {
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "EVALUATE ROW(""v"", " + $m + ")"
    $r = $cmd.ExecuteReader()
    $valori[$m] = if ($r.Read()) { $r.GetValue(0) } else { $null }
    $r.Close()
}
$conn.Close()
Esci @{ porta = [int]$vive[0]; misure = $valori }
