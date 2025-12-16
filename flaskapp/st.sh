#!/bin/bash

# Запускаем сервер в фоновом режиме
gunicorn --bind 127.0.0.1:5000 wsgi:app --workers 2 --timeout 120 & APP_PID=$!

# Ждем запуска сервера
sleep 10

# Запускаем тесты
echo "Запуск тестов..."
python3 test_client.py
TEST_RESULT=$?

# Останавливаем сервер
kill -TERM $APP_PID
wait $APP_PID

# Возвращаем код результата тестов
exit $TEST_RESULT
