from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from font_processor import FontStyleProcessor
import os
import uuid
import random

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'hai-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
session_fonts = {}

DEFAULT_STYLE_ID = 'Styleimg'
DEFAULT_STYLE_PATH = 'style/Styleimg.pdf'
DEFAULT_STYLE_OUTPUT = f'static/outputs/{DEFAULT_STYLE_ID}'

def should_generate_default():
    if not os.path.exists(DEFAULT_STYLE_OUTPUT):
        return True
    pngs = [f for f in os.listdir(DEFAULT_STYLE_OUTPUT) if f.endswith('.png')]
    return len(pngs) == 0

if should_generate_default():
    print("기본 손글씨 스타일 추론 중...")
    processor = FontStyleProcessor(DEFAULT_STYLE_PATH)
    processor.run_all('가')


@app.before_request
def load_session_fonts():
    session_id = session.get('id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['id'] = session_id
    if session_id not in session_fonts:
        session_fonts[session_id] = [DEFAULT_STYLE_ID]

@app.route('/')
def index():
    session_id = session['id']
    examples = [{'id': fid, 'image': f'{fid}/sample.png'} for fid in session_fonts[session_id]]
    selected_style = session_fonts[session_id][0]
    rand_num = random.random()
    return render_template('index.html', examples=examples, selected_style=selected_style, rand_num=rand_num)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'PDF 파일만 업로드 가능합니다.'}), 400

    filename = secure_filename(file.filename)
    style_id = os.path.splitext(filename)[0]

    if style_id == DEFAULT_STYLE_ID:
        return jsonify({'error': '기본 스타일 이름(Styleimg)으로는 업로드할 수 없습니다.'}), 400

    session_id = session['id']
    if style_id in session_fonts.get(session_id, []):
        return jsonify({'error': '이미 등록된 스타일입니다.'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    processor = FontStyleProcessor(filepath)
    processor.run_all('가')

    session_fonts[session_id].append(style_id)

    # 업로드 후 클라이언트에 새 예시 HTML 반환 (sample.png 포함)
    example_html = f'''
    <div onclick="selectTemplate('{style_id}')" class="cursor-pointer hover:scale-105 transition">
        <img src="/static/outputs/{style_id}/sample.png?t={uuid.uuid4().hex}" alt="예시"
            class="rounded-lg shadow border-2 border-transparent hover:border-blue-400" />
        <p class="text-center text-sm mt-1">예시 {len(session_fonts[session_id])}</p>
    </div>
    '''

    return jsonify({'status': 'success', 'example_html': example_html})


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

    output_dir = f'static/outputs/{style_id}'
    image_files = [
        f"/static/outputs/{style_id}/{f}?t={uuid.uuid4().hex}"
        for f in os.listdir(output_dir) if f.endswith('.png')
    ]
    return jsonify({'images': image_files})

@app.route('/download-template')
def download_template():
    return send_from_directory(directory='.', path='28_template.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
