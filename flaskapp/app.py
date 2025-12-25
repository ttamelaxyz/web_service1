import os
from flask import Flask, render_template, request, send_file, url_for, session
from werkzeug.utils import secure_filename
from image_processor import split_image_into_four, generate_color_histograms
import uuid
import shutil

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-123")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PLOTS_FOLDER'] = 'static/plots'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_old_sessions():
    # Очистка старых сессий для предотвращения утечек памяти
    session_folder = session.get('session_id')
    if session_folder:
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], session_folder)
        plots_path = os.path.join(app.config['PLOTS_FOLDER'], session_folder)
        for path in [upload_path, plots_path]:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    if request.method == 'POST':
        clear_old_sessions()
        
        if 'file' not in request.files:
            return render_template('index.html', error="No file selected")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if file and allowed_file(file.filename):
            session_id = session['session_id']
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
            plots_dir = os.path.join(app.config['PLOTS_FOLDER'], session_id)
            
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(plots_dir, exist_ok=True)
            
            # Сохраняем оригинальное изображение
            original_filename = secure_filename(file.filename)
            original_path = os.path.join(upload_dir, 'original.jpg')
            file.save(original_path)
            
            # Обрабатываем изображение
            parts = split_image_into_four(original_path, upload_dir)
            histograms = generate_color_histograms(original_path, parts, plots_dir)
            
            # Генерируем URL для отображения
            image_urls = {
                'original': url_for('static', filename=f'uploads/{session_id}/original.jpg'),
                'parts': [url_for('static', filename=f'uploads/{session_id}/{p}') for p in parts],
                'histograms': [url_for('static', filename=f'plots/{session_id}/{h}') for h in histograms]
            }
            
            return render_template('index.html', 
                                 image_urls=image_urls,
                                 success="Image processed successfully")
    
    return render_template('index.html')

@app.route('/clear', methods=['POST'])
def clear_session():
    clear_old_sessions()
    session.pop('session_id', None)
    return {'status': 'cleared'}

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PLOTS_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)