import numpy as np
import matplotlib
# Используем неинтерактивный бэкэнд для Matplotlib
matplotlib.use('Agg')  # Важно: должен быть ДО импорта pyplot
import matplotlib.pyplot as plt
import os
from PIL import Image

def split_image_into_four(image_path, output_dir):
    """
    Разбивает изображение на 4 равные части с использованием PIL
    """
    img = Image.open(image_path)
    if img is None:
        raise ValueError("Cannot read image")
    
    # Конвертируем в RGB если нужно
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    w_mid = width // 2
    h_mid = height // 2
    
    parts = []
    part_names = []
    
    # Координаты частей
    coordinates = [
        (0, w_mid, 0, h_mid),       # Верхняя левая
        (w_mid, width, 0, h_mid),   # Верхняя правая
        (0, w_mid, h_mid, height),  # Нижняя левая
        (w_mid, width, h_mid, height) # Нижняя правая
    ]
    
    for i, (x1, x2, y1, y2) in enumerate(coordinates):
        part = img.crop((x1, y1, x2, y2))
        part_name = f'part_{i+1}.jpg'
        part_path = os.path.join(output_dir, part_name)
        
        # Сохраняем с оптимизацией
        part.save(part_path, 'JPEG', quality=85, optimize=True)
        parts.append(part)
        part_names.append(part_name)
    
    return part_names

def generate_color_histograms(original_path, part_paths, output_dir):
    """
    Генерирует гистограммы распределения цвета с использованием PIL
    Возвращает список имен файлов гистограмм
    """
    # Читаем все изображения
    images = {}
    
    # Оригинальное изображение
    try:
        orig_img = Image.open(original_path)
        if orig_img.mode != 'RGB':
            orig_img = orig_img.convert('RGB')
        images['Original'] = np.array(orig_img)
        orig_img.close()
    except Exception as e:
        print(f"Error loading original: {e}")
        return []
    
    # Части изображения
    for i, part_name in enumerate(part_paths):
        try:
            # Исправляем путь: plots → uploads
            uploads_dir = output_dir.replace('plots', 'uploads')
            part_path = os.path.join(uploads_dir, part_name)
            
            part_img = Image.open(part_path)
            if part_img.mode != 'RGB':
                part_img = part_img.convert('RGB')
            images[f'Part {i+1}'] = np.array(part_img)
            part_img.close()
        except Exception as e:
            print(f"Error loading part {i+1}: {e}")
            continue
    
    histogram_names = []
    
    for name, img_array in images.items():
        if img_array is None or img_array.size == 0:
            continue
        
        try:
            # Создаем новую фигуру для каждого графика
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # Создаем гистограммы для каждого канала (R, G, B)
            colors = ['red', 'green', 'blue']
            
            for i, color in enumerate(colors):
                # Извлекаем канал
                channel = img_array[:, :, i].flatten()
                
                # Строим гистограмму
                ax.hist(channel, bins=256, range=(0, 256), 
                        color=color, alpha=0.5, density=True, 
                        label=color.capitalize())
            
            ax.set_title(f'Color Distribution - {name}')
            ax.set_xlabel('Pixel Intensity (0-255)')
            ax.set_ylabel('Normalized Frequency')
            ax.grid(True, alpha=0.3)
            ax.set_xlim([0, 256])
            ax.legend()
            
            # Сохраняем график
            hist_name = f'hist_{name.lower().replace(" ", "_")}.png'
            hist_path = os.path.join(output_dir, hist_name)
            
            plt.savefig(hist_path, dpi=100, bbox_inches='tight')
            plt.close(fig)  # Явно закрываем фигуру
            
            histogram_names.append(hist_name)
            
        except Exception as e:
            print(f"Error creating histogram for {name}: {e}")
            continue
    
    return histogram_names