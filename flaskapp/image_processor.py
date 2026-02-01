import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def split_image_into_four(image_path, output_dir):
    """
    Разбиваем изображение на 4 равные части
    """
    img = Image.open(image_path)
    if img is None:
        raise ValueError("Cant read image")
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    w_mid = width // 2
    h_mid = height // 2
    
    parts = []
    part_names = []
    
    coordinates = [
        (0, w_mid, 0, h_mid),
        (w_mid, width, 0, h_mid),
        (0, w_mid, h_mid, height),
        (w_mid, width, h_mid, height)
    ]
    
    for i, (x1, x2, y1, y2) in enumerate(coordinates):
        part = img.crop((x1, y1, x2, y2))
        part_name = f'part_{i+1}.jpg'
        part_path = os.path.join(output_dir, part_name)
        
        part.save(part_path, 'JPEG', quality=85, optimize=True)
        parts.append(part)
        part_names.append(part_name)
    
    img.close()
    return part_names

def add_watermark_to_parts(part_names, output_dir, watermark_text, 
                          font_size=None, opacity=0.5, angle=30, 
                          color=(255, 255, 255, 128)):
    """
    Добавляет водяной знак на каждую часть изображения
    
    Args:
        part_names: список имен файлов частей
        output_dir: директория для сохранения
        watermark_text: текст водяного знака
        font_size: размер шрифта (автоопределение, если None)
        opacity: прозрачность (0.0 - 1.0)
        angle: угол наклона текста
        color: цвет текста в формате RGBA
        
    Returns:
        Список имен файлов с водяными знаками
    """
    if not watermark_text:
        return []
    
    watermarked_names = []
    
    for i, part_name in enumerate(part_names):
        try:
            # Открываем изображение
            part_path = os.path.join(output_dir, part_name)
            img = Image.open(part_path)
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Создаем слой для водяного знака
            watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # Определяем размер шрифта
            width, height = img.size
            if font_size is None:
                #расчет размера шрифта
                font_size = min(width, height) // 10
            
            # Используем системный шрифт
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Рассчитываем размер текста
            try:
                text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except:
                text_width, text_height = draw.textsize(watermark_text, font=font)
            
            # Позиционируем текст по центру
            position = ((width - text_width) // 2, 
                       (height - text_height) // 2)
            
            # Рисуем текст
            draw.text(position, watermark_text, font=font, fill=color)
            
            # Поворачиваем текст
            watermark_layer = watermark_layer.rotate(angle, expand=0, fillcolor=(0, 0, 0, 0))
            
            # Регулируем прозрачность
            if opacity != 1.0:
                alpha = watermark_layer.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                watermark_layer.putalpha(alpha)
            
            # Накладываем водяной знак на изображение
            watermarked = Image.alpha_composite(img, watermark_layer)
            
            # Конвертируем обратно в RGB для сохранения в JPEG
            if watermarked.mode == 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # Сохраняем
            watermarked_name = f'watermarked_{i+1}.jpg'
            watermarked_path = os.path.join(output_dir, watermarked_name)
            watermarked.save(watermarked_path, 'JPEG', quality=90, optimize=True)
            
            watermarked_names.append(watermarked_name)
            
            img.close()
            
        except Exception as e:
            print(f"Error adding watermark to {part_name}: {e}")
            continue
    
    return watermarked_names

def generate_color_histograms(original_path, part_paths, output_dir):
    """
    Генерируем гистограммы распределения цвета
    """
    images = {}
    
    try:
        orig_img = Image.open(original_path)
        if orig_img.mode != 'RGB':
            orig_img = orig_img.convert('RGB')
        images['Original'] = np.array(orig_img)
        orig_img.close()
    except Exception as e:
        print(f"Error loading original: {e}")
        return []
    
    for i, part_name in enumerate(part_paths):
        try:
            uploads_dir = output_dir.replace('plots', 'uploads')
            part_path = os.path.join(uploads_dir, part_name)
            
            part_img = Image.open(part_path)
            if part_img.mode != 'RGB':
                part_img = part_img.convert('RGB')
            images[f'Part_{i+1}'] = np.array(part_img)
            part_img.close()
        except Exception as e:
            print(f"Error loading part {i+1}: {e}")
            continue
    
    histogram_names = []
    
    for name, img_array in images.items():
        if img_array is None or img_array.size == 0:
            continue
        
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            colors = ['red', 'green', 'blue']
            
            for i, color in enumerate(colors):
                channel = img_array[:, :, i].flatten()
                ax.hist(channel, bins=64, range=(0, 256), 
                       color=color, alpha=0.5, density=True)
            
            ax.set_title(f'Color Distribution - {name}')
            ax.set_xlabel('Pixel Intensity')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
            ax.set_xlim([0, 256])
            
            hist_name = f'hist_{name.lower()}.png'
            hist_path = os.path.join(output_dir, hist_name)
            
            plt.savefig(hist_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            histogram_names.append(hist_name)
            
        except Exception as e:
            print(f"Error creating histogram for {name}: {e}")
            continue
    
    return histogram_names

def add_diagonal_watermark(part_names, output_dir, watermark_text, 
                          font_size=None, opacity=0.3, spacing=200):
    """
    Альтернативная функция: повторяющийся водяной знак по диагонали
    """
    if not watermark_text:
        return []
    
    watermarked_names = []
    
    for i, part_name in enumerate(part_names):
        try:
            part_path = os.path.join(output_dir, part_name)
            img = Image.open(part_path)
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            width, height = img.size
            if font_size is None:
                font_size = min(width, height) // 15
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Создаем повторяющийся узор
            text_length = len(watermark_text) * font_size
            for x in range(-height, width + height, spacing):
                for y in range(-width, height + width, spacing):
                    # Рисуем под углом 45 градусов
                    draw.text((x, y), watermark_text, font=font, 
                             fill=(255, 255, 255, int(255 * opacity)), 
                             stroke_width=1, stroke_fill=(0, 0, 0, 100))
            
            # Накладываем водяной знак
            watermarked = Image.alpha_composite(img, watermark_layer)
            
            if watermarked.mode == 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            watermarked_name = f'diagonal_watermark_{i+1}.jpg'
            watermarked_path = os.path.join(output_dir, watermarked_name)
            watermarked.save(watermarked_path, 'JPEG', quality=90, optimize=True)
            
            watermarked_names.append(watermarked_name)
            img.close()
            
        except Exception as e:
            print(f"Error adding diagonal watermark: {e}")
            continue
    
    return watermarked_names