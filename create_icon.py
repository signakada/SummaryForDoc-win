"""
PNG画像からマルチサイズの.icoファイルを作成するスクリプト（Windows最適化版）
"""
from PIL import Image
import os

# アイコンファイルのパス
icon_folder = "iconset2"
output_icon = "icon.ico"

# Windows用に最適化されたサイズ（ICOファイルとして重要な順）
# 256以上のサイズは含めない（Windows Vistaまでの互換性とファイルサイズのバランス）
windows_sizes = [
    256,  # Windows Vista以降の特大アイコン（最重要）
    128,  # 大アイコン
    64,   # 中アイコン
    48,   # 標準アイコン
    32,   # 小アイコン
    24,   # タスクバー用
    16,   # 最小アイコン
]

print(f"Windows最適化ICOファイル作成ツール")
print(f"="*50)

# 最大サイズの画像を読み込む（1024か512を基準にする）
base_image = None
for size in [1024, 512, 256]:
    base_path = os.path.join(icon_folder, f"icon_{size}x{size}.png")
    if os.path.exists(base_path):
        print(f"ベース画像を読み込み: {base_path}")
        base_image = Image.open(base_path)
        break

if base_image is None:
    print("エラー: ベースとなる大きなアイコン画像が見つかりませんでした")
    print(f"必要なファイル: {icon_folder}/icon_256x256.png 以上")
    exit(1)

# RGBAモードに変換（アルファチャンネルを確保）
if base_image.mode != 'RGBA':
    print(f"RGBAモードに変換: {base_image.mode} -> RGBA")
    base_image = base_image.convert('RGBA')

# 各サイズの画像を生成
print(f"\n各サイズの画像を生成中...")
resized_images = []

for size in windows_sizes:
    target_size = (size, size)

    # 対応するPNGファイルが存在する場合はそれを使用
    icon_path = os.path.join(icon_folder, f"icon_{size}x{size}.png")

    if os.path.exists(icon_path) and size <= 256:
        print(f"  {size}x{size}: 既存ファイルを使用 ({icon_path})")
        img = Image.open(icon_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
    else:
        # 高品質リサンプリングで生成
        print(f"  {size}x{size}: リサンプリング生成 (LANCZOS)")
        img = base_image.resize(target_size, Image.Resampling.LANCZOS)

    resized_images.append(img)

# マルチサイズのICOファイルを作成
print(f"\nICOファイルを作成中: {output_icon}")

# 最初の画像を基準に、残りを append_images として追加
resized_images[0].save(
    output_icon,
    format='ICO',
    sizes=[(img.width, img.height) for img in resized_images],
    append_images=resized_images[1:] if len(resized_images) > 1 else []
)

print(f"\n[OK] {output_icon} の作成に成功しました！")
print(f"  含まれるサイズ: {', '.join([f'{size}x{size}' for size in windows_sizes])}")
print(f"  ファイルサイズ: {os.path.getsize(output_icon) / 1024:.1f} KB")
print(f"\nヒント: PyInstallerでビルドする際は、必ずクリーンビルドしてください:")
print(f"  1. dist/ と build/ フォルダを削除")
print(f"  2. pyinstaller SummaryForDoc.spec でビルド")
