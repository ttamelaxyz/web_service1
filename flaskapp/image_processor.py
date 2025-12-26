import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from PIL import Image

def split_image_into_four(image_path, output_dir):
    """
    Разбивает изображение на 4 равные части
    """
    img = Image.open(image_path)
    if img is None:
        raise ValueError("Cannot read image")
    
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

def generate_color_histograms(original_path, part_paths, output_dir):
    """
    Генерирует гистограммы распределения цвета
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