"""
DMFont
Copyright (c) 2020-present NAVER Corp.
MIT license
"""
import torch
from torch.utils.data import DataLoader
from datasets import get_ma_val_dataset
from datasets.nonpaired_dataset import EncodeDataset, DecodeDataset
import os




def get_val_loader(data, fonts, chars, style_avails, transform, content_font, language,
                   B=32, n_max_match=3, n_workers=2):
    val_dset, collate_fn = get_ma_val_dataset(
        data, fonts, chars, style_avails, n_max_match, transform=transform,
        content_font=content_font, language=language
    )
    loader = DataLoader(val_dset, batch_size=B, shuffle=False,
                        num_workers=n_workers, collate_fn=collate_fn)

    return loader


def infer_2stage(gen, encode_loader, decode_loader, reset_memory=True):
    """ 2-stage infer; encode first, decode second """
    # stage 1. encode
    if reset_memory:
        gen.reset_dynamic_memory()

    for style_ids, style_comp_ids, style_imgs in encode_loader:
        style_ids = style_ids.to("cpu")
        style_comp_ids = style_comp_ids.to("cpu")
        style_imgs = style_imgs.to("cpu")

        gen.encode_write(style_ids, style_comp_ids, style_imgs, reset_dynamic_memory=False)

    # stage 2. decode
    outs = []
    for trg_ids, trg_comp_ids in decode_loader:
        trg_ids = trg_ids.to("cpu")
        trg_comp_ids = trg_comp_ids.to("cpu")
        # print("🧠 target_style_ids:", style_ids)


        out = gen.read_decode(trg_ids, trg_comp_ids)

        outs.append(out.detach().cpu())

    return torch.cat(outs)


def get_val_decode_loader(chars, language, B=32, num_workers=2, style_id=0):
    decode_dset = DecodeDataset(chars, language=language, style_id=style_id)
    loader = DataLoader(decode_dset, batch_size=B, shuffle=False, num_workers=num_workers)

    return loader



###추가
from datasets.style_image_dataset import StyleImageDataset  # 직접 만든 Dataset일 수도 있음
from torch.utils.data import DataLoader

def get_styleimg_encode_loader(style_imgs, style_chars, language, transform, style_id=0, B=32, num_workers=2):
    dset = StyleImageDataset(style_imgs, style_chars, language=language, transform=transform, style_id=style_id)
    return DataLoader(dset, batch_size=B, shuffle=False, num_workers=num_workers)



from torchvision import transforms

def get_transform():
    return transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])

#수정후
from PIL import Image
import numpy as np
import torch
import os

