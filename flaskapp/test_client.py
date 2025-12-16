import requests
import json
import os
from PIL import Image
import io

def test_app():
    print("Тестирование веб-приложения...")
    
    # 1. Проверяем доступность главной страницы
    try:
        response = requests.get('http://127.0.0.1:5000/')
        if response.status_code == 200:
            print("Главная страница доступна")
        else:
            print(f"Главная страница недоступна: {response.status_code}")
            return 1
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return 1
    
    # 2. Создаем тестовое изображение
    print("Создание тестового изображения...")
    img = Image.new('RGB', (400, 300), color='red')
    img.save('test_image.png')
    
    # 3. Отправляем изображение на обработку
    print("Отправка изображения на обработку...")
    try:
        with open('test_image.png', 'rb') as f:
            files = {'image': f}
            response = requests.post('http://127.0.0.1:5000/', files=files)
        
        if response.status_code == 200:
            print("✓ Изображение успешно отправлено")
        else:
            print(f"✗ Ошибка при отправке: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return 1
    
    # 4. Проверяем API endpoint
    print("Проверка API...")
    try:
        response = requests.get('http://127.0.0.1:5000/process/test_image.png')
        if response.status_code == 200:
            print("✓ API endpoint работает")
        else:
            print(f"✗ API endpoint не работает: {response.status_code}")
            return 1
    except Exception as e:
        print(f"✗ Ошибка API: {e}")
        return 1
    
    # 5. Удаляем тестовые файлы
    if os.path.exists('test_image.png'):
        os.remove('test_image.png')
    
    print("\nсе тесты пройдены успешно!")
    return 0

if __name__ == '__main__':
    exit(test_app())
