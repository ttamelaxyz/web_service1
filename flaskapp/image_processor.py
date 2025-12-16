from PIL import Image
import numpy as np

def split_image_into_four(image_path):
    """
    Разбивает изображение на 4 равные части
    Возвращает список из 4 объектов Image
    """
    # Открываем изображение
    img = Image.open(image_path)
    width, height = img.size
    
    # Вычисляем середины
    mid_x = width // 2
    mid_y = height // 2
    
    # Разбиваем на 4 части
    parts = [
        img.crop((0, 0, mid_x, mid_y)),           # Верхний левый
        img.crop((mid_x, 0, width, mid_y)),       # Верхний правый
        img.crop((0, mid_y, mid_x, height)),      # Нижний левый
        img.crop((mid_x, mid_y, width, height))   # Нижний правый
    ]
    
    return parts

def get_color_distribution(img):
    """
    Рассчитывает среднюю интенсивность для каждого цветового канала
    Возвращает словарь с нормализованными значениями (0-1)
    """
    if not isinstance(img, np.ndarray):
        img_array = np.array(img)
    else:
        img_array = img
    
    # Если изображение в градациях серого
    if len(img_array.shape) == 2:
        gray_value = np.mean(img_array) / 255.0
        return {'red': gray_value, 'green': gray_value, 'blue': gray_value}
    
    # Для цветных изображений (RGB)
    elif len(img_array.shape) == 3:
        # Разделяем на каналы
        red_channel = img_array[:, :, 0]
        green_channel = img_array[:, :, 1]
        blue_channel = img_array[:, :, 2]
        
        # Рассчитываем среднюю интенсивность
        red_avg = np.mean(red_channel) / 255.0
        green_avg = np.mean(green_channel) / 255.0
        blue_avg = np.mean(blue_channel) / 255.0
        
        return {
            'red': float(red_avg),
            'green': float(green_avg),
            'blue': float(blue_avg)
        }
    
    return {'red': 0, 'green': 0, 'blue': 0}
