"""
PNG画像からマルチサイズの.icoファイルを作成するスクリプト
"""
from PIL import Image
import os

# アイコンファイルのパス
icon_folder = "iconset2"
output_icon = "icon.ico"

# 利用可能なサイズ（小さい順）
sizes = [
    (16, 16),
    (32, 32),
    (64, 64),
    (128, 128),
    (256, 256),
]

# 各サイズのPNG画像を読み込む
images = []
for size in sizes:
    width, height = size
    icon_path = os.path.join(icon_folder, f"icon_{width}x{height}.png")

    if os.path.exists(icon_path):
        print(f"読み込み: {icon_path}")
        img = Image.open(icon_path)
        images.append(img)
    else:
        print(f"警告: {icon_path} が見つかりません")

if not images:
    print("エラー: アイコン画像が見つかりませんでした")
    exit(1)

# マルチサイズのICOファイルを作成
print(f"\n作成中: {output_icon}")
images[0].save(
    output_icon,
    format='ICO',
    sizes=[(img.width, img.height) for img in images],
    append_images=images[1:]
)

print(f"✓ {output_icon} を作成しました！")
print(f"  含まれるサイズ: {', '.join([f'{img.width}x{img.height}' for img in images])}")
