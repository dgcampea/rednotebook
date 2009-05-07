; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{82A7E9C3-D3F3-4B85-9AC3-D0E011D19E50}
AppName=RedNotebook
AppVerName=RedNotebook 0.6.8
; AppPublisher=Jendrik Seipp
AppPublisherURL=http://rednotebook.sourceforge.net
AppSupportURL=http://rednotebook.sourceforge.net
AppUpdatesURL=http://rednotebook.sourceforge.net
DefaultDirName={pf}\RedNotebook
DefaultGroupName=RedNotebook
AllowNoIcons=yes
OutputBaseFilename=rednotebook-0.6.8-win32
SetupIconFile=rednotebook.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\*"; Excludes: "rednotebook.log"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\RedNotebook"; Filename: "{app}\redNotebook.exe"
Name: "{group}\{cm:UninstallProgram,RedNotebook}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\RedNotebook"; Filename: "{app}\redNotebook.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\RedNotebook"; Filename: "{app}\redNotebook.exe"; Tasks: quicklaunchicon

;experimental
Name: "{userstartup}\RedNotebook"; Filename: "{app}\redNotebook.exe"; Flags: unchecked


[Run]
Filename: "{app}\redNotebook.exe"; Description: "{cm:LaunchProgram,RedNotebook}"; Flags: nowait postinstall skipifsilent


