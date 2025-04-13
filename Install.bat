@echo off
setlocal

echo Installing DillyDefender...
echo This script will install DillyDefender and register it for Windows Notifications.
set ZIP_FILE_PATH="%cd%\file.zip"
set PROGRAMS_DIR="C:\Program Files\DillyDefender"
set TEMP_DIR="C:\Temp"

if not exist %TEMP_DIR% mkdir %TEMP_DIR%
if not exist %PROGRAMS_DIR% mkdir %PROGRAMS_DIR%

if not exist %ZIP_FILE_PATH% (
    echo The file %ZIP_FILE_PATH% does not exist.
    exit /b 1
)
move %ZIP_FILE_PATH% %PROGRAMS_DIR%

echo Unzipping the file...
powershell -command "Expand-Archive -Path '%PROGRAMS_DIR%\file.zip' -DestinationPath '%PROGRAMS_DIR%'"

call %PROGRAMS_DIR%\DillyDefender\Register.bat

del %TEMP_DIR%\file.zip
echo Installation complete.

endlocal
