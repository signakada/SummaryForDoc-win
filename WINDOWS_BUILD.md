# Windows版ビルド手順

## 変更履歴

### v1.1 - Windows互換性の改善
- ✅ ファイルピッカーをクロスプラットフォーム対応に変更（Flet標準FilePickerを使用）
- ✅ ドラッグ&ドロップのWindows対応を強化（file://URIとURLエンコード処理）
- ✅ pyproject.toml追加でビルド設定を明示化

## 前提条件

### 1. Python 3.9以上のインストール
- [Python公式サイト](https://www.python.org/downloads/windows/)からインストーラーをダウンロード
- インストール時に「Add Python to PATH」にチェックを入れる

### 2. Tesseract for Windowsのインストール
1. [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)からインストーラーをダウンロード
   - 推奨: tesseract-ocr-w64-setup-5.x.x.exe（64bit版）

2. インストール時の設定:
   - インストール先: `C:\Program Files\Tesseract-OCR` （デフォルト）
   - **重要**: 「Additional language data」で「Japanese」にチェックを入れる
   - 「English」もチェックされていることを確認

3. インストール後、環境変数PATHに追加されているか確認:
   ```cmd
   tesseract --version
   ```
   バージョン情報が表示されればOK

### 3. 必要なPythonパッケージのインストール
```cmd
pip install -r requirements.txt
```

## ビルド手順

### 1. 依存関係の確認
まず、必要なパッケージがすべてインストールされているか確認：
```cmd
pip install -r requirements.txt
```

### 2. 既存のビルドをクリーンアップ（初回は不要）
```cmd
rmdir /s /q build
```

### 3. Windows版アプリをビルド
```cmd
flet build windows
```

ビルドには数分かかります。完了すると `build\windows\` ディレクトリに実行ファイルが生成されます。

**注意**: ビルド時に `flet-dropzone` に関する警告が表示される場合がありますが、これは正常です。ビルド版ではドラッグ&ドロップ機能は正常に動作します。

### 4. Tesseractをアプリに統合
```cmd
copy_tesseract_windows.bat
```

このスクリプトは以下を実行します:
- Tesseract実行ファイルのコピー
- 日本語・英語の学習データのコピー
- 必要なDLLファイルのコピー

### 5. 動作確認
```cmd
cd build\windows
SummaryForDoc.exe
```

アプリが起動したら:
1. APIキーを設定
2. **ファイルピッカーボタン**でファイルを選択、または**ドラッグ&ドロップ**でファイルを追加
3. テスト用ファイル:
   - テキストファイル（.txt）
   - PDFファイル（.pdf）
   - 画像ファイル（.jpg, .png）
4. OCRとAI要約が正常に動作することを確認

**ドラッグ&ドロップの確認**:
- Windows Explorer からファイルをアプリウィンドウにドラッグ
- 複数ファイルの同時ドロップも可能
- サポートされていない形式は自動的にフィルタリング

## トラブルシューティング

### ドラッグ&ドロップが動作しない
**症状**: ファイルをドラッグしてもアプリに追加されない

**原因と解決方法**:
1. **開発モードで実行している**:
   - `python main.py` で実行している場合、flet-dropzoneは動作しません
   - **解決**: ビルド版（`flet build windows`）で実行してください

2. **管理者権限の問題**:
   - アプリを管理者権限で実行している場合、通常のExplorerからのドラッグ&ドロップができないことがあります
   - **解決**: 管理者権限なしでアプリを実行してください

3. **ファイル形式の問題**:
   - サポートされていない形式（.docx, .xlsxなど）はドロップできません
   - **確認**: .txt, .pdf, .jpg, .png のみサポート

4. **代替手段**:
   - ドラッグ&ドロップが使えない場合は、「📁 ファイルを選択」ボタンをクリック
   - Fletの標準FilePickerが開きます（全プラットフォーム対応）

### ファイルピッカーが開かない
**症状**: 「📁 ファイルを選択」ボタンを押してもファイル選択ダイアログが表示されない

**解決方法**:
1. アプリを再起動してください
2. Windowsのセキュリティ設定でアプリがブロックされていないか確認
3. コマンドプロンプトから実行して、エラーメッセージを確認：
   ```cmd
   cd build\windows
   SummaryForDoc.exe
   ```

### エラー: Tesseractが見つかりません
**原因**: Tesseractが正しくインストールされていない、またはパスが異なる

**解決方法**:
1. Tesseractのインストール先を確認:
   ```cmd
   where tesseract
   ```

2. 標準インストール先（`C:\Program Files\Tesseract-OCR`）以外にインストールした場合は、`copy_tesseract_windows.bat` の6行目を修正:
   ```batch
   set TESSERACT_PATH=C:\Program Files\Tesseract-OCR
   ```
   ↓
   ```batch
   set TESSERACT_PATH=実際のインストールパス
   ```

### エラー: jpn.traineddata が見つかりません
**原因**: インストール時に日本語学習データを選択していない

**解決方法**:
1. Tesseractを再インストールし、「Additional language data」で「Japanese」を選択
2. または、[tessdata リポジトリ](https://github.com/tesseract-ocr/tessdata)から `jpn.traineddata` をダウンロードして手動で配置:
   ```
   C:\Program Files\Tesseract-OCR\tessdata\jpn.traineddata
   ```

### エラー: ビルドディレクトリが見つかりません
**原因**: `flet build windows` を実行していない

**解決方法**:
先に `flet build windows` を実行してからスクリプトを実行

### OCRが動作しない
**確認ポイント**:
1. `build\windows\tesseract\` ディレクトリが存在するか
2. `build\windows\tesseract\tesseract.exe` が存在するか
3. `build\windows\tesseract\tessdata\jpn.traineddata` が存在するか
4. 必要なDLLがすべてコピーされているか

**デバッグモードで起動**:
コマンドプロンプトから実行すると、デバッグログが表示されます:
```cmd
cd build\windows
SummaryForDoc.exe
```

ログから以下を確認:
- `DEBUG: sys.frozen = True`
- `DEBUG: platform = win32`
- `DEBUG: tesseract_cmd.exists() = True`

## ビルド構成

ビルド後のディレクトリ構造:
```
build/windows/
├── SummaryForDoc.exe      # メイン実行ファイル
├── data/                   # Fletのリソース
└── tesseract/              # Tesseract統合（copy_tesseract_windows.batで追加）
    ├── tesseract.exe       # Tesseract実行ファイル
    ├── tessdata/           # 学習データ
    │   ├── eng.traineddata # 英語
    │   └── jpn.traineddata # 日本語
    ├── libtesseract-5.dll  # Tesseract本体DLL
    ├── libleptonica-*.dll  # 画像処理ライブラリ
    └── その他の依存DLL
```

## 配布用パッケージの作成

### 方法1: ZIPファイルでの配布
```cmd
cd build
powershell Compress-Archive -Path windows -DestinationPath SummaryForDoc-Windows.zip
```

### 方法2: インストーラーの作成
[Inno Setup](https://jrsoftware.org/isinfo.php) などのツールを使用してインストーラーを作成できます。

## 開発環境での実行

Windows環境で開発する場合:
```cmd
python main.py
```

注意: flet-dropzone は開発モードでは動作しません。ドラッグ&ドロップ機能をテストするには、必ずビルド版で確認してください。

## 次のステップ

- [ ] Windows環境でビルドとテストを実施
- [ ] カスタムプロンプト機能のGUI修正（開発メモ_カスタムプロンプト機能.txt参照）
- [ ] コード署名の実施（オプション）
- [ ] インストーラーの作成（オプション）
- [ ] macOS版とWindows版の動作確認
