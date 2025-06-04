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

    # 기존 메서드 생략...

    def generate_sample_image(self):
        sample_text = '가'
        self.generate_yaml(sample_text)
        self.run_inference()
        output_images = [f for f in os.listdir(self.save_dir) if f.endswith('.png')]
        sentence_img = os.path.join(self.save_dir, 'sentence.png')
        if output_images and os.path.exists(sentence_img):
            sample_image_path = os.path.join(self.save_dir, 'sample.png')
            Image.open(sentence_img).save(sample_image_path)
            print(f"[SAVE] Sample image saved to {sample_image_path}")
        else:
            print("[WARN] Sample image 생성 실패 - sentence.png 또는 이미지 없음")

    def run_all(self, target_chars):
        self.convert_pdf_to_images()
        self.trim_and_save_images()
        self.clean_images()
        self.generate_yaml(target_chars)
        self.run_inference()
        # 기본 sample.png 생성 추가
        self.generate_sample_image()
