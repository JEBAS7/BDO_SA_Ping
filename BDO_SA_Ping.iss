; Script do Inno Setup para o BDO SA Ping
; https://github.com/JEBAS7/BDO_SA_Ping

#define MyAppName "BDO SA Ping"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "JEBAS7"
#define MyAppURL "https://github.com/JEBAS7/BDO_SA_Ping"
#define MyAppExeName "BDO_SA_Ping.exe"

[Setup]
AppId={{A4F3D471-FEC8-4E99-9BBE-5F105FDED1CD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=dist_installer
OutputBaseFilename=Instalar_BDO_SA_Ping_v{#MyAppVersion}
SetupIconFile=assets\BDO.ico
LicenseFile=LICENSE
SolidCompression=yes
WizardStyle=modern dark windows11

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\BDO_SA_Ping\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BDO_SA_Ping\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent