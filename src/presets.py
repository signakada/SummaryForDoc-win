"""
プリセット管理モジュール
各種文書用のプリセット（プロンプトとパラメータ）を管理します
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PresetConfig:
    """プリセット設定クラス"""
    name: str  # プリセット名
    description: str  # 説明
    prompt: Optional[str] = None  # プロンプト（改行除去モードの場合はNone）
    max_tokens: int = 600  # 最大トークン数
    target_chars: str = ""  # 目標文字数（表示用）
    is_custom: bool = False  # カスタムプリセットかどうか
    is_format_only: bool = False  # 整形のみモード（AI不使用）


class PresetManager:
    """プリセット管理クラス"""

    # プリセット定義
    PRESETS: Dict[str, PresetConfig] = {}
    _custom_loaded: bool = False  # カスタムプリセットが読み込まれたか

    @classmethod
    def initialize_presets(cls):
        """プリセットを初期化"""

        # 1. 病歴欄用（200~300文字）
        cls.PRESETS['medical_history'] = PresetConfig(
            name='病歴欄用',
            description='診断書の病歴欄用（200~300文字）',
            target_chars='200~300文字',
            max_tokens=600,
            prompt="""以下は個人情報を削除した医療文書です。
診断書の「病歴」欄に記載する内容を200-300文字で作成してください。

必ず含める項目:
- 発症に至る経過
- 発症時期（いつから症状が始まったか）
- 初診時期（いつ初めて受診したか）
- 治療経過（どんな治療をしてきたか。薬剤名は不要）
- 入院歴があれば時期と期間

文体: 簡潔な医学的記述（である調）
文字数: 200-300文字厳守

【医療文書】
{text}

【出力】
診断名から始めて、時系列順に簡潔に記載してください。"""
        )

        # 2. 病状記載用（200~300文字）
        cls.PRESETS['symptom_description'] = PresetConfig(
            name='病状記載用',
            description='診断書の病状記載欄用（200~300文字）',
            target_chars='200~300文字',
            max_tokens=600,
            prompt="""以下は個人情報を削除した医療文書です。
診断書の「病状」欄に記載する内容を200-300文字で作成してください。

必ず含める項目:
- 現在の主要な症状（具体的に）
- 症状の頻度や程度
- 日常生活への影響（ADL）
- 就労能力への影響
- 必要な支援や見守りの内容

文体: 簡潔な医学的記述（である調）
文字数: 200-300文字厳守

【医療文書】
{text}

【出力】
現在の状態を中心に、具体的な影響を記載してください。"""
        )

        # 3. サマリー用（1000文字程度）
        cls.PRESETS['summary'] = PresetConfig(
            name='サマリー用',
            description='詳細なサマリー（1000文字程度）',
            target_chars='1000文字程度',
            max_tokens=2048,
            prompt="""以下は個人情報を削除した医療文書です。
全期間の経過を詳しくまとめてください。

以下の構成で記載:
1. 診断名
2. 発症と初診の経緯
3. 治療経過（時系列で詳細に）
   - 薬物療法の内容と変更
   - 入院治療があれば詳細
   - 検査結果
4. 現在の状態
   - 症状
   - 日常生活状況
   - 就労状況
5. 今後の治療方針

文体: 詳細な医学的記述
文字数: 1000文字程度

【医療文書】
{text}

【出力】
見出しをつけて、時系列順に詳しく記載してください。"""
        )

        # 4. 介護保険意見書用（200~300文字）
        cls.PRESETS['care_insurance'] = PresetConfig(
            name='介護保険意見書用',
            description='介護保険主治医意見書用（200~300文字）',
            target_chars='200~300文字',
            max_tokens=600,
            prompt="""以下は個人情報を削除した医療文書です。
介護保険主治医意見書に記載する内容を200-300文字で作成してください。

必ず含める項目:
- 診断名と発症時期
- 現在の症状と障害の程度
- 認知機能や身体機能の状態
- 日常生活動作（ADL）への影響
- 介護の必要性とその理由
- 見守りや支援が必要な具体的な内容

文体: 簡潔な医学的記述（である調）
文字数: 200-300文字厳守

【医療文書】
{text}

【出力】
介護の必要性を中心に、具体的な状態を記載してください。"""
        )

        # 5. 診療情報提供書の整形（改行除去のみ）
        cls.PRESETS['format_only'] = PresetConfig(
            name='診療情報提供書の整形',
            description='不要な改行を取り除くのみ（AI不使用）',
            target_chars='—',
            is_format_only=True,
        )

    @classmethod
    def get_preset(cls, preset_key: str) -> PresetConfig:
        """
        プリセットを取得

        Args:
            preset_key: プリセットのキー

        Returns:
            PresetConfig: プリセット

        Raises:
            KeyError: 存在しないキー
        """
        if not cls.PRESETS:
            cls.initialize_presets()

        if preset_key not in cls.PRESETS:
            raise KeyError(
                f"プリセット '{preset_key}' が見つかりません。\n"
                f"利用可能なプリセット: {list(cls.PRESETS.keys())}"
            )

        return cls.PRESETS[preset_key]

    @classmethod
    def load_custom_presets(cls):
        """カスタムプリセットを読み込む"""
        from .config import config

        config_manager = config.get_config_manager()
        custom_presets = config_manager.get_custom_presets()

        for key, preset_data in custom_presets.items():
            # カスタムプリセットのキーには "custom_" プレフィックスを付ける
            custom_key = f"custom_{key}"
            cls.PRESETS[custom_key] = PresetConfig(
                name=preset_data.get('name', 'カスタムプリセット'),
                description=preset_data.get('description', 'カスタムプリセット'),
                prompt=preset_data.get('prompt', ''),
                max_tokens=preset_data.get('max_tokens', 600),
                target_chars=preset_data.get('target_chars', ''),
                is_custom=True
            )

        cls._custom_loaded = True

    @classmethod
    def get_all_presets(cls) -> Dict[str, PresetConfig]:
        """すべてのプリセットを取得（カスタムプリセットを含む）"""
        if not cls.PRESETS:
            cls.initialize_presets()

        # カスタムプリセットをまだ読み込んでいない場合は読み込む
        if not cls._custom_loaded:
            cls.load_custom_presets()

        return cls.PRESETS

    @classmethod
    def reload_custom_presets(cls):
        """カスタムプリセットを再読み込み"""
        # 既存のカスタムプリセットを削除
        cls.PRESETS = {k: v for k, v in cls.PRESETS.items() if not v.is_custom}
        cls._custom_loaded = False
        # 再読み込み
        cls.load_custom_presets()

    @classmethod
    def format_prompt(cls, prompt_template: str, text: str) -> str:
        """
        プロンプトに医療文書を埋め込む

        Args:
            prompt_template: プロンプトテンプレート
            text: 医療文書

        Returns:
            str: 完成したプロンプト
        """
        return prompt_template.format(text=text)

    @classmethod
    def format_text_only(cls, text: str) -> str:
        """
        テキストの整形のみ（不要な改行を削除）

        Args:
            text: 元のテキスト

        Returns:
            str: 整形されたテキスト
        """
        import re

        # 連続する空白行を1つにする
        text = re.sub(r'\n\n+', '\n\n', text)

        # 段落内の改行を削除（ただし、箇条書きや見出しは保持）
        lines = text.split('\n')
        formatted_lines = []
        current_paragraph = []

        for line in lines:
            line = line.strip()

            # 空行の場合
            if not line:
                if current_paragraph:
                    formatted_lines.append(''.join(current_paragraph))
                    current_paragraph = []
                formatted_lines.append('')
                continue

            # 箇条書きや見出しっぽい行（短い行、記号で始まる行など）
            if (len(line) < 30 or
                line.startswith(('・', '○', '●', '※', '■', '□', '【', '1.', '2.', '3.', '-', '*')) or
                line.endswith(('：', ':'))):
                if current_paragraph:
                    formatted_lines.append(''.join(current_paragraph))
                    current_paragraph = []
                formatted_lines.append(line)
                continue

            # 通常の文章行は結合
            current_paragraph.append(line)

        # 最後の段落を追加
        if current_paragraph:
            formatted_lines.append(''.join(current_paragraph))

        return '\n'.join(formatted_lines)


# 初期化
PresetManager.initialize_presets()


if __name__ == "__main__":
    # テスト用
    print("=== 利用可能なプリセット ===")
    for key, preset in PresetManager.get_all_presets().items():
        print(f"\n[{key}]")
        print(f"名前: {preset.name}")
        print(f"説明: {preset.description}")
        print(f"目標文字数: {preset.target_chars}")
        print(f"整形のみモード: {preset.is_format_only}")

    print("\n\n=== プリセット使用例 ===")
    preset = PresetManager.get_preset('medical_history')
    sample_text = "統合失調症。2020年4月頃より幻聴が出現..."

    if not preset.is_format_only:
        print("\n--- プロンプト ---")
        print(PresetManager.format_prompt(preset.prompt, sample_text))

    print("\n\n=== テキスト整形例 ===")
    sample_text_with_newlines = """診断名：統合失調症

【経過】
2020年4月頃より幻聴（命令性）
と被害念慮が出現。当初は自宅で
様子観察していたが症状が悪化し、
同年6月15日に当院初診となった。

初診時所見：
・幻聴あり
・被害妄想あり
"""
    print(PresetManager.format_text_only(sample_text_with_newlines))
