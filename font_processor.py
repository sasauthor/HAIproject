import os
import yaml
import numpy as np
from PIL import Image, ImageChops
from pdf2image import convert_from_path
import subprocess
from inference import main as inference_main

class FontStyleProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        self.output_dir = f"style/{self.base_name}"
        self.cropped_dir = os.path.join(self.output_dir, "cropped")
        self.cleaned_dir = os.path.join(self.output_dir, "cleaned")
        self.yaml_path = f"configs/{self.base_name}.yaml"
        self.checkpoint = "checkpoints/korean-handwriting.pth"
        self.save_dir = f"static/outputs/{self.base_name}"
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_pdf_to_images(self):
        images = convert_from_path(self.pdf_path, dpi=300)
        for i, img in enumerate(images):
            fname = f"{self.output_dir}/{self.base_name}_p{i+1}.png" if len(images) > 1 else f"{self.output_dir}/{self.base_name}.png"
            img.save(fname, dpi=(300, 300))  
            print(f"[SAVE] {fname}")

    def trim_and_save_images(self):
        def trim_whitespace(path):
            img = Image.open(path)
            bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
            diff = ImageChops.difference(img, bg)
            bbox = diff.getbbox()
            if bbox:
                img = img.crop(bbox)
                img.save(path)

        for fname in os.listdir(self.output_dir):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                trim_whitespace(os.path.join(self.output_dir, fname))

        try:
            subprocess.run([
                "python", "style/crop.py",
                f"--src_dir={self.output_dir}",
                f"--dst_dir={self.cropped_dir}"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] crop.py 실행 실패: {e}")

    def clean_images(self):
        os.makedirs(self.cleaned_dir, exist_ok=True)
        for fname in os.listdir(self.cropped_dir):
            if fname.endswith(".png"):
                img = Image.open(os.path.join(self.cropped_dir, fname)).convert("L")
                img_np = np.array(img)
                img_bin = np.where(img_np > 200, 255, 0).astype(np.uint8)
                img_cleaned = Image.fromarray(img_bin).resize((128, 128), Image.Resampling.LANCZOS)
                img_cleaned.save(os.path.join(self.cleaned_dir, fname))

    def generate_yaml(self, target_chars):
        style_imgs = [os.path.join(self.cleaned_dir, f) for f in sorted(os.listdir(self.cleaned_dir)) if f.endswith(".png")]
        style_chars = list("각깪냓댼떥렎멷볠뽉솲쐛욄죭쭖춣퀨튑퓺흣읬잉잊잋잌잍잎잏이")
        cfg = {
            'style_imgs': style_imgs,
            'style_chars': style_chars,
            'charset_path': 'data/charset/korean11172.txt',
            'output_dir': self.save_dir,
            'checkpoint': self.checkpoint,
            'num_font_samples': 1,
            'target_chars': target_chars,
            'C': 32,
            'n_comps': 68,
            'n_comp_types': 3,
            'language': 'kor'
        }
        os.makedirs(os.path.dirname(self.yaml_path), exist_ok=True)
        with open(self.yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(cfg, f, allow_unicode=True)

    def run_inference(self):
        inference_main(self.yaml_path)

    def run_all(self, test_char):
        print(f"[PROCESS] {self.pdf_path}")
        self.convert_pdf_to_images()
        self.trim_and_save_images()
        self.clean_images()
        self.generate_yaml(test_char)
        self.run_inference()

    def generate_sample_image(self):
        sample_src = f"{self.output_dir}/sample.png"
        sample_dst = f"{self.save_dir}/sample.png"
        if os.path.exists(sample_src):
            os.makedirs(self.save_dir, exist_ok=True)
            import shutil
            shutil.copyfile(sample_src, sample_dst)
            print("[INFO] sample.png copied")
        else:
            print("[WARN] sample.png 없음")
