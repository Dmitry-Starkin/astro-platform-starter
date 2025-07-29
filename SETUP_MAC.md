# 🚀 Crypto Price Monitor Bot - Установка на Mac

## 📋 Требования
- macOS 10.15 или новее
- Python 3.8+ (обычно уже установлен)
- Visual Studio Code
- Доступ к интернету

## 🛠 Установка

### 1. Распаковка проекта
```bash
# Распакуйте архив crypto_bot_project.tar.gz
tar -xzf crypto_bot_project.tar.gz
cd crypto_bot_project
```

### 2. Откройте проект в VS Code
```bash
code .
```

### 3. Создайте виртуальное окружение
```bash
# В терминале VS Code
python3 -m venv venv
source venv/bin/activate
```

### 4. Установите зависимости
```bash
pip install -r requirements.txt
```

### 5. Настройте конфигурацию
```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл в VS Code
# Вставьте ваши данные:
```

Отредактируйте файл `.env`:
```env
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN=8228590806:AAE-P_9YHO9fuow_lZSLfw5hgoHPIwFABfM

# Telegram Chat ID (ваш ID)
TELEGRAM_CHAT_ID=89156628

# Настройки мониторинга
MONITORING_INTERVAL=3  # минуты
PRICE_CHANGE_THRESHOLD=2.0  # процент изменения для уведомления

# Bybit API (публичные эндпоинты, ключи не нужны)
BYBIT_BASE_URL=https://api.bybit.com
```

## 🚀 Запуск

### Способ 1: Через скрипт (рекомендуется)
```bash
chmod +x start_bot.sh
./start_bot.sh
```

### Способ 2: Напрямую
```bash
source venv/bin/activate
python3 main.py
```

### Способ 3: В фоновом режиме
```bash
source venv/bin/activate
nohup python3 main.py > bot.log 2>&1 &
```

## 📊 Что делает бот

### ✅ Функционал:
- **Мониторинг**: Каждые 3 минуты получает данные от Bybit API
- **Анализ**: Сравнивает текущие цены с предыдущими
- **Уведомления**: Отправляет в Telegram при изменениях ≥2%
- **Данные**: Только USDT пары (фьючерсы)

### 📱 Формат уведомлений:
```
🚨 Значительные изменения цен!

📈 BTCUSDT: +2.5% за 3 мин
💰 Цена: $117,500 → $120,437
🔗 https://www.bybit.com/trade/usdt/BTCUSDT

📉 ETHUSDT: -3.1% за 3 мин  
💰 Цена: $3,750 → $3,634
🔗 https://www.bybit.com/trade/usdt/ETHUSDT
```

## 🛠 Структура проекта

```
crypto_bot_project/
├── main.py              # Главный файл - запуск бота
├── crypto_api.py        # Работа с Bybit API
├── telegram_bot.py      # Telegram уведомления
├── data_manager.py      # Сохранение и сравнение данных
├── config.py           # Конфигурация
├── requirements.txt    # Python зависимости
├── .env               # Ваши настройки (создается)
├── .env.example       # Пример настроек
├── start_bot.sh       # Скрипт запуска
├── README.md          # Основная документация
└── SETUP_MAC.md       # Эта инструкция
```

## 🔧 Отладка

### Проверка Bybit API:
```bash
python3 crypto_api.py
```

### Просмотр логов:
```bash
tail -f bot.log
```

### Остановка бота:
```bash
# Найти процесс
ps aux | grep "python3 main.py"

# Остановить по PID
kill <PID>
```

## ⚠️ Возможные проблемы

### 1. Bybit API недоступен (ошибка 403)
- **Причина**: Географические ограничения
- **Решение**: Бот будет продолжать попытки каждые 3 минуты

### 2. Telegram ошибки
- **Проверьте**: Правильность токена бота и Chat ID
- **Тест**: Отправьте `/start` боту в Telegram

### 3. Python не найден
```bash
# Установите через Homebrew
brew install python3
```

## 🎯 Настройки

В файле `.env` можно изменить:

- `MONITORING_INTERVAL=3` - интервал проверки (минуты)
- `PRICE_CHANGE_THRESHOLD=2.0` - порог уведомлений (%)

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f bot.log`
2. Убедитесь в правильности `.env`
3. Протестируйте API: `python3 crypto_api.py`

## 🚀 Готово!

Бот будет работать 24/7 и отправлять уведомления только при значительных изменениях цен USDT пар на Bybit!