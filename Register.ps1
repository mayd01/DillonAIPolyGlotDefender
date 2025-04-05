param (
    [string]$AppName = "DillyDefender",
    [string]$ExePath = "C:\Program Files\DillyDefender\dilly_defender.exe",
    [string]$IconPath = "C:\Program Files\DillyDefender\Defender.ico",
    [string]$ShortcutPath = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
)

$ProgramFilesGUID = "{6D809377-6AF0-444B-8957-A3773F02200E}"
$AppUserModelID = "$ProgramFilesGUID\$AppName\dilly_defender.exe"

Write-Host "🔧 Registering $AppName for Windows Notifications..."
$RegPath = "HKCU:\Software\Classes\Applications\dilly_defender.exe"

if (!(Test-Path $RegPath)) {
    New-Item -Path $RegPath -Force | Out-Null
}

New-ItemProperty -Path $RegPath -Name "AppUserModelID" -Value $AppUserModelID -PropertyType String -Force | Out-Null
Write-Host "✅ AppUserModelID Registered: $AppUserModelID"

Write-Host "📌 Creating Start Menu Shortcut..."
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = [System.IO.Path]::GetDirectoryName($ExePath)
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()
Write-Host "✅ Shortcut created: $ShortcutPath"

Write-Host "🔄 Restarting Windows Explorer..."
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Process explorer

Write-Host "🎉 Setup Complete! $AppName is now fully registered for Windows Notifications."
