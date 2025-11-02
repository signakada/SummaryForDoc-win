# 変更履歴

## v1.2 - PyInstallerビルド対応 (2025-11-02)

### 🎉 主要な変更

#### ビルドシステムの改善
- ✅ **PyInstallerによる高速ビルド対応**
  - ビルド時間: 5-10分（Flet buildは45分以上）
  - 自動化スクリプト追加: `build_pyinstaller.bat`
  - PyInstaller spec ファイル: `SummaryForDoc.spec`

#### 機能の変更
- ⚠️ **ドラッグ&ドロップ機能を一時的に無効化**
  - 理由: PyInstallerビルドとの互換性問題
  - 影響: `main.py` Line 10-11 で `DROPZONE_AVAILABLE = False` に設定
  - 代替: Flet標準のFilePickerで同等の機能を提供
  - 複数ファイル選択可能（Ctrlキー + クリック）

#### Tesseract統合の改善
- ✅ Tesseract OCRの完全統合
  - 英語・日本語データを含む
  - 60個以上のDLLを自動コピー
  - ビルド後すぐに使用可能

### 📝 新規ファイル

| ファイル名 | 説明 |
|-----------|------|
| `build_pyinstaller.bat` | PyInstallerビルドの自動化スクリプト |
| `TESTING_GUIDE.md` | 詳細なテスト手順ガイド |
| `BUILD_COMPLETE.md` | ビルド完了サマリー |
| `QUICKSTART_BUILT_APP.md` | ビルド済みアプリのクイックスタート |
| `CHANGELOG.md` | このファイル - 変更履歴 |

### 📝 更新されたファイル

| ファイル名 | 変更内容 |
|-----------|---------|
| `main.py` | ドラッグ&ドロップ機能を無効化（Line 10-11） |
| `SummaryForDoc.spec` | PyInstaller設定を最適化（hiddenimportsをクリーン化） |
| `WINDOWS_BUILD.md` | PyInstallerビルド手順を追加、トラブルシューティング更新 |
| `README.md` | PyInstallerビルド方法を追加、ドラッグ&ドロップ無効化の注記追加 |
| `TESSERACT_JAPANESE_INSTALL.md` | （既存）日本語データの手動インストール手順 |

### 🔧 技術的な詳細

#### ビルド構成
- **ビルドツール**: PyInstaller 6.16.0
- **Python**: 3.14.0
- **Flet**: 0.28.3
- **出力ディレクトリ**: `dist/SummaryForDoc/`
- **総サイズ**: 約221MB

#### ファイル構造
```
dist/SummaryForDoc/
├── SummaryForDoc.exe (14MB)
├── _internal/ (Python依存関係)
└── tesseract/ (Tesseract OCR)
    ├── tesseract.exe
    ├── tessdata/
    │   ├── eng.traineddata (4.0MB)
    │   └── jpn.traineddata (2.4MB)
    └── 60個以上のDLL
```

#### コード変更

**main.py (Line 10-11)**
```python
# ドラッグ&ドロップはビルド環境で問題が多いため、無効化
DROPZONE_AVAILABLE = False
```

**SummaryForDoc.spec (Line 9)**
```python
hiddenimports=[],  # flet_dropzoneを削除
```

### 🐛 既知の問題

#### ドラッグ&ドロップ機能
- **問題**: flet-dropzoneパッケージがPyInstallerビルドで動作しない
- **影響**: ドラッグ&ドロップでのファイル追加ができない
- **回避策**: ファイルピッカーボタン（📁 ファイルを選択）を使用
- **将来の対応**: flet-dropzoneの互換性が改善されたら再度有効化を検討

#### Flet Buildの速度
- **問題**: 初回ビルドに45分以上かかる
- **影響**: 開発サイクルが遅くなる
- **回避策**: PyInstallerを使用（5-10分）

### ⚙️ ビルド方法の変更

#### v1.2以前
```cmd
flet build windows
copy_tesseract_windows.bat
```

#### v1.2以降（推奨）
```cmd
build_pyinstaller.bat
```

または手動で:
```cmd
python -m PyInstaller SummaryForDoc.spec
# Tesseractファイルをコピー...
```

### 📖 ドキュメントの改善

#### 新規ドキュメント
- **TESTING_GUIDE.md**: 包括的なテスト手順
  - 基本機能テスト
  - OCR機能テスト
  - エラーケーステスト
  - テストチェックリスト

- **BUILD_COMPLETE.md**: ビルド完了サマリー
  - ビルド情報
  - クイックスタート
  - 次のステップ
  - トラブルシューティング

- **QUICKSTART_BUILT_APP.md**: ビルド済みアプリの使い方
  - 5分で始めるガイド
  - 基本的な使い方
  - 実際の使用例
  - 注意事項

#### 更新されたドキュメント
- **WINDOWS_BUILD.md**:
  - PyInstallerビルド手順を追加（方法1: 推奨）
  - Flet buildを代替方法として明記
  - ドラッグ&ドロップ無効化の説明追加
  - トラブルシューティングセクション更新

- **README.md**:
  - PyInstallerビルド方法を追加
  - ドラッグ&ドロップ無効化の注記
  - ビルド方法の選択肢を明示

### 🚀 次のバージョンの計画

#### v1.3 予定
- [ ] カスタムプロンプト機能のGUI実装
- [ ] ドラッグ&ドロップの再実装（互換性問題解決後）
- [ ] 設定の永続化改善
- [ ] エラーハンドリングの強化

#### v2.0 予定
- [ ] macOS版のビルドとテスト
- [ ] Linux版のサポート
- [ ] テンプレートのカスタマイズ機能
- [ ] バッチ処理機能

### 🙏 謝辞

このバージョンは以下の問題を解決するために作成されました:
1. Tesseractの日本語データインストール問題
2. Tesseractの環境変数PATH問題
3. flet buildの長いビルド時間
4. flet-dropzoneのビルド互換性問題

すべての問題が解決され、安定したビルドが完成しました。

---

## v1.1 - Windows互換性の改善

### 変更内容
- ファイルピッカーをクロスプラットフォーム対応に変更
- ドラッグ&ドロップのWindows対応を強化
- pyproject.toml追加でビルド設定を明示化

---

## v1.0 - 初回リリース

### 機能
- テキスト・PDF・画像ファイルの読み込み
- 個人情報の自動削除
- AI要約生成（病歴・症状の詳細・全期間サマリー）
- 複数のテンプレート対応
- OCR機能（日本語対応）

---

**最終更新**: 2025-11-02
