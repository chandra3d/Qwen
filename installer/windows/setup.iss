; Blender AI Copilot Windows Installer Script
; Requires Inno Setup 6.x or later

#define MyAppName "Blender AI Copilot"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Blender AI Copilot Team"
#define MyAppURL "https://github.com/blender-copilot"
#define MyAppExeName "blender-copilot.exe"

[Setup]
AppId={{A3B5C7D9-1234-5678-90AB-CDEF12345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\..\LICENSE
OutputDir=output
OutputBaseFilename=BlenderAICopilot-Setup-{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\blender-copilot.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "..\..\src\desktop_client\src-tauri\target\release\blender-copilot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\src\backend\main.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\src\backend\services\*"; DestDir: "{app}\backend\services"; Flags: ignoreversion recursesubdirs
Source: "..\..\src\memory_db\*"; DestDir: "{app}\memory_db"; Flags: ignoreversion
Source: "..\..\src\ocr_service\*"; DestDir: "{app}\ocr_service"; Flags: ignoreversion
Source: "..\..\src\blender_addon\*"; DestDir: "{app}\blender_addon"; Flags: ignoreversion

; Python embedded (for Windows)
Source: "python-embed\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs

; Requirements
Source: "..\..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Configuration
Source: "..\..\config.example.json"; DestDir: "{app}"; DestName: "config.json"; Flags: ignoreversion

; Documentation
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\blender-copilot.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\blender-copilot.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\blender-copilot.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\python\python.exe"; Parameters: "-m pip install --upgrade pip"; Flags: runhidden waituntilterminated
Filename: "{app}\python\python.exe"; Parameters: "-m pip install -r requirements.txt"; Flags: runhidden waituntilterminated
Filename: "{app}\blender-copilot.exe"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked

[Code]
var
  InstallBlenderAddonPage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  InstallBlenderAddonPage := CreateInputOptionPage(
    wpWelcome,
    'Blender Add-on Installation',
    'Install Blender Add-on',
    'Should the installer configure the Blender add-on automatically?',
    True,
    False
  );
  InstallBlenderAddonPage.Add('Install add-on to Blender 4.5+ configuration directory');
  InstallBlenderAddonPage.Values[0] := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BlenderAddonPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    if InstallBlenderAddonPage.Values[0] then
    begin
      // Copy add-on to Blender scripts directory
      BlenderAddonPath := ExpandConstant('{userappdata}') + '\Blender Foundation\Blender\4.5\scripts\addons\blender_copilot';
      
      if DirExists(BlenderAddonPath) then
        DelTree(BlenderAddonPath, True, True, True);
      
      ExtractTemporaryFile('blender_addon');
      // Additional installation logic would go here
    end;
  end;
end;

function IsBlenderRunning(): Boolean;
begin
  Result := FindWindowByClassName('Blender') <> 0;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpReady then
  begin
    if IsBlenderRunning() then
      MsgBox('Warning: Blender is currently running. Please close Blender before installing the add-on.', mbWarning, MB_OK);
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\Blender Foundation\Blender\4.5\scripts\addons\blender_copilot"
Type: filesandordirs; Name: "{localappdata}\blender-copilot"
