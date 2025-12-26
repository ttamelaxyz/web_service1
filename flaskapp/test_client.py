import requests
import os

# Тест основного функционала
def test_main():
    print("Testing Flask application...")
    
    # Проверяем доступность главной страницы
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("Main page: OK")
        else:
            print(f"Main page: ERROR - {response.status_code}")
    except Exception as e:
        print(f"Main page: ERROR - {e}")

if __name__ == "__main__":
    test_main()