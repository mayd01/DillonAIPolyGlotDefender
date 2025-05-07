
[Setup]
AppName=DillyDefender
AppVersion=1.0.0
AppPublisher=Dillon May AI and Cloud
AppPublisherURL=https://dillonmay.com
AppSupportURL=https://defender.dillonmay.com
AppUpdatesURL=https://defender.dillonmay.com
DefaultDirName={pf}\DillyDefender
DefaultGroupName=DillyDefender
OutputBaseFilename=DMZInstaller
SetupIconFile=C:\Users\dtmay\dillyDefender\Defender.ico
UninstallDisplayIcon={app}\Defender.ico
Compression=lzma
SolidCompression=yes
WizardImageFile=C:\Users\dtmay\Desktop\Defender.bmp
WizardSmallImageFile=C:\Users\dtmay\Desktop\Defender.bmp

LicenseFile="C:\Users\dtmay\Desktop\license.txt"
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "C:\Users\dtmay\dillyDefender\target\release\dilly_defender.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\dillyDefender\target\release\defender_ui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\dillyDefender\Defender.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\dillyDefender\Defender.jpg"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\Desktop\app.manifest"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\Desktop\RegisterRightClick.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\dtmay\dillyDefender\AITraining\TrainingTools\D2\bin\*"; DestDir: "{app}\bin"; Flags: recursesubdirs createallsubdirs
Source: "C:\Users\dtmay\dillyDefender\scripts\Register.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "C:\Users\dtmay\dillyDefender\scripts\Scan.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "C:\Users\dtmay\Desktop\clamav\*"; DestDir: "{app}\clamav"; Flags: recursesubdirs ignoreversion 

[Icons]
Name: "{group}\DillyDefender"; Filename: "{app}\dilly_defender.exe"; IconFilename: "{app}\Defender.ico"
Name: "{commondesktop}\DillyDefender UI"; Filename: "{app}\defender_ui.exe"; IconFilename: "{app}\Defender.ico"; Tasks: desktopicon


[Registry]
Root: HKLM; Subkey: "Software\DillyDefender"; ValueName: "InstallPath"; ValueType: string; ValueData: "{app}"
Root: HKLM; Subkey: "Software\DillyDefender"; ValueName: "Version"; ValueType: string; ValueData: "1.0.0"
Root: HKLM; Subkey: "Software\DillyDefender"; ValueName: "Enabled"; ValueType: string; ValueData: "1"
Root: HKLM; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueName: "DillyDefender"; ValueType: string; ValueData: """{app}\\dilly_defender.exe"" passive-scan -d ""%USERPROFILE%\\Downloads"""

[Run]
Filename: "{cmd}"; Parameters: "/C mkdir C:\ProgramData\DillyDefender\Logs\"; Flags: runhidden
Filename: "{cmd}"; Parameters: "/C setx DLogger ""C:\ProgramData\DillyDefender\Logs"" /M"; Flags: runhidden
Filename: "{app}\RegisterRightClick.bat";
Filename: "{app}\scripts\Register.bat"; 

[UninstallDelete]
Type: filesandordirs; Name: "C:\ProgramData\DillyDefender\Logs"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut for DillyDefender UI"; GroupDescription: "Additional icons:"
