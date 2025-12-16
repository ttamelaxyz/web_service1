from flask import Flask, render_template, request, send_file, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from wtforms.validators import DataRequired
import os
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import io
import base64
from image_processor import split_image_into_four, get_color_distribution

app = Flask(__name__)
SECRET_KEY = "qwerty"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Создаем папку для загрузок если её нет
#os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

Bootstrap(app)

# Форма для загрузки изображения
class ImageUploadForm(FlaskForm):
    image = FileField('Выберите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp'], 'Только изображения!')
    ])
    submit = SubmitField('Обработать')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return render_template('result.html', 
                             filename=filename,
                             original_image=filepath)
    
    return render_template('index.html', form=form)

@app.route('/process/<filename>')
def process_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        #разбиваем изображение на 4 части
        parts = split_image_into_four(filepath)
        
        #распределения цветов для каждой части
        distributions = []
        for i, part in enumerate(parts):
            dist = get_color_distribution(part)
            distributions.append(dist)
            
            #сохраняем каждую часть
            part_filename = f"{filename.split('.')[0]}_part{i+1}.png"
            part_path = os.path.join(app.config['UPLOAD_FOLDER'], part_filename)
            part.save(part_path, 'PNG')
        
        #графики распределения цветов
        plot_urls = []
        for i, dist in enumerate(distributions):
            plot_url = create_color_distribution_plot(dist, f"Часть {i+1}")
            plot_urls.append(plot_url)
        
        #график для исходного изображения
        original_dist = get_color_distribution(Image.open(filepath))
        original_plot = create_color_distribution_plot(original_dist, "Исходное изображение")
        
        return render_template('result.html',
                             filename=filename,
                             original_image=filepath,
                             parts=parts,
                             distributions=distributions,
                             plot_urls=plot_urls,
                             original_plot=original_plot)
        
    except Exception as e:
        return f"Ошибка обработки изображения: {str(e)}", 500

def create_color_distribution_plot(distribution, title):
    """Создает график распределения цветов и возвращает base64 строку"""
    colors = ['Red', 'Green', 'Blue']
    values = [distribution['red'], distribution['green'], distribution['blue']]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(colors, values, color=['red', 'green', 'blue'])
    plt.title(f'Распределение цветов - {title}', fontsize=16)
    plt.ylabel('Интенсивность', fontsize=12)
    plt.xlabel('Цветовой канал', fontsize=12)
    plt.ylim(0, 1)
    
    #значения на столбцы
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    #сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    
    #конвертируем в base64
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

@app.route('/download/<part>/<filename>')
def download_part(part, filename):
    part_filename = f"{filename.split('.')[0]}_part{part}.png"
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], part_filename),
        as_attachment=True,
        download_name=part_filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
