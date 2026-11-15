# Capture the KV260 UART console to a log (BRINGUP-001).
# Usage: .\serial_capture.ps1 -Port COM9 -Seconds 60 [-Send "echo hello world"] [-Log file]
param([Parameter(Mandatory)][string]$Port, [int]$Seconds = 30, [string[]]$Send = @(),
      [string]$Log = "$PSScriptRoot\build\uart_$Port.log", [int]$Baud = 115200)
New-Item -ItemType Directory -Force (Split-Path $Log) | Out-Null
$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, 'None', 8, 'One'
$sp.ReadTimeout = 200; $sp.NewLine = "`r"
$sp.Open()
try {
  "=== $(Get-Date -Format o) $Port @ $Baud ===" | Add-Content $Log
  $end = (Get-Date).AddSeconds($Seconds); $sent = 0
  while ((Get-Date) -lt $end) {
    $t = $sp.ReadExisting()
    if ($t) { Write-Host -NoNewline $t; Add-Content $Log $t -NoNewline }
    if ($sent -lt $Send.Count -and (Get-Date) -gt $end.AddSeconds(-$Seconds + 2 + 3*$sent)) {
      $sp.Write($Send[$sent] + "`r"); $sent++
    }
    Start-Sleep -Milliseconds 100
  }
} finally { $sp.Close(); "`n=== end ===" | Add-Content $Log }
