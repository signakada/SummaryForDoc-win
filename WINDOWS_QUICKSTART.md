# Windows版クイックスタートガイド

このガイドでは、Windows環境で医療文書要約ツールをビルドして実行するための最短手順を説明します。

## 📋 必要なもの

1. **Python 3.9以上**
2. **Tesseract OCR**（画像ファイルからテキスト抽出に必要）
3. **AI APIキー**（Anthropic Claude または OpenAI GPT）

## 🚀 5分で始める

### ステップ1: Python環境のセットアップ

```cmd
# リポジトリをクローンまたはダウンロード
cd C:\Users\YourName\Desktop\SummaryForDoc-SimpleSummary

# 依存パッケージをインストール
pip install -r requirements.txt
```

### ステップ2: Tesseractのインストール

1. [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)から最新版をダウンロード
2. インストーラーを実行
3. **重要**: インストール時に「Japanese」言語データを選択
4. デフォルトのインストール先（`C:\Program Files\Tesseract-OCR`）を使用

### ステップ3: アプリをビルド

```cmd
# Windowsアプリをビルド（数分かかります）
flet build windows

# Tesseractをアプリにコピー
copy_tesseract_windows.bat
```

### ステップ4: アプリを起動

```cmd
# ビルドディレクトリに移動
cd build\windows

# アプリを起動
SummaryForDoc.exe
```

### ステップ5: 初期設定

アプリが起動したら：

1. **APIキーを設定**
   - 初回起動時に設定画面が表示されます
   - Anthropic または OpenAI のAPIキーを入力
   - 「保存して開始」をクリック

2. **ファイルを追加**
   - 方法1: 「📁 ファイルを選択」ボタンをクリック
   - 方法2: ファイルをドラッグ&ドロップ
   - サポート形式: .txt, .pdf, .jpg, .png

3. **要約を作成**
   - プリセットを選択（病歴欄用、サマリー用など）
   - 「🔍 個人情報削除を確認」または「個人情報を削除して要約作成」をクリック
   - 要約結果が表示されます

## 📱 2つのモード

### 確認モード（デフォルト、推奨）
- 個人情報削除を目視確認してから要約作成
- 検索機能で特定の文字列を探して手動削除可能
- 医療情報の取り扱いに最適

### 自動モード
- 個人情報削除と要約作成を一度に実行
- 迅速な処理が必要な場合に使用

## 🛠️ よくある問題

### ドラッグ&ドロップが動かない
→ **解決**: 「📁 ファイルを選択」ボタンを使用してください（常に動作します）

### Tesseractエラーが出る
→ **解決**:
1. Tesseractが正しくインストールされているか確認：
   ```cmd
   tesseract --version
   ```
2. 日本語データがあるか確認：
   ```cmd
   dir "C:\Program Files\Tesseract-OCR\tessdata\jpn.traineddata"
   ```

### ビルドに失敗する
→ **解決**:
1. 既存のビルドを削除：
   ```cmd
   rmdir /s /q build
   ```
2. もう一度ビルド：
   ```cmd
   flet build windows
   ```

## 🔄 開発モードで実行（ビルド不要）

ビルドせずにすぐに試したい場合：

```cmd
python main.py
```

**注意**:
- ドラッグ&ドロップは開発モードでは動作しません
- ファイル選択ボタンは使用できます
- 完全な機能を使うにはビルド版を使用してください

## 📖 詳細な情報

より詳しいビルド手順やトラブルシューティングについては、以下を参照してください：

- [WINDOWS_BUILD.md](WINDOWS_BUILD.md) - 詳細なビルド手順
- [README.md](README.md) - プロジェクト全体の説明
- [GETTING_STARTED.md](GETTING_STARTED.md) - 機能の詳細説明

## 💡 ヒント

- **複数ファイル対応**: 複数の診療録を一度に処理できます
- **カスタムプリセット**: 設定画面から独自のプロンプトを作成可能
- **検索機能**: 確認モードで特定の個人情報を検索・削除できます
- **クリップボードコピー**: 要約結果をワンクリックでコピー可能

## 🎯 次のステップ

1. カスタムプリセットを作成して自分の用途に合わせる
2. 確認モードで個人情報削除の精度を確認
3. よく使うプリセットを設定から選択

---

**問題が解決しない場合**: [Issues](https://github.com/your-repo/issues)で報告してください
