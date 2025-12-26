import os
import sys
from flask import Flask, render_template, request, url_for, session
from werkzeug.utils import secure_filename
import uuid
import shutil
import threading
import time

# Добавляем путь к текущей папке
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from image_processor import split_image_into_four, generate_color_histograms

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "web-service-secret-key-2003")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Пути относительно папки flaskapp
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['PLOTS_FOLDER'] = os.path.join(BASE_DIR, 'static', 'plots')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_sessions():
    """Очищает файлы сессий старше 1 часа"""
    while True:
        time.sleep(3600)
        try:
            for folder_type in ['uploads', 'plots']:
                base_path = os.path.join(BASE_DIR, 'static', folder_type)
                if not os.path.exists(base_path):
                    continue
                    
                for session_folder in os.listdir(base_path):
                    session_path = os.path.join(base_path, session_folder)
                    if os.path.isdir(session_path):
                        try:
                            mod_time = os.path.getmtime(session_path)
                            if time.time() - mod_time > 3600:
                                shutil.rmtree(session_path, ignore_errors=True)
                        except:
                            continue
        except Exception as e:
            print(f"Cleanup error: {e}")

def clear_current_session():
    """Очищает файлы текущей сессии"""
    session_id = session.get('session_id')
    if session_id:
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        plots_path = os.path.join(app.config['PLOTS_FOLDER'], session_id)
        
        for path in [upload_path, plots_path]:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except:
                    pass
        
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(plots_path, exist_ok=True)

@app.before_request
def before_request():
    """Инициализация сессии перед каждым запросом"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    plots_dir = os.path.join(app.config['PLOTS_FOLDER'], session_id)
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file selected")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if file and allowed_file(file.filename):
            clear_current_session()
            
            session_id = session['session_id']
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
            plots_dir = os.path.join(app.config['PLOTS_FOLDER'], session_id)
            
            original_filename = secure_filename(file.filename)
            original_path = os.path.join(upload_dir, 'original.jpg')
            
            try:
                file.save(original_path)
                
                parts = split_image_into_four(original_path, upload_dir)
                
                if not parts:
                    return render_template('index.html', error="Failed to split image")
                
                histograms = generate_color_histograms(original_path, parts, plots_dir)
                
                if not histograms:
                    return render_template('index.html', error="Failed to generate histograms")
                
                # Генерируем URL с учетом папки flaskapp
                image_urls = {
                    'original': url_for('static', filename=f'uploads/{session_id}/original.jpg'),
                    'parts': [url_for('static', filename=f'uploads/{session_id}/{p}') for p in parts],
                    'histograms': [url_for('static', filename=f'plots/{session_id}/{h}') for h in histograms]
                }
                
                return render_template('index.html', 
                                     image_urls=image_urls,
                                     success="Image processed successfully")
                
            except Exception as e:
                print(f"Error: {e}")
                return render_template('index.html', error=f"Error: {str(e)}")
        else:
            return render_template('index.html', error="Invalid file type")
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PLOTS_FOLDER'], exist_ok=True)
    
    cleanup_thread = threading.Thread(target=cleanup_old_sessions, daemon=True)
    cleanup_thread.start()
    
    app.run(debug=False, host='0.0.0.0', port=5000)