# app.py (수정 버전)
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from font_processor import FontStyleProcessor
import os, uuid

app = Flask(__name__)
app.secret_key = 'hai-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 세션별 스타일 목록
session_fonts = {}

# ✅ 서버 시작 시 Styleimg 추론 (한 번만 실행)
DEFAULT_STYLE_ID = 'Styleimg'
DEFAULT_STYLE_PATH = 'style/styleimg.pdf'
DEFAULT_STYLE_OUTPUT = f'static/outputs/{DEFAULT_STYLE_ID}'

if not os.path.exists(DEFAULT_STYLE_OUTPUT) or not os.listdir(DEFAULT_STYLE_OUTPUT):
    print("기본 손글씨 스타일 추론 중...")
    processor = FontStyleProcessor(DEFAULT_STYLE_PATH)
    processor.run_all('가')  # 초기용 문자

@app.before_request
def load_session_fonts():
    session_id = session.get('id')
    if not session_id:
        session['id'] = str(uuid.uuid4())
        session_id = session['id']
        session_fonts[session_id] = [DEFAULT_STYLE_ID]
    if session_id not in session_fonts:
        session_fonts[session_id] = [DEFAULT_STYLE_ID]

@app.route('/')
def index():
    session_id = session['id']
    examples = [{'id': fid, 'image': f'{fid}/sample.png'} for fid in session_fonts[session_id]]
    selected_style = session_fonts[session_id][0]  # ✅ 기본 선택
    return render_template('index.html', examples=examples, selected_style=selected_style)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'PDF 파일만 업로드 가능합니다.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    style_id = os.path.splitext(filename)[0]
    processor = FontStyleProcessor(filepath)
    processor.run_all('가')

    session_fonts[session['id']].append(style_id)
    return jsonify({'status': 'success'})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text')
    style_id = data.get('style_id')
    if not text or not style_id:
        return jsonify({'error': '문구 또는 스타일이 없습니다.'}), 400

    pdf_path = DEFAULT_STYLE_PATH if style_id == DEFAULT_STYLE_ID else f'uploads/{style_id}.pdf'
    processor = FontStyleProcessor(pdf_path)
    processor.generate_yaml(text)
    processor.run_inference()

    image_files = [
        f"/static/outputs/{style_id}/{f}"
        for f in os.listdir(f'static/outputs/{style_id}') if f.endswith('.png')
    ]
    return jsonify({'images': image_files})
