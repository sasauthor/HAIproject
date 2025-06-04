import os
from PIL import Image, ImageChops, ImageOps
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--src_dir", required=True)
parser.add_argument("--dst_dir", required=True)
args = parser.parse_args()

# 각 템플릿별 행, 열
layout = {
    "Styleimg.png": (4, 7)
}

pad = 20
os.makedirs(args.dst_dir, exist_ok=True)

start_unicode = 0xAC00
count = 0

skip_indices = {
    "Styleimg.png": set()  # 건너뛸 칸이 없으면 빈 set()
}

for fname in sorted(os.listdir(args.src_dir)):
    if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    if fname not in layout:
        print(f"danger {fname}no information for layout, jumped")
        continue

    rows, cols = layout[fname]
    skip_set = skip_indices.get(fname, set())

    img_path = os.path.join(args.src_dir, fname)
    img = Image.open(img_path).convert("L")

    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows

    index = 1  # 1부터 시작

    for r in range(rows):
        for c in range(cols):
            if index in skip_set:
                print(f"{fname} - {index} jumped")
                index += 1
                continue

            left = c * cell_w + pad
            upper = r * cell_h + pad + 40
            right = (c + 1) * cell_w - pad
            lower = (r + 1) * cell_h - pad
            cropped = img.crop((left, upper, right, lower))

            bg = Image.new("L", cropped.size, 255)
            diff = ImageChops.difference(cropped, bg)
            bbox = diff.getbbox()

            if bbox:
                cropped = cropped.crop(bbox)

            padding = 30
            cropped = ImageOps.expand(cropped, border=padding, fill=255)

            # 정사각형 배경 만들고 중앙 배치
            max_side = max(cropped.size)
            square = Image.new("L", (max_side, max_side), 255)
            offset = ((max_side - cropped.width) // 2, (max_side - cropped.height) // 2)
            square.paste(cropped, offset)
            cropped = square

            # 최종 리사이즈
            cropped = cropped.resize((512, 512), Image.BICUBIC)

            fname_out = f"uni{start_unicode + count:04X}.png"
            cropped.save(os.path.join(args.dst_dir, fname_out))
            count += 1
            index += 1

print(f"complete {count} chars are saved: {args.dst_dir}")
