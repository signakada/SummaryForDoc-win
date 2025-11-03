; Script generated for SummaryForDoc
; PyInstallerでビルドされたアプリケーション用のInno Setupスクリプト

#define MyAppName "SummaryForDoc"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "SummaryForDoc.exe"

[Setup]
; アプリケーションの基本情報
AppId={{E63F250B-52A1-4064-82BC-0889F573A24A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.\InnoSetupOutput
OutputBaseFilename=SummaryForDoc-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; アイコン設定
SetupIconFile=icon.ico

; アンインストール情報
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Windows Vista以降をサポート
MinVersion=6.1
PrivilegesRequired=admin

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; メインの実行ファイル
Source: "dist\SummaryForDoc\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; _internalフォルダ全体（PyInstallerの重要なランタイムファイル）
Source: "dist\SummaryForDoc\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; tesseractフォルダ全体（OCR機能に必要）
Source: "dist\SummaryForDoc\tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
