$targets = @("360Safe", "360sd", "CoolFileViewer", "Assistant")

Write-Host "===== 360/CoolFileViewer 强制清理 =====" -ForegroundColor Cyan
Write-Host "Targets: $($targets -join ', ')" -ForegroundColor Yellow

# ── 1. Kill processes ──
Write-Host "`n----- 1. Kill Processes -----" -ForegroundColor Cyan
$killed = 0
foreach ($kw in $targets) {
    $procs = Get-Process -Name "*$kw*" -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        try {
            $p.Kill()
            Write-Host "  [OK] Killed $($p.Name) (PID $($p.Id))" -ForegroundColor Green
            $killed++
        } catch {
            Write-Warning "  [!!] Failed to kill $($p.Name) (PID $($p.Id)): $_"
        }
    }
}
if ($killed -eq 0) { Write-Host "  [-] No matching processes" -ForegroundColor Gray }

Start-Sleep -Seconds 1

# ── 2. Disable services ──
Write-Host "`n----- 2. Disable Services -----" -ForegroundColor Cyan
$svcDisabled = 0
$allSvcs = Get-Service -ErrorAction SilentlyContinue
foreach ($kw in $targets) {
    $matches = $allSvcs | Where-Object { $_.Name -like "*$kw*" -or $_.DisplayName -like "*$kw*" }
    foreach ($s in $matches) {
        try {
            sc.exe config $s.Name start=disabled | Out-Null
            Stop-Service $s.Name -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Disabled+Stopped $($s.Name) ($($s.DisplayName))" -ForegroundColor Green
            $svcDisabled++
        } catch {
            Write-Warning "  [!!] Failed service $($s.Name): $_"
        }
    }
}
if ($svcDisabled -eq 0) { Write-Host "  [-] No matching services" -ForegroundColor Gray }

# ── 3. Delete directories ──
Write-Host "`n----- 3. Delete Directories -----" -ForegroundColor Cyan
$dirs = @(
    "$env:ProgramFiles\360",
    "${env:ProgramFiles(x86)}\360",
    "$env:ProgramFiles\360Safe",
    "${env:ProgramFiles(x86)}\360Safe",
    "$env:LocalAppData\360Safe",
    "$env:LocalAppData\360sd",
    "$env:AppData\360Safe",
    "$env:AppData\360sd",
    "$env:ProgramData\360Safe",
    "$env:ProgramData\360sd",
    "$env:LocalAppData\CoolFileViewer",
    "$env:AppData\CoolFileViewer"
)
$delCount = 0
foreach ($d in $dirs) {
    if (Test-Path $d) {
        try {
            Remove-Item -Path $d -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Deleted $d" -ForegroundColor Green
            $delCount++
        } catch {
            Write-Warning "  [!!] Failed to delete $d : $_"
        }
    }
}
if ($delCount -eq 0) { Write-Host "  [-] No matching directories" -ForegroundColor Gray }

# ── 4. Registry cleanup ──
Write-Host "`n----- 4. Registry Run/RunOnce Cleanup -----" -ForegroundColor Cyan
$regPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce"
)
$regRemoved = 0
foreach ($rp in $regPaths) {
    if (-not (Test-Path $rp)) { continue }
    $items = Get-ItemProperty -Path $rp -ErrorAction SilentlyContinue
    foreach ($prop in $items.PSObject.Properties) {
        if ($prop.Name -match '^(PSPath|PSParentPath|PSChildName|PSDrive|PSProvider)$') { continue }
        $matched = $false
        foreach ($kw in $targets) {
            if ($prop.Name -like "*$kw*" -or "$($prop.Value)" -like "*$kw*") { $matched = $true; break }
        }
        if ($matched) {
            try {
                Remove-ItemProperty -Path $rp -Name $prop.Name -ErrorAction Stop
                Write-Host "  [OK] Removed $rp -> $($prop.Name)" -ForegroundColor Green
                $regRemoved++
            } catch {
                Write-Warning "  [!!] Failed to remove $rp -> $($prop.Name): $_"
            }
        }
    }
}
if ($regRemoved -eq 0) { Write-Host "  [-] No matching registry entries" -ForegroundColor Gray }

# ── Summary ──
Write-Host "`n`n===== CLEANUP COMPLETE =====" -ForegroundColor Cyan
Write-Host "  Processes killed: $killed" -ForegroundColor Yellow
Write-Host "  Services disabled: $svcDisabled" -ForegroundColor Yellow
Write-Host "  Directories deleted: $delCount" -ForegroundColor Yellow
Write-Host "  Registry entries removed: $regRemoved" -ForegroundColor Yellow
Write-Host "`nRecommend restart to ensure full effect." -ForegroundColor Magenta
