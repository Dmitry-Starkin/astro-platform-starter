#!/bin/bash

echo "🚀 Запуск Crypto Price Monitor Bot..."

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден. Скопируйте .env.example в .env и настройте его."
    exit 1
fi

echo "🔄 Запуск мониторинга..."
python3 main.py