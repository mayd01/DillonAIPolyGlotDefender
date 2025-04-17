@echo off
setlocal

set APP_PATH=C:\Program Files\DillyDefender

reg add "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\DillyDefender" /v AppUserModelID /t REG_SZ /d "{6D809377-6AF0-444B-8957-A3773F02200E}\DillyDefender\dilly_defender.exe" /f

reg add "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\DillyDefender" /v IconPath /t REG_SZ /d "%APP_PATH%\Defender.ico" /f

echo Application registered with Windows notification system!

endlocal
