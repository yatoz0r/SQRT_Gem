; Inno Setup Script for SQRT_Gem (High-Precision Calculator)
; Satisfies Requirements: Sections 8, 9, 10, 11 of TZ_1.md

#define MyAppName "SQRT_Gem"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SQRT_Gem Team"
#define MyAppURL "https://github.com/yatoz0r/SQRT_Gem"
#define MyAppExeName "SQRT_Gem.exe"

[Setup]
AppId={{C8E28B91-4475-4C3D-8692-7E1A63DC458F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist_installer
OutputBaseFilename=SQRT_Gem_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\SQRT_Gem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Section 10 Requirement: Prompt user whether to keep or remove user data
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
  UserChoice: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\SQRT_Gem');
    if DirExists(DataDir) then
    begin
      UserChoice := MsgBox(
        'Удалить также пользовательские данные (историю вычислений и настройки)?' + #13#10 +
        'Do you also want to delete user data (calculation history and settings)?',
        mbConfirmation, MB_YESNO
      );
      if UserChoice = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;
