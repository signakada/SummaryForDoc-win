# Inno Setupインストーラー作成ガイド

## 必要なもの

- Inno Setup Compiler（https://jrsoftware.org/isinfo.php からダウンロード）
- ビルド済みのアプリケーション（dist/SummaryForDoc フォルダ）

## インストーラーの作成手順

### 1. Inno Setup Compilerのインストール

1. https://jrsoftware.org/isinfo.php から最新版をダウンロード
2. インストーラーを実行してインストール
3. 日本語サポートを含めてインストール

### 2. installer.issファイルの編集

`installer.iss`ファイルをテキストエディタで開き、以下を編集：

```iss
#define MyAppPublisher "Your Name"  ; ←あなたの名前に変更
```

AppIdのGUIDを生成する場合：
- Inno Setup Compilerのメニューから「Tools」→「Generate GUID」を実行
- 生成されたGUIDを`AppId={{YOUR-GUID-HERE}`に貼り付け

### 3. インストーラーのコンパイル

#### 方法A: GUIから実行
1. Inno Setup Compilerを起動
2. `installer.iss`ファイルを開く
3. メニューから「Build」→「Compile」をクリック（またはF9キー）

#### 方法B: コマンドラインから実行
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### 4. 完成

- `InnoSetupOutput`フォルダに`SummaryForDoc-Setup.exe`が生成されます
- このファイルを配布すれば、ユーザーは簡単にインストールできます

## 重要なポイント

### フォルダ構造が保持される理由

```iss
[Files]
; メインの実行ファイル
Source: "dist\SummaryForDoc\SummaryForDoc.exe"; DestDir: "{app}"; Flags: ignoreversion

; _internalフォルダ - recursesubdirs createallsubdirsで全てのサブフォルダも含める
Source: "dist\SummaryForDoc\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; tesseractフォルダ - OCR機能に必要
Source: "dist\SummaryForDoc\tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs

; Outputフォルダ - 出力用
Source: "dist\SummaryForDoc\Output\*"; DestDir: "{app}\Output"; Flags: ignoreversion recursesubdirs createallsubdirs
```

**重要なフラグの説明：**

- `*` - フォルダ内の全ファイルを指定
- `recursesubdirs` - サブフォルダも再帰的に含める
- `createallsubdirs` - インストール先にサブフォルダ構造を再現
- `ignoreversion` - 既存ファイルを上書き

### よくある問題と解決方法

#### 問題1: 「Add Folder」で追加しても動かない

**原因**: GUIの「Add Folder」だけでは、サブフォルダやすべてのファイルが含まれない場合があります。

**解決**: 上記のスクリプトのように、ワイルドカード`*`と`recursesubdirs`フラグを使用してください。

#### 問題2: インストール後に実行できない

**原因**:
- フォルダ構造が正しく保持されていない
- `_internal`フォルダが正しくインストールされていない

**解決**:
1. インストール先フォルダを確認（例: `C:\Program Files\SummaryForDoc\`）
2. 以下のフォルダ構造になっているか確認：
   ```
   C:\Program Files\SummaryForDoc\
   ├── SummaryForDoc.exe
   ├── _internal\
   │   └── （多数のファイル）
   ├── tesseract\
   │   └── （tesseract関連ファイル）
   └── Output\
   ```

#### 問題3: 「DLLが見つかりません」エラー

**原因**: `_internal`フォルダまたは`tesseract`フォルダ内のDLLが正しくコピーされていません。

**解決**: スクリプトの`[Files]`セクションで`recursesubdirs createallsubdirs`フラグが設定されていることを確認してください。

## カスタマイズ

### インストーラーにアイコンを追加

アプリケーションのアイコンファイル(.ico)がある場合：

```iss
[Setup]
SetupIconFile=path\to\your\icon.ico
```

### インストールディレクトリの変更

```iss
[Setup]
DefaultDirName={autopf}\{#MyAppName}  ; Program Files配下
; または
DefaultDirName={userdocs}\{#MyAppName}  ; ドキュメント配下
```

### アンインストール情報を追加

```iss
[Setup]
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
```

## テスト方法

1. 生成された`SummaryForDoc-Setup.exe`を実行
2. インストール先フォルダを確認
3. インストールされたアプリケーションを起動して動作確認
4. スタートメニューからも起動できることを確認
5. アンインストールが正常に動作することを確認

## トラブルシューティング

### コンパイルエラーが出る場合

1. パスが正しいか確認
2. `dist\SummaryForDoc`フォルダが存在するか確認
3. 日本語パスを使用している場合は英語パスに変更

### インストーラーのサイズが大きすぎる場合

Tesseractの言語データは大きいため、インストーラーのサイズも大きくなります。これは正常です。
圧縮設定を調整する場合：

```iss
[Setup]
Compression=lzma2/max  ; 最大圧縮
SolidCompression=yes
```

## 参考リンク

- Inno Setup公式サイト: https://jrsoftware.org/isinfo.php
- Inno Setup日本語ドキュメント: https://jrsoftware.org/ishelp/
