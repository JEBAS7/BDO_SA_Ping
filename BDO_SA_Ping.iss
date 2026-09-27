; =====================================================================
; Script do Inno Setup para o BDO SA Ping
; https://github.com
; =====================================================================

#define MyAppName "BDO SA Ping"
#define MyAppVersion "1.0.1.3"
#define MyAppPublisher "JEBAS7"
#define MyAppURL "https://github.com"
#define MyAppExeName "BDO_SA_Ping.exe"

[Setup]
; --- Identificação do Aplicativo ---
AppId={{A4F3D471-FEC8-4E99-9BBE-5F105FDED1CD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

; --- Informações de Versão do Executável (Propriedades do Windows) ---
VersionInfoVersion={#MyAppVersion}
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright="Copyright © 2026 {#MyAppPublisher}"

; --- Links de Suporte ---
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; --- Configurações de Instalação e Pastas ---
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=dist_installer
OutputBaseFilename=Instalar_BDO_SA_Ping_v{#MyAppVersion}

; --- Compatibilidade do Sistema (Apenas 64-bit) ---
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog

; --- Visual e Aparência ---
SetupIconFile=assets\BDO.ico
LicenseFile=LICENSE
SolidCompression=yes
WizardStyle=modern dark windows11

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
; Opção para criar ícone na Área de Trabalho
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Arquivos do programa que serão empacotados
Source: "dist\BDO_SA_Ping\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BDO_SA_Ping\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Atalhos no Menu Iniciar e Área de Trabalho
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Executar o programa automaticamente após o término da instalação
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
