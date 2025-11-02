"""
医療文書要約ツール - メインGUIアプリ (Flet)
Mac・Windows・Linux対応
"""

import flet as ft
from pathlib import Path
from typing import List

# ドラッグ&ドロップはビルド環境で問題が多いため、無効化
DROPZONE_AVAILABLE = False

from src.config import config
from src.file_reader import FileReader
from src.pii_remover import PIIRemover
from src.summarizer import MedicalSummarizer
from src.prompts import PromptManager


class MedicalSummarizerApp:
    """医療文書要約ツール GUIアプリ"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "医療文書要約ツール"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

        # 状態管理
        self.selected_files: List[Path] = []
        self.cleaned_text = ""
        self.summary_result = None
        self.pii_log = []
        self.confirmation_mode = True   # 確認モード（デフォルトON）
        self.main_view = None           # メインビュー
        self.settings_view = None       # 設定ビュー

        # コンポーネント
        self.file_list = None
        self.preset_dropdown = None     # プリセット選択ドロップダウン
        self.process_button = None
        self.result_container = None
        self.status_text = None
        self.masked_text_field = None  # 編集可能なテキストフィールド
        self.confirm_button = None      # 確認完了ボタン
        self.search_field = None        # 検索フィールド
        self.search_results = []        # 検索結果のリスト
        self.current_search_index = 0   # 現在の検索結果インデックス
        self.search_result_text = None  # 検索結果表示テキスト
        self.confirmation_toggle = None # 確認モードトグル
        self.create_summary_button = None # 要約作成ボタン（確認モード用）

        # 初期化
        if not self._check_config():
            # APIキーが未設定の場合は設定画面を表示
            self._show_initial_setup()
        else:
            self._build_ui()

    def _check_config(self):
        """
        設定をチェック

        Returns:
            bool: 設定が正常な場合True
        """
        errors = config.validate_config()
        return len(errors) == 0

    def _show_snack_bar(self, message: str):
        """
        スナックバーを表示するヘルパーメソッド

        Args:
            message: 表示するメッセージ
        """
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def _build_ui(self):
        """UIを構築"""

        # タイトルと設定ボタン
        title_row = ft.Row([
            ft.Text(
                "医療文書要約ツール",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#1976d2"  # BLUE_700
            ),
            ft.IconButton(
                icon="settings",
                tooltip="設定",
                icon_color="#1976d2",
                on_click=self._show_settings_screen
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # FilePicker設定（クロスプラットフォーム対応）
        file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        self.page.overlay.append(file_picker)
        self.file_picker = file_picker

        # ファイル選択エリア
        def open_file_picker(e):
            print("ファイル選択ボタンがクリックされました")  # デバッグ
            try:
                # Fletの標準FilePickerを使用（全プラットフォーム対応）
                self.file_picker.pick_files(
                    dialog_title="ファイルを選択してください",
                    allowed_extensions=["txt", "pdf", "jpg", "jpeg", "png"],
                    allow_multiple=True
                )
            except Exception as ex:
                print(f"ファイルピッカーエラー: {ex}")
                import traceback
                traceback.print_exc()
                self._show_snack_bar(f"ファイル選択エラー: {str(ex)}")

        # ファイルリスト表示
        self.file_list = ft.Column(spacing=5)

        # ファイル選択エリアのコンテンツ
        file_select_content = ft.Column([
            ft.Icon("cloud_upload", size=48, color="#1976d2"),
            ft.Text(
                "ファイルをここにドラッグ&ドロップ" if DROPZONE_AVAILABLE else "ファイルを選択してください",
                size=16,
                weight=ft.FontWeight.BOLD,
                color="#1976d2"
            ),
            ft.Text("txt, pdf, jpg, png に対応", size=12, color="#616161"),
            ft.ElevatedButton(
                "📁 ファイルを選択",
                icon="upload_file",
                on_click=open_file_picker,
                style=ft.ButtonStyle(
                    bgcolor="#1976d2",
                    color="#ffffff",
                ),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10)

        # ドロップゾーンが利用可能な場合は、ドラッグ&ドロップ対応エリアを作成
        if DROPZONE_AVAILABLE:
            file_select_area = ftd.Dropzone(
                content=ft.Container(
                    content=file_select_content,
                    width=None,
                    height=180,
                    alignment=ft.alignment.center,
                    bgcolor="#e3f2fd",  # BLUE_50
                    border=ft.border.all(2, "#90caf9"),  # BLUE_200
                    border_radius=10,
                ),
                on_dropped=self._on_file_dropped,
            )
        else:
            # ドロップゾーンが利用できない場合は通常のコンテナ
            file_select_area = ft.Container(
                content=file_select_content,
                width=None,
                height=180,
                alignment=ft.alignment.center,
                bgcolor="#e3f2fd",  # BLUE_50
                border=ft.border.all(2, "#90caf9"),  # BLUE_200
                border_radius=10,
            )

        file_section = ft.Container(
            content=ft.Column([
                ft.Text("📄 読み込んだファイル:", size=16, weight=ft.FontWeight.BOLD),
                self.file_list,
                file_select_area,
            ]),
            padding=15,
            border=ft.border.all(1, "#90caf9"),  # BLUE_200
            border_radius=10,
        )

        # プリセット選択
        from src.presets import PresetManager

        # 設定から現在のプリセットを取得
        config_manager = config.get_config_manager()
        current_preset = config_manager.get_current_preset()

        preset_options = [
            ft.dropdown.Option(key="medical_history", text="病歴欄用（200~300文字）"),
            ft.dropdown.Option(key="symptom_description", text="病状記載用（200~300文字）"),
            ft.dropdown.Option(key="summary", text="サマリー用（1000文字程度）"),
            ft.dropdown.Option(key="care_insurance", text="介護保険意見書用（200~300文字）"),
            ft.dropdown.Option(key="format_only", text="診療情報提供書の整形（改行除去のみ）"),
        ]

        # カスタムプリセットを追加
        all_presets = PresetManager.get_all_presets()
        for key, preset in all_presets.items():
            if preset.is_custom:
                preset_options.append(
                    ft.dropdown.Option(key=key, text=f"📝 {preset.name}")
                )

        self.preset_dropdown = ft.Dropdown(
            label="プリセット",
            options=preset_options,
            value=current_preset,
            width=500,
            on_change=self._on_preset_changed
        )

        # 確認モードトグル
        self.confirmation_toggle = ft.Switch(
            label="確認モード（個人情報削除を目視確認してから要約作成）",
            value=True,
            active_color="#1976d2",
            on_change=self._on_toggle_confirmation_mode
        )

        options_section = ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 動作モード:", size=16, weight=ft.FontWeight.BOLD),
                self.confirmation_toggle,
                ft.Divider(),
                ft.Text("📝 プリセット選択:", size=16, weight=ft.FontWeight.BOLD),
                self.preset_dropdown,
            ]),
            padding=15,
            border=ft.border.all(1, "#90caf9"),  # BLUE_200
            border_radius=10,
        )

        # 実行ボタン（初期状態は確認モードON）
        self.process_button = ft.ElevatedButton(
            "🔍 個人情報削除を確認",
            icon="search",
            on_click=self._on_process,
            style=ft.ButtonStyle(
                color="#ffffff",  # WHITE
                bgcolor="#1976d2",  # BLUE_700
            ),
            height=50,
            disabled=True
        )

        # ステータステキスト
        self.status_text = ft.Text("", size=14, color="#616161")  # GREY_700

        # 結果表示エリア
        self.result_container = ft.Column(spacing=15)

        # メインレイアウト
        self.page.add(
            title_row,
            ft.Divider(),
            file_section,
            options_section,
            self.process_button,
            self.status_text,
            ft.Divider(),
            self.result_container
        )

    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """ファイルピッカーの結果を処理"""
        if e.files:
            print(f"{len(e.files)}個のファイルが選択されました")
            for file in e.files:
                file_path = Path(file.path)
                if file_path.exists() and file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    print(f"ファイルを追加: {file_path.name}")

            self._update_file_list()
            self.process_button.disabled = len(self.selected_files) == 0
            self.page.update()
        else:
            print("ファイルが選択されませんでした")

    def _on_file_dropped(self, e):
        """ファイルがドロップされたときの処理（Windows対応強化）"""
        if not hasattr(e, 'files') or not e.files:
            print("ファイルがドロップされませんでした")
            return

        print(f"ドロップされたファイル: {e.files}")

        # ドロップされたファイルを追加
        for file_path_str in e.files:
            try:
                # file:// URIスキームを削除（Windowsで発生する可能性）
                if file_path_str.startswith('file:///'):
                    file_path_str = file_path_str[8:]  # file:/// を削除
                elif file_path_str.startswith('file://'):
                    file_path_str = file_path_str[7:]  # file:// を削除

                # URLエンコードされたパスをデコード
                from urllib.parse import unquote
                file_path_str = unquote(file_path_str)

                file_path = Path(file_path_str)

                if file_path.exists() and file_path not in self.selected_files:
                    # サポートされているファイル形式かチェック
                    if file_path.suffix.lower() in ['.txt', '.pdf', '.jpg', '.jpeg', '.png']:
                        self.selected_files.append(file_path)
                        print(f"ファイルを追加: {file_path.name}")
                    else:
                        print(f"サポートされていないファイル形式: {file_path.suffix}")
                else:
                    print(f"ファイルが見つからないか、既に追加されています: {file_path_str}")
            except Exception as ex:
                print(f"ファイルパス処理エラー: {file_path_str} - {ex}")

        self._update_file_list()
        self.process_button.disabled = len(self.selected_files) == 0
        self.page.update()

    def _update_file_list(self):
        """ファイルリストを更新"""
        self.file_list.controls.clear()

        if not self.selected_files:
            self.file_list.controls.append(
                ft.Text("（ファイルが選択されていません）", color="#9e9e9e")  # GREY_500
            )
        else:
            for i, file_path in enumerate(self.selected_files):
                def make_remove_handler(index):
                    def handler(e):
                        self.selected_files.pop(index)
                        self._update_file_list()
                        self.process_button.disabled = len(self.selected_files) == 0
                        self.page.update()
                    return handler

                file_row = ft.Row([
                    ft.Icon("description", size=20, color="#42a5f5"),  # BLUE_400
                    ft.Text(file_path.name, expand=True),
                    ft.IconButton(
                        icon="delete",
                        icon_color="#ef5350",  # RED_400
                        tooltip="削除",
                        on_click=make_remove_handler(i)
                    )
                ])
                self.file_list.controls.append(file_row)

    def _on_preset_changed(self, e):
        """プリセットが変更されたときの処理"""
        # 設定に保存
        config_manager = config.get_config_manager()
        config_manager.save_current_preset(self.preset_dropdown.value)

    def _on_toggle_confirmation_mode(self, e):
        """確認モードのトグルが変更されたときの処理"""
        self.confirmation_mode = self.confirmation_toggle.value

        # ボタンのラベルを更新
        if self.confirmation_mode:
            self.process_button.text = "🔍 個人情報削除を確認"
            self.process_button.icon = "search"
        else:
            self.process_button.text = "個人情報を削除して要約作成"
            self.process_button.icon = "play_arrow"

        self.page.update()

    def _on_process(self, e):
        """要約作成ボタンが押されたときの処理"""
        self.process_button.disabled = True
        self.result_container.controls.clear()
        self.status_text.value = "処理中..."
        self.page.update()

        try:
            # 1. ファイル読み込み
            self.status_text.value = "📖 ファイルを読み込み中..."
            self.page.update()

            reader = FileReader()
            all_text = reader.read_multiple_files(self.selected_files)

            # 2. 個人情報削除
            self.status_text.value = "🔒 個人情報を削除中..."
            self.page.update()

            remover = PIIRemover()
            self.cleaned_text, self.pii_log = remover.clean_text(all_text)

            # 確認モードの分岐
            if self.confirmation_mode:
                # 確認モードON：確認画面を表示
                self.status_text.value = "✅ 個人情報の削除が完了しました（確認してください）"
                self.status_text.color = "#1976d2"  # BLUE_700
                self.page.update()

                # マスクされたテキストと削除サマリーを表示
                self._show_masked_text_with_summary(self.cleaned_text, remover.get_summary_report())
            else:
                # 確認モードOFF：自動で要約生成
                self._execute_summary_generation()

        except Exception as ex:
            self.status_text.value = f"❌ エラー: {str(ex)}"
            self.status_text.color = "#d32f2f"  # RED_700

        finally:
            self.process_button.disabled = False
            self.page.update()

    def _execute_summary_generation(self):
        """要約生成を実行（確認モードOFFまたは確認完了後）"""
        try:
            # 3. 要約生成
            preset_key = self.preset_dropdown.value
            from src.presets import PresetManager
            preset = PresetManager.get_preset(preset_key)

            if preset.is_format_only:
                self.status_text.value = "📝 テキストを整形中..."
            else:
                self.status_text.value = "🤖 AI要約を生成中..."
            self.page.update()

            summarizer = MedicalSummarizer()
            self.summary_result = summarizer.generate_summary(
                self.cleaned_text,
                preset_key=preset_key
            )

            if self.summary_result.error:
                raise Exception(self.summary_result.error)

            # 4. 結果表示
            self._show_results()

            # 5. ファイル保存
            saved_files = summarizer.save_results(self.summary_result)

            self.status_text.value = f"✅ 完了しました！ ({len(saved_files)}件のファイルを保存)"
            self.status_text.color = "#388e3c"  # GREEN_700
            self.page.update()

        except Exception as ex:
            self.status_text.value = f"❌ エラー: {str(ex)}"
            self.status_text.color = "#d32f2f"  # RED_700
            self.page.update()

    def _show_masked_text_with_summary(self, masked_text: str, summary_report: str):
        """マスクされたテキストと削除サマリーを表示（デバッグ用）"""
        self.result_container.controls.clear()

        # 削除サマリー
        self.result_container.controls.append(
            self._create_result_card(
                "🔒 個人情報削除サマリー",
                summary_report,
                "#fff3e0"  # ORANGE_50
            )
        )

        # 説明テキスト
        instruction_text = ft.Text(
            "⚠️ 下記のテキストを確認し、必要に応じて手動で個人情報を削除してください。\n"
            "検索機能を使って特定の文字列を探すことができます。\n"
            "確認が完了したら「確認完了して要約作成」ボタンを押してください。",
            size=14,
            color="#d32f2f",  # RED_700
            weight=ft.FontWeight.BOLD
        )

        # 検索フィールド
        self.search_field = ft.TextField(
            label="検索ワード（氏名、住所など）",
            width=300,
            border_color="#1976d2",
        )

        # 検索結果表示テキスト
        self.search_result_text = ft.Text("", size=12, color="#616161")

        # 検索ボタン
        search_button = ft.ElevatedButton(
            "🔍 検索",
            on_click=self._on_search,
            style=ft.ButtonStyle(
                bgcolor="#1976d2",
                color="#ffffff",
            ),
        )

        # 前へボタン
        prev_button = ft.IconButton(
            icon="arrow_back",
            tooltip="前の結果",
            on_click=self._on_prev_search,
        )

        # 次へボタン
        next_button = ft.IconButton(
            icon="arrow_forward",
            tooltip="次の結果",
            on_click=self._on_next_search,
        )

        # 削除ボタン
        delete_button = ft.ElevatedButton(
            "❌ この箇所を削除",
            on_click=self._on_delete_current_match,
            style=ft.ButtonStyle(
                bgcolor="#d32f2f",
                color="#ffffff",
            ),
        )

        # 検索バー
        search_bar = ft.Row([
            self.search_field,
            search_button,
            prev_button,
            next_button,
            delete_button,
            self.search_result_text,
        ], spacing=10)

        # 編集可能なマスク済みテキストフィールド
        self.masked_text_field = ft.TextField(
            value=masked_text,
            multiline=True,
            min_lines=10,
            max_lines=20,
            border_color="#1976d2",  # BLUE_700
            bgcolor="#ffffff",
        )

        # 確認完了して要約作成ボタン
        self.create_summary_button = ft.ElevatedButton(
            "✅ 確認完了して要約作成",
            icon="check_circle",
            on_click=self._on_create_summary_after_confirmation,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#388e3c",  # GREEN_700
            ),
            height=50,
        )

        # コンテナに追加
        masked_text_container = ft.Container(
            content=ft.Column([
                ft.Text("📝 マスク済み文字起こし（編集可能）", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                instruction_text,
                search_bar,
                ft.Divider(),
                self.masked_text_field,
                self.create_summary_button,
            ]),
            padding=15,
            bgcolor="#e3f2fd",  # BLUE_50
            border_radius=10,
        )

        self.result_container.controls.append(masked_text_container)
        self.page.update()

    def _on_search(self, e):
        """検索ボタンが押されたときの処理"""
        search_word = self.search_field.value
        if not search_word:
            self.search_result_text.value = "検索ワードを入力してください"
            self.search_result_text.color = "#d32f2f"
            self.page.update()
            return

        # テキスト内を検索
        text = self.masked_text_field.value
        self.search_results = []

        # すべてのマッチ箇所を見つける
        start = 0
        while True:
            pos = text.find(search_word, start)
            if pos == -1:
                break
            self.search_results.append(pos)
            start = pos + 1

        if not self.search_results:
            self.search_result_text.value = f"「{search_word}」は見つかりませんでした"
            self.search_result_text.color = "#616161"
            self.page.update()
            return

        # 最初の結果を表示
        self.current_search_index = 0
        self._show_search_result()

    def _on_prev_search(self, e):
        """前の検索結果に移動"""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self._show_search_result()

    def _on_next_search(self, e):
        """次の検索結果に移動"""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self._show_search_result()

    def _show_search_result(self):
        """現在の検索結果を表示"""
        if not self.search_results:
            return

        text = self.masked_text_field.value
        pos = self.search_results[self.current_search_index]
        search_word = self.search_field.value

        # 周辺テキストを取得（前後50文字）
        start = max(0, pos - 50)
        end = min(len(text), pos + len(search_word) + 50)
        context = text[start:end]

        # 検索結果情報を表示
        self.search_result_text.value = (
            f"🔍 {self.current_search_index + 1}/{len(self.search_results)}件目\n"
            f"位置: {pos}文字目\n"
            f"周辺: ...{context}..."
        )
        self.search_result_text.color = "#1976d2"
        self.page.update()

    def _on_delete_current_match(self, e):
        """現在の検索結果を削除"""
        if not self.search_results:
            self.search_result_text.value = "検索結果がありません"
            self.search_result_text.color = "#d32f2f"
            self.page.update()
            return

        text = self.masked_text_field.value
        pos = self.search_results[self.current_search_index]
        search_word = self.search_field.value

        # マッチ箇所を削除（空文字に置換）
        new_text = text[:pos] + text[pos + len(search_word):]
        self.masked_text_field.value = new_text

        # 検索結果リストを更新（削除後の位置を再計算）
        self.search_results.pop(self.current_search_index)

        # 後続の検索結果の位置を調整
        for i in range(self.current_search_index, len(self.search_results)):
            self.search_results[i] -= len(search_word)

        if self.search_results:
            # 次の結果を表示（範囲外なら最後の結果）
            if self.current_search_index >= len(self.search_results):
                self.current_search_index = len(self.search_results) - 1
            self._show_search_result()
            self.search_result_text.value += "\n✅ 削除しました"
        else:
            self.search_result_text.value = f"✅「{search_word}」はすべて削除されました"
            self.search_result_text.color = "#388e3c"

        self.page.update()

    def _on_create_summary_after_confirmation(self, e):
        """確認完了して要約作成ボタンが押されたときの処理"""
        # ユーザーが編集したテキストを取得
        self.cleaned_text = self.masked_text_field.value

        # 確認画面を非表示にする
        self.result_container.controls.clear()
        self.page.update()

        # 要約生成を実行
        self._execute_summary_generation()

    def _show_results(self):
        """結果を表示"""
        self.result_container.controls.clear()

        # 要約結果を表示
        if self.summary_result.content:
            self.result_container.controls.append(
                self._create_result_card(
                    self.summary_result.preset_name,
                    self.summary_result.content,
                    "#e3f2fd"  # BLUE_50
                )
            )

    def _create_result_card(self, title: str, content: str, bg_color):
        """結果カードを作成"""
        def copy_to_clipboard(e):
            self.page.set_clipboard(content)
            self._show_snack_bar(f"{title}をクリップボードにコピーしました")

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon="copy",
                        tooltip="コピー",
                        on_click=copy_to_clipboard
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text(content, size=14, selectable=True),
                ft.Text(f"({len(content)}文字)", size=12, color="#757575")  # GREY_600
            ]),
            padding=15,
            bgcolor=bg_color,
            border_radius=10,
        )

    def _show_initial_setup(self):
        """初回起動時の設定画面を表示"""
        self.page.clean()

        # タイトル
        title = ft.Text(
            "医療文書要約ツール - 初期設定",
            size=28,
            weight=ft.FontWeight.BOLD,
            color="#1976d2"
        )

        # 説明文
        description = ft.Text(
            "このアプリを使用するには、AIプロバイダーのAPIキーが必要です。\n"
            "Anthropic: https://console.anthropic.com/\n"
            "OpenAI: https://platform.openai.com/api-keys",
            size=14,
            color="#616161"
        )

        # プロバイダー選択
        provider_dropdown = ft.Dropdown(
            label="AIプロバイダー",
            options=[
                ft.dropdown.Option("anthropic", "Anthropic (Claude)"),
                ft.dropdown.Option("openai", "OpenAI (GPT)"),
            ],
            value="anthropic",
            width=500,
        )

        # Anthropic APIキー入力フィールド
        anthropic_key_field = ft.TextField(
            label="Anthropic APIキー",
            hint_text="sk-ant-...",
            password=True,
            can_reveal_password=True,
            width=500,
            border_color="#1976d2",
        )

        # OpenAI APIキー入力フィールド
        openai_key_field = ft.TextField(
            label="OpenAI APIキー",
            hint_text="sk-...",
            password=True,
            can_reveal_password=True,
            width=500,
            border_color="#1976d2",
            visible=False,
        )

        # プロバイダー変更時の処理
        def on_provider_change(e):
            if provider_dropdown.value == "anthropic":
                anthropic_key_field.visible = True
                openai_key_field.visible = False
            else:
                anthropic_key_field.visible = False
                openai_key_field.visible = True
            self.page.update()

        provider_dropdown.on_change = on_provider_change

        # 保存ボタン
        def save_and_continue(e):
            provider = provider_dropdown.value
            anthropic_key = anthropic_key_field.value
            openai_key = openai_key_field.value

            # 選択されたプロバイダーのAPIキーを確認
            if provider == "anthropic" and (not anthropic_key or not anthropic_key.strip()):
                self._show_snack_bar("Anthropic APIキーを入力してください")
                return
            elif provider == "openai" and (not openai_key or not openai_key.strip()):
                self._show_snack_bar("OpenAI APIキーを入力してください")
                return

            # 設定を保存
            config_manager = config.get_config_manager()
            if config_manager.save_api_settings(
                anthropic_api_key=anthropic_key.strip() if anthropic_key else None,
                openai_api_key=openai_key.strip() if openai_key else None,
                ai_provider=provider
            ):
                # 設定を再読み込み
                config.reload_config()

                # メイン画面を表示
                self.page.clean()
                self._build_ui()
                self._show_snack_bar("設定を保存しました")
            else:
                self._show_snack_bar("設定の保存に失敗しました")

        save_button = ft.ElevatedButton(
            "保存して開始",
            icon="check",
            on_click=save_and_continue,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#1976d2",
            ),
            height=50,
        )

        # レイアウト
        self.page.add(
            ft.Container(
                content=ft.Column([
                    title,
                    ft.Divider(),
                    description,
                    ft.Container(height=20),
                    provider_dropdown,
                    ft.Container(height=10),
                    anthropic_key_field,
                    openai_key_field,
                    ft.Container(height=20),
                    save_button,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center,
            )
        )

    def _show_settings_screen(self, e=None, tab="api"):
        """設定画面を表示

        Args:
            e: イベント（オプション）
            tab: 表示するタブ（"api" or "preset"）
        """
        # メインビューを保存
        if not self.main_view:
            self.main_view = list(self.page.controls)

        self.page.clean()

        # タイトル
        title = ft.Text(
            "設定",
            size=28,
            weight=ft.FontWeight.BOLD,
            color="#1976d2"
        )

        # 戻るボタン（共通）
        def back_to_main(e):
            self.page.clean()
            # メイン画面を再構築してカスタムプロンプトを反映
            self.main_view = None  # ビューをクリア
            self._build_ui()
            self.page.update()

        back_button = ft.ElevatedButton(
            "戻る",
            icon="arrow_back",
            on_click=back_to_main,
            style=ft.ButtonStyle(
                color="#1976d2",
                bgcolor="#e3f2fd",
            ),
        )

        # コンテンツコンテナ（切り替え可能）
        initial_content = self._create_api_settings_content() if tab == "api" else self._create_custom_preset_content()
        content_container = ft.Container(
            content=initial_content,
            expand=True,
        )

        # タブ切り替えボタン
        api_button = ft.ElevatedButton(
            "⚙️ API設定",
            style=ft.ButtonStyle(
                color="white" if tab == "api" else "#1976d2",
                bgcolor="#1976d2" if tab == "api" else "#e3f2fd",
            ),
        )

        preset_button = ft.ElevatedButton(
            "📝 カスタムプリセット",
            style=ft.ButtonStyle(
                color="white" if tab == "preset" else "#1976d2",
                bgcolor="#1976d2" if tab == "preset" else "#e3f2fd",
            ),
        )

        def switch_to_api(e):
            api_button.style.bgcolor = "#1976d2"
            api_button.style.color = "white"
            preset_button.style.bgcolor = "#e3f2fd"
            preset_button.style.color = "#1976d2"
            content_container.content = self._create_api_settings_content()
            self.page.update()

        def switch_to_preset(e):
            api_button.style.bgcolor = "#e3f2fd"
            api_button.style.color = "#1976d2"
            preset_button.style.bgcolor = "#1976d2"
            preset_button.style.color = "white"
            content_container.content = self._create_custom_preset_content()
            self.page.update()

        api_button.on_click = switch_to_api
        preset_button.on_click = switch_to_preset

        # レイアウト
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([title, back_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([api_button, preset_button], spacing=10),
                    ft.Divider(),
                    content_container,
                ]),
                padding=40,
            )
        )

    def _create_api_settings_content(self):
        """API設定タブのコンテンツを作成"""
        config_manager = config.get_config_manager()
        current_anthropic_key = config_manager.get_anthropic_api_key() or ""
        current_openai_key = config_manager.get_openai_api_key() or ""
        current_provider = config_manager.get_ai_provider()

        # プロバイダー選択
        provider_dropdown = ft.Dropdown(
            label="AIプロバイダー",
            options=[
                ft.dropdown.Option("anthropic", "Anthropic (Claude)"),
                ft.dropdown.Option("openai", "OpenAI (GPT)"),
            ],
            value=current_provider,
            width=500,
        )

        # Anthropic APIキー入力フィールド
        anthropic_key_field = ft.TextField(
            label="Anthropic APIキー",
            hint_text="sk-ant-...",
            value=current_anthropic_key,
            password=True,
            can_reveal_password=True,
            width=500,
            border_color="#1976d2",
        )

        # OpenAI APIキー入力フィールド
        openai_key_field = ft.TextField(
            label="OpenAI APIキー",
            hint_text="sk-...",
            value=current_openai_key,
            password=True,
            can_reveal_password=True,
            width=500,
            border_color="#1976d2",
        )

        # モデル選択（プロバイダーに応じて変更）
        current_model = config_manager.get_ai_model()

        model_dropdown = ft.Dropdown(
            label="AIモデル",
            width=500,
            value=current_model,
        )

        # プロバイダー変更時の処理
        def update_model_options(update_page=True):
            if provider_dropdown.value == "anthropic":
                model_dropdown.options = [
                    ft.dropdown.Option("claude-sonnet-4-5-20250929", "Claude Sonnet 4.5（高性能・推奨）"),
                    ft.dropdown.Option("claude-haiku-4-5-20251001", "Claude Haiku 4.5（最速・最新）"),
                    ft.dropdown.Option("claude-3-5-haiku-20241022", "Claude 3.5 Haiku（旧版）"),
                    ft.dropdown.Option("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet（旧版）"),
                ]
                # デフォルトはSonnet 4.5
                valid_models = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]
                if model_dropdown.value not in valid_models:
                    model_dropdown.value = "claude-sonnet-4-5-20250929"
            else:
                model_dropdown.options = [
                    ft.dropdown.Option("gpt-5", "GPT-5（推奨）"),
                    ft.dropdown.Option("gpt-5-mini", "GPT-5 mini（高速・低コスト）"),
                    ft.dropdown.Option("gpt-4o", "GPT-4o（旧版）"),
                    ft.dropdown.Option("gpt-4o-mini", "GPT-4o mini（旧版）"),
                ]
                if model_dropdown.value not in ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"]:
                    model_dropdown.value = "gpt-5"
            if update_page:
                self.page.update()

        provider_dropdown.on_change = lambda e: update_model_options()
        update_model_options(update_page=False)  # 初期表示時はページ更新しない

        # 保存ボタン
        def save_settings(e):
            provider = provider_dropdown.value
            anthropic_key = anthropic_key_field.value
            openai_key = openai_key_field.value
            model = model_dropdown.value

            # 選択されたプロバイダーのAPIキーを確認
            if provider == "anthropic" and (not anthropic_key or not anthropic_key.strip()):
                self._show_snack_bar("Anthropic APIキーを入力してください")
                return
            elif provider == "openai" and (not openai_key or not openai_key.strip()):
                self._show_snack_bar("OpenAI APIキーを入力してください")
                return

            # 設定を保存
            if config_manager.save_api_settings(
                anthropic_api_key=anthropic_key.strip() if anthropic_key else None,
                openai_api_key=openai_key.strip() if openai_key else None,
                ai_provider=provider,
                ai_model=model
            ):
                # 設定を再読み込み
                config.reload_config()

                self._show_snack_bar("設定を保存しました")
            else:
                self._show_snack_bar("設定の保存に失敗しました")

        save_button = ft.ElevatedButton(
            "保存",
            icon="save",
            on_click=save_settings,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#1976d2",
            ),
        )

        # 設定ファイルの場所を表示
        config_location = ft.Text(
            f"設定ファイル: {config_manager.config_file}",
            size=12,
            color="#757575"
        )

        # コンテンツを返す
        return ft.Container(
            content=ft.Column([
                provider_dropdown,
                ft.Container(height=10),
                anthropic_key_field,
                ft.Container(height=10),
                openai_key_field,
                ft.Container(height=10),
                model_dropdown,
                ft.Container(height=20),
                save_button,
                ft.Container(height=20),
                config_location,
            ]),
            padding=20,
        )

    def _create_custom_preset_content(self):
        """カスタムプリセットタブのコンテンツを作成"""
        config_manager = config.get_config_manager()

        # プリセット一覧
        preset_list = ft.Column(spacing=10)

        def refresh_preset_list():
            """プリセット一覧を更新"""
            preset_list.controls.clear()
            custom_presets = config_manager.get_custom_presets()

            if not custom_presets:
                preset_list.controls.append(
                    ft.Text("カスタムプリセットがありません", color="#9e9e9e")
                )
            else:
                for key, preset_data in custom_presets.items():
                    def make_edit_handler(preset_key):
                        def handler(e):
                            self._show_preset_editor(preset_key)
                        return handler

                    def make_delete_handler(preset_key):
                        def handler(e):
                            if config_manager.delete_custom_preset(preset_key):
                                # PresetManagerを再読み込み
                                from src.presets import PresetManager
                                PresetManager.reload_custom_presets()
                                # 一覧を更新
                                refresh_preset_list()
                                self._show_snack_bar("プリセットを削除しました")
                            else:
                                self._show_snack_bar("削除に失敗しました")
                        return handler

                    preset_card = ft.Container(
                        content=ft.Row([
                            ft.Icon("edit_note", size=20, color="#1976d2"),
                            ft.Column([
                                ft.Text(preset_data.get('name', '無題'), weight=ft.FontWeight.BOLD),
                                ft.Text(preset_data.get('description', ''), size=12, color="#757575"),
                            ], expand=True, spacing=2),
                            ft.IconButton(
                                icon="edit",
                                icon_color="#1976d2",
                                tooltip="編集",
                                on_click=make_edit_handler(key)
                            ),
                            ft.IconButton(
                                icon="delete",
                                icon_color="#ef5350",
                                tooltip="削除",
                                on_click=make_delete_handler(key)
                            )
                        ]),
                        bgcolor="#e3f2fd",
                        padding=10,
                        border_radius=5,
                    )
                    preset_list.controls.append(preset_card)

            self.page.update()

        # 初期表示（初回はpage.update()を呼ばない）
        custom_presets = config_manager.get_custom_presets()
        if not custom_presets:
            preset_list.controls.append(
                ft.Text("カスタムプリセットがありません", color="#9e9e9e")
            )
        else:
            for key, preset_data in custom_presets.items():
                def make_edit_handler(preset_key):
                    def handler(e):
                        self._show_preset_editor(preset_key)
                    return handler

                def make_delete_handler(preset_key):
                    def handler(e):
                        if config_manager.delete_custom_preset(preset_key):
                            # PresetManagerを再読み込み
                            from src.presets import PresetManager
                            PresetManager.reload_custom_presets()
                            # 一覧を更新
                            refresh_preset_list()
                            self._show_snack_bar("プリセットを削除しました")
                        else:
                            self._show_snack_bar("削除に失敗しました")
                    return handler

                preset_card = ft.Container(
                    content=ft.Row([
                        ft.Icon("edit_note", size=20, color="#1976d2"),
                        ft.Column([
                            ft.Text(preset_data.get('name', '無題'), weight=ft.FontWeight.BOLD),
                            ft.Text(preset_data.get('description', ''), size=12, color="#757575"),
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            icon="edit",
                            icon_color="#1976d2",
                            tooltip="編集",
                            on_click=make_edit_handler(key)
                        ),
                        ft.IconButton(
                            icon="delete",
                            icon_color="#ef5350",
                            tooltip="削除",
                            on_click=make_delete_handler(key)
                        )
                    ]),
                    bgcolor="#e3f2fd",
                    padding=10,
                    border_radius=5,
                )
                preset_list.controls.append(preset_card)

        # 新規作成ボタン
        def create_new_preset(e):
            self._show_preset_editor(None)

        create_button = ft.ElevatedButton(
            "新規プリセット作成",
            icon="add",
            on_click=create_new_preset,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#1976d2",
            ),
        )

        return ft.Container(
            content=ft.Column([
                create_button,
                ft.Divider(),
                ft.Text("カスタムプリセット一覧", size=16, weight=ft.FontWeight.BOLD),
                preset_list,
            ]),
            padding=20,
        )

    def _show_preset_editor(self, preset_key=None):
        """プリセット編集画面を表示"""
        config_manager = config.get_config_manager()

        # 編集の場合は既存のプリセットを読み込む
        if preset_key:
            custom_presets = config_manager.get_custom_presets()
            preset_data = custom_presets.get(preset_key, {})
            title_text = "プリセットを編集"
        else:
            preset_data = {}
            title_text = "新規プリセット作成"

        self.page.clean()

        # タイトル
        title = ft.Text(
            title_text,
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#1976d2"
        )

        # 名前入力
        name_field = ft.TextField(
            label="プリセット名",
            value=preset_data.get('name', ''),
            width=500,
            border_color="#1976d2",
            autofocus=False,
        )

        # 説明入力
        description_field = ft.TextField(
            label="説明",
            value=preset_data.get('description', ''),
            width=500,
            border_color="#1976d2",
            hint_text="例: 自立支援医療申請用（200~300文字）",
            autofocus=False,
        )

        # 目標文字数入力
        target_chars_field = ft.TextField(
            label="目標文字数（表示用）",
            value=preset_data.get('target_chars', ''),
            width=500,
            border_color="#1976d2",
            hint_text="例: 200~300文字",
            autofocus=False,
        )

        # 最大トークン数入力
        max_tokens_field = ft.TextField(
            label="最大トークン数",
            value=str(preset_data.get('max_tokens', 600)),
            width=500,
            border_color="#1976d2",
            hint_text="例: 600（約200~300文字）、2048（約1000文字）",
            autofocus=False,
        )

        # プロンプト入力
        prompt_field = ft.TextField(
            label="プロンプトテンプレート",
            value=preset_data.get('prompt', ''),
            multiline=True,
            min_lines=10,
            max_lines=20,
            border_color="#1976d2",
            hint_text="「{text}」を含めることで、文書の内容が挿入されます",
            autofocus=False,
        )

        # 保存ボタン
        def save_preset(e):
            name = name_field.value
            description = description_field.value
            if not name or not name.strip():
                self._show_snack_bar("プリセット名を入力してください")
                return

            # 最大トークン数を数値に変換
            try:
                max_tokens = int(max_tokens_field.value) if max_tokens_field.value else 600
            except ValueError:
                self._show_snack_bar("最大トークン数は数値で入力してください")
                return

            # キーを生成（新規の場合）
            if not preset_key:
                import time
                new_key = f"preset_{int(time.time())}"
            else:
                new_key = preset_key

            # プリセットを保存
            success = config_manager.save_custom_preset(
                key=new_key,
                name=name.strip(),
                description=description.strip() if description else '',
                prompt=prompt_field.value or '',
                max_tokens=max_tokens,
                target_chars=target_chars_field.value or ''
            )

            if success:
                # PresetManagerを再読み込み
                from src.presets import PresetManager
                PresetManager.reload_custom_presets()

                # 設定画面（カスタムプリセットタブ）に戻る
                self._show_settings_screen(tab="preset")
                # スナックバーは設定画面が表示された後に表示
                self._show_snack_bar("プリセットを保存しました")
            else:
                self._show_snack_bar("保存に失敗しました")

        # キャンセルボタン
        def cancel_edit(e):
            self._show_settings_screen(tab="preset")

        save_button = ft.ElevatedButton(
            "保存",
            icon="save",
            on_click=save_preset,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#1976d2",
            ),
        )

        cancel_button = ft.ElevatedButton(
            "キャンセル",
            icon="cancel",
            on_click=cancel_edit,
            style=ft.ButtonStyle(
                color="#1976d2",
                bgcolor="#e3f2fd",
            ),
        )

        # レイアウト
        self.page.add(
            ft.Container(
                content=ft.Column([
                    title,
                    ft.Divider(),
                    name_field,
                    ft.Container(height=10),
                    description_field,
                    ft.Container(height=10),
                    target_chars_field,
                    ft.Container(height=10),
                    max_tokens_field,
                    ft.Container(height=10),
                    prompt_field,
                    ft.Container(height=20),
                    ft.Row([save_button, cancel_button], spacing=10),
                ], scroll=ft.ScrollMode.AUTO),
                padding=40,
            )
        )


def main(page: ft.Page):
    """メイン関数"""
    app = MedicalSummarizerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
