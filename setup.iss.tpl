#define MyAppName "$my_app_name"
#define MyAppVersion "$my_app_version"
#define MyAppPublisher "James Scholes"
#define MyAppURL "http://jscholesjscholes.net/codex"
#define MyAppExeName "codex.exe"

[Setup]
AppId={{CB4C7D26-CE2E-4AF7-AAD0-853606352084}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}2
DefaultGroupName={#MyAppName}
LicenseFile=$project_directory\LICENSE.txt
OutputDir=$project_directory
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "$distribution_directory\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "$project_directory\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Add to Calibre"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to EPUB"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to Text"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert_to_HTML"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to HTML"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to HTML (compressed)"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to ePub"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "Amazon.Kindle.content\shell\Convert to Text"; ValueType: none; Flags: deletekey noerror
Root: HKCR; Subkey: "AllFilesystemObjects\Shell\CodexShellIntegration"; ValueType: none; Flags: DELETEKEY dontcreatekey uninsdeletekey noerror
Root: HKCU; Subkey: "Software\Classes\AllFilesystemObjects\Shell\CodexShellIntegration"; ValueType: none; Flags: dontcreatekey uninsdeletekey noerror

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall
