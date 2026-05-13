# Start monitor as background PowerShell job (has proper console)
$logFile = "E:\MyCodeProjects\06-存档中心\logs\monitor_psjob.log"
$monitorPy = "E:\MyCodeProjects\审计工具\monitor_susu_pro.py"

# Kill existing
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*monitor_susu_pro*' } | ForEach-Object { Stop-Process $_.ProcessId -Force }
Start-Sleep 2

# Start with Start-Process (creates real console, hidden)
$argList = """$monitorPy"" --auto --no-bg --headless"
Write-Output "Starting: python $argList"
$p = Start-Process -FilePath "python" -ArgumentList $argList -WindowStyle Hidden -PassThru -RedirectStandardOutput $logFile
Write-Output "PID: $($p.Id)"

Start-Sleep 20

# Check if running
$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*monitor_susu_pro*' }
if ($procs) {
    Write-Output "ALIVE: $($procs | Select-Object ProcessId, CommandLine)"
} else {
    Write-Output "DEAD"
    Write-Output "--- Log tail ---"
    Get-Content $logFile -Tail 20 -Encoding UTF8
}
