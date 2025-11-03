# インストーラー作成クイックスタート

## 🚀 最速の方法（3ステップ）

### 1. Inno Setup Compilerのインストール

https://jrsoftware.org/isinfo.php から最新版をダウンロードしてインストール

### 2. インストーラーをビルド

`build_installer.bat`をダブルクリックするだけ！

### 3. 完成！

`InnoSetupOutput\SummaryForDoc-Setup.exe`が生成されます。

---

## 📋 詳細な手順

### 方法A: バッチファイルを使用（推奨）

1. `build_installer.bat`をダブルクリック
2. 自動的にコンパイルが開始されます
3. 完了すると、エクスプローラーで出力ファイルが表示されます

### 方法B: Inno Setup GUIを使用

1. Inno Setup Compilerを起動
2. `installer.iss`ファイルを開く
3. メニューから「Build」→「Compile」（F9キー）
4. 完了！

---

## ❓ 問題が発生した場合

### エラー: "ファイルが見つかりません"

**原因**: ビルドされたアプリケーションがない

**解決**: 先に`build_pyinstaller.bat`を実行してアプリケーションをビルドしてください

### エラー: "Inno Setup Compilerが見つかりません"

**原因**: Inno Setupがインストールされていないか、パスが異なる

**解決**:
1. Inno Setupをインストール: https://jrsoftware.org/isinfo.php
2. または、`build_installer.bat`の以下の行を編集：
   ```batch
   set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
   ```

### インストーラーは作成できるが、インストール後に実行できない

これは**今回修正した問題**です！

**以前の問題**: フォルダを「Add Folder」で追加しても、サブフォルダやすべてのファイルが含まれていなかった

**修正内容**:
- `recursesubdirs createallsubdirs`フラグを追加
- ワイルドカード`*`を使用してすべてのファイルを含める
- フォルダ構造を正しく保持

```iss
[Files]
; ❌ 間違い: これだけでは不十分
Source: "dist\SummaryForDoc\_internal\"; DestDir: "{app}\_internal";

; ✅ 正解: すべてのファイルとサブフォルダを含める
Source: "dist\SummaryForDoc\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
```

---

## 📦 インストーラーに含まれるもの

```
インストール先 (例: C:\Program Files\SummaryForDoc\)
├── SummaryForDoc.exe          ← メインの実行ファイル
├── _internal\                 ← PyInstallerのランタイム（重要！）
│   ├── base_library.zip
│   ├── *.pyd ファイル
│   └── その他の依存ファイル
├── tesseract\                 ← OCR機能
│   ├── tesseract.exe
│   ├── tessdata\              ← 言語データ
│   └── *.dll ファイル
└── Output\                    ← 出力フォルダ
```

すべてのフォルダとファイルが正しくインストールされるため、インストール後すぐに実行できます。

---

## 🎨 カスタマイズ

### アプリケーション情報の変更

`installer.iss`の先頭部分を編集：

```iss
#define MyAppName "SummaryForDoc"
#define MyAppVersion "1.0"              ← バージョン番号を変更
#define MyAppPublisher "Your Name"       ← あなたの名前に変更
#define MyAppExeName "SummaryForDoc.exe"
```

### 出力ファイル名の変更

```iss
[Setup]
OutputBaseFilename=SummaryForDoc-Setup  ← これを変更
```

### アイコンの追加

アイコンファイル(.ico)を用意して：

```iss
[Setup]
SetupIconFile=path\to\your\icon.ico
```

---

## ✅ 動作確認

1. `SummaryForDoc-Setup.exe`を実行
2. インストール先を確認（例: `C:\Program Files\SummaryForDoc\`）
3. 以下をチェック：
   - [ ] `SummaryForDoc.exe`が存在する
   - [ ] `_internal`フォルダとその中身がある
   - [ ] `tesseract`フォルダとその中身がある
   - [ ] アプリケーションが起動する
   - [ ] スタートメニューから起動できる
   - [ ] デスクトップアイコン（選択した場合）から起動できる
   - [ ] アンインストールが正常に動作する

---

## 📖 さらに詳しく知りたい場合

`INSTALLER_GUIDE.md`をご覧ください。詳細なトラブルシューティングやカスタマイズ方法が記載されています。

---

## 🎉 これで完了です！

インストーラーを配布すれば、ユーザーは簡単にアプリケーションをインストールできます。

質問や問題がある場合は、`INSTALLER_GUIDE.md`の「トラブルシューティング」セクションを参照してください。