def save_sentence_image(
    imgs, path, text=None, target_height=128,
    max_side_crop1=25, max_side_crop2=25,
    overlap_margin=0, space_margin=30, line_spacing=20
):
    imgs = imgs.squeeze(1)  # [N, 1, H, W] → [N, H, W]
    imgs = imgs.mul(0.5).add(0.5).clamp(0, 1)  # [-1,1] → [0,1]
    imgs = imgs.mul(255).byte().cpu().numpy()  # [0,255]

    # 문자 이미지 전처리
    char_imgs = []
    for img in imgs:
        pil_img = Image.fromarray(img, mode='L')
        arr = np.array(pil_img)

        col_sum = np.mean(arr, axis=0)
        non_white = np.where(col_sum < 245)[0]
        if len(non_white) > 0:
            x0 = max(non_white[0] - max_side_crop1, 0)
            x1 = min(non_white[-1] + max_side_crop2 + 1, arr.shape[1])
            cropped = pil_img.crop((x0, 0, x1, arr.shape[0]))
        else:
            cropped = pil_img

        # 높이 맞춤
        W, H = cropped.size
        if H < target_height:
            top_pad = (target_height - H) // 2
            padded = Image.new('L', (W, target_height), 255)
            padded.paste(cropped, (0, top_pad))
        else:
            padded = cropped.resize((W, target_height), Image.Resampling.LANCZOS)

        char_imgs.append(padded)

    # 총 이미지 크기 계산
    max_line_width = 0
    line_width = 0
    img_idx = 0
    line_count = 1
    for c in text:
        if c == '\\n':
            max_line_width = max(max_line_width, line_width)
            line_width = 0
            line_count += 1
        elif c == ' ':
            line_width += space_margin
        else:
            if img_idx < len(char_imgs):
                line_width += char_imgs[img_idx].size[0]
                if line_width > 0:
                    line_width -= overlap_margin
                img_idx += 1
    max_line_width = max(max_line_width, line_width)
    total_height = line_count * target_height + (line_count - 1) * line_spacing

    # 이미지 생성 및 붙이기
    final_img = Image.new('L', (max_line_width, total_height), 255)
    x_offset = 0
    y_offset = 0
    img_idx = 0

    for c in text:
        if c == '\\n':
            y_offset += target_height + line_spacing
            x_offset = 0
        elif c == ' ':
            x_offset += space_margin
        else:
            if img_idx >= len(char_imgs):
                break
            im = char_imgs[img_idx]
            final_img.paste(im, (x_offset, y_offset))
            x_offset += im.size[0] - overlap_margin
            img_idx += 1

    os.makedirs(os.path.dirname(path), exist_ok=True)
    final_img.save(path)


def main(config, checkpoint, save_dir):
    import os
    import torch
    import yaml
    with open(config, 'r') as f:
      cfg = yaml.safe_load(f)
    from models.comp_encoder import ComponentEncoder
    from models.decoder import Decoder
    from models.ma_core import MACore
    # from datasets.transforms import get_transform
    # from utils.misc import save_imgs
    from inference import infer_2stage, get_val_decode_loader

    os.makedirs(save_dir, exist_ok=True)
    device = torch.device("cpu")

    with open(config, 'r') as f:
      cfg = yaml.safe_load(f)


    # style-aware feed-forward block 설정
    sa = {'n_heads': 4}  # Clova 기본 세팅


    # 최종 Generator 생성
    gen = MACore(
        C_in=1,
        C=32,              # ← from config
        C_out=1,
        comp_enc={
            'norm': 'none',
            'activ': 'relu',
            'pad_type': 'zero',
            'sa': {
                'C_qk_ratio': 0.5,
                'n_heads': 2,
                'area': False,
                'ffn_mult': 2
            }
        },
        dec={
            'norm': 'IN',
            'activ': 'relu',
            'pad_type': 'zero'
        },
        n_comps=68,
        n_comp_types=3,
        language='kor'
    ).to(device)




    # 사전학습된 파라미터 로드
    ckpt = torch.load(checkpoint, map_location="cpu")
    gen.load_state_dict(ckpt["generator_ema"])  # ✅ 이거로!

    gen.eval()

    # 인코딩 및 디코딩용 데이터로더
    from inference import get_styleimg_encode_loader  # 위에서 만든 함수

    encode_loader = get_styleimg_encode_loader(
      cfg['style_imgs'], cfg['style_chars'], cfg['language'],
      transform=get_transform(), style_id=0
    )
    import re
    valid_target_chars = [c for c in cfg['target_chars'] if re.match(r'[가-힣]', c)]
    decode_loader = get_val_decode_loader(valid_target_chars, cfg['language'], style_id=0)
    text = ''.join(cfg['target_chars'])  # 출력용 문장은 그대로 유지


    # 추론 실행
    with torch.no_grad():
        outs = infer_2stage(gen, encode_loader, decode_loader)

    # save_sentence_image_with_padding(outs, os.path.join(save_dir, "sentence.png"))
    save_sentence_image(outs, os.path.join(save_dir, "sentence.png"), text=text, overlap_margin=0, space_margin=50)



if __name__ == '__main__':
    import fire
    fire.Fire(main)
