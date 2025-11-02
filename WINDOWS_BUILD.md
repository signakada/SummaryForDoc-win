# Windows版ビルド手順

## 変更履歴

### v1.2 - PyInstallerビルド対応（推奨）
- ✅ PyInstallerによる高速ビルドに対応
- ✅ flet_dropzoneを無効化（ビルド互換性のため）
- ✅ ファイルピッカーのみで動作（安定性重視）
- ✅ ビルド自動化スクリプト追加 (`build_pyinstaller.bat`)

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

### 🚀 方法1: PyInstallerビルド（推奨）

**メリット**:
- ✅ 高速ビルド（5-10分）
- ✅ 安定性が高い
- ✅ ファイルピッカーが確実に動作
- ✅ 自動化スクリプトあり

#### クイックビルド

```cmd
build_pyinstaller.bat
```

**このスクリプトは以下を自動実行します:**
1. 既存ビルドのクリーンアップ
2. PyInstallerでアプリをビルド
3. Tesseractファイルのコピー
4. ビルド結果の検証

#### 手動ビルド

```cmd
# 1. クリーンアップ
rmdir /s /q build
rmdir /s /q dist

# 2. PyInstallerでビルド
python -m PyInstaller SummaryForDoc.spec

# 3. Tesseractをコピー
mkdir "dist\SummaryForDoc\tesseract\tessdata"
copy "C:\Program Files\Tesseract-OCR\tesseract.exe" "dist\SummaryForDoc\tesseract\"
copy "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata" "dist\SummaryForDoc\tesseract\tessdata\"
copy "C:\Program Files\Tesseract-OCR\tessdata\jpn.traineddata" "dist\SummaryForDoc\tesseract\tessdata\"
copy "C:\Program Files\Tesseract-OCR\*.dll" "dist\SummaryForDoc\tesseract\"

# 4. 動作確認
cd dist\SummaryForDoc
SummaryForDoc.exe
```

**ビルド完了後の構造:**
```
dist/SummaryForDoc/
├── SummaryForDoc.exe      # メイン実行ファイル (14MB)
├── _internal/             # Python依存関係
└── tesseract/             # Tesseract OCR
    ├── tesseract.exe
    ├── tessdata/
    │   ├── eng.traineddata
    │   └── jpn.traineddata
    └── *.dll (60個以上)
```

**総サイズ**: 約221MB

---

### 方法2: Flet Buildビルド（代替）

**注意**: 初回ビルドに45分以上かかることがあります。時間がない場合は方法1を推奨。

#### ビルド手順

```cmd
# 1. 依存関係の確認
pip install -r requirements.txt

# 2. 既存のビルドをクリーンアップ
rmdir /s /q build

# 3. Fletでビルド
flet build windows

# 4. Tesseractをコピー
copy_tesseract_windows.bat

# 5. 動作確認
cd build\windows
SummaryForDoc.exe
```

**注意**: ビルド時に `flet-dropzone` に関する警告が表示される場合がありますが、現在は無効化されているため無視してください。

アプリが起動したら:
1. APIキーを設定
2. **「📁 ファイルを選択」ボタン**でファイルを選択
3. テスト用ファイル:
   - テキストファイル（.txt）
   - PDFファイル（.pdf）
   - 画像ファイル（.jpg, .png）
4. OCRとAI要約が正常に動作することを確認

**ファイル選択の確認**:
- ファイル選択ダイアログが正常に開く
- 複数ファイルの選択が可能（Ctrlキー + クリック）
- サポートされている形式のみが表示される

## トラブルシューティング

### ドラッグ&ドロップが利用できない（v1.2以降）

**現在の状態**:
- ドラッグ&ドロップ機能は、PyInstallerビルドとの互換性問題により**一時的に無効化**されています
- 代わりに、より安定した**ファイルピッカー機能**を使用してください

**ファイルの追加方法**:
1. 「📁 ファイルを選択」ボタンをクリック
2. ファイル選択ダイアログで目的のファイルを選択
3. 複数ファイルを選択する場合は**Ctrlキーを押しながらクリック**

**技術的な背景**:
- flet-dropzoneパッケージがPyInstallerでビルドしたアプリで正常に動作しない問題があります
- 将来のバージョンで修正される可能性があります
- 現在はFlet標準のFilePickerで同等の機能を提供しています

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
1. **📖 [日本語データの手動インストール手順](TESSERACT_JAPANESE_INSTALL.md)を参照**（推奨）
2. または、Tesseractを再インストールし、「Additional language data」で「Japanese」を選択
3. または、[tessdata リポジトリ](https://github.com/tesseract-ocr/tessdata)から `jpn.traineddata` をダウンロードして手動で配置:
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

### PyInstallerビルド（推奨）

ビルド後のディレクトリ構造:
```
dist/SummaryForDoc/
├── SummaryForDoc.exe      # メイン実行ファイル (14MB)
├── _internal/             # Python依存関係とライブラリ
│   ├── flet/              # Flet フレームワーク
│   ├── PIL/               # Pillow (画像処理)
│   ├── PyPDF2/            # PDF読み込み
│   └── その他のPythonパッケージ
└── tesseract/             # Tesseract OCR統合
    ├── tesseract.exe      # Tesseract実行ファイル
    ├── tessdata/          # 学習データ
    │   ├── eng.traineddata # 英語 (4.0MB)
    │   └── jpn.traineddata # 日本語 (2.4MB)
    ├── libtesseract-5.dll # Tesseract本体DLL
    ├── libleptonica-6.dll # 画像処理ライブラリ
    └── その他60個以上のDLL
```

**総サイズ**: 約221MB

### Flet Buildビルド

ビルド後のディレクトリ構造:
```
build/windows/
├── SummaryForDoc.exe      # メイン実行ファイル
├── data/                   # Fletのリソース
└── tesseract/              # Tesseract統合
    ├── tesseract.exe       # Tesseract実行ファイル
    ├── tessdata/           # 学習データ
    │   ├── eng.traineddata # 英語
    │   └── jpn.traineddata # 日本語
    ├── libtesseract-5.dll  # Tesseract本体DLL
    ├── libleptonica-*.dll  # 画像処理ライブラリ
    └── その他の依存DLL
```

## 配布用パッケージの作成

### 方法1: ZIPファイルでの配布（推奨）

#### PyInstallerビルドの場合
```cmd
cd dist
powershell Compress-Archive -Path SummaryForDoc -DestinationPath SummaryForDoc-Windows-v1.2.zip
```

#### Flet Buildの場合
```cmd
cd build
powershell Compress-Archive -Path windows -DestinationPath SummaryForDoc-Windows.zip
```

**配布時の注意事項**:
- ZIPファイルを展開後、`SummaryForDoc.exe` を実行
- Tesseractが統合されているため、別途インストール不要
- `.env`ファイルは含まれないため、各ユーザーがAPIキーを設定する必要あり

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
