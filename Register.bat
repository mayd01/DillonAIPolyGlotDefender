@echo off
setlocal

:: Define variables
set APP_NAME=DillyDefender
set EXE_PATH="%CD%\dilly_defender.exe"
set REG_PATH=HKCU\Software\Classes\Applications\dilly_defender.exe

echo Registering %APP_NAME% for Windows Notifications...

:: Add registry key using PowerShell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "New-Item -Path '%REG_PATH%' -Force | Out-Null; ^
  New-ItemProperty -Path '%REG_PATH%' -Name 'AppUserModelID' -Value '%APP_NAME%' -PropertyType String -Force | Out-Null; ^
  Write-Output 'Registration Complete!'"

echo Restarting Windows Explorer...
:: Restart Windows Explorer
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "Stop-Process -Name explorer -Force; ^
  Start-Process explorer;"

echo Done! Your app should now send notifications under '%APP_NAME%'.

endlocal
pause
