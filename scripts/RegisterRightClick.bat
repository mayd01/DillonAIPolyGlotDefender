@echo off
echo Creating registry entries for Dilly Defender...

:: Add context menu
reg add "HKCR\*\shell\ScanWithDillyDefender" /ve /t REG_SZ /d "Scan with Dilly Defender" /f
reg add "HKCR\*\shell\ScanWithDillyDefender" /v Icon /t REG_SZ /d "C:\Program Files\DillyDefender\Defender.ico" /f
reg add "HKCR\*\shell\ScanWithDillyDefender\command" /ve /t REG_SZ /d "\"C:\Program Files\DillyDefender\scripts\Scan.bat\" \"%%1\"" /f

echo Done!
pause
