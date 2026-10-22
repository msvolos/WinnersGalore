# Opens a workbook in Excel (hidden), recalculates every formula, reports any
# error cells, and saves so the calculated values and charts are cached for
# previews (OneDrive, phone). Usage: powershell -File refresh_excel.ps1 [path] [-Dump]
param(
    [string]$Path = (Join-Path $PSScriptRoot "DRF Tracker.xlsx"),
    [switch]$Dump
)
$Path = (Resolve-Path $Path).Path
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
try {
    $wb = $xl.Workbooks.Open($Path)
    $xl.CalculateFull()
    $errors = @()
    foreach ($ws in $wb.Worksheets) {
        $used = $ws.UsedRange
        foreach ($c in $used.Cells) {
            if ($c.HasFormula -and $c.Text -match '^#') { $errors += "$($ws.Name)!$($c.Address(0,0)) $($c.Text)" }
        }
    }
    if ($Dump) {
        $d = $wb.Worksheets.Item("Dashboard")
        foreach ($r in 5..34) {
            $line = foreach ($col in 2..14) { $t = $d.Cells.Item($r, $col).Text; if ($t) { $t } else { "." } }
            "{0,2}: {1}" -f $r, ($line -join " | ")
        }
        $b = $wb.Worksheets.Item("Bet Log")
        foreach ($r in 1..10) {
            $line = foreach ($col in 1..16) { $b.Cells.Item($r, $col).Text }
            "BL{0}: {1}" -f $r, ($line -join " | ")
        }
    }
    $wb.Save()
    $wb.Close($false)
    if ($errors.Count) { "ERRORS: " + ($errors -join "; "); exit 1 } else { "OK: recalculated, no formula errors" }
}
finally {
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
}
