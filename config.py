import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    # Telegram настройки
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Настройки мониторинга
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 3))  # минуты
    PRICE_CHANGE_THRESHOLD = float(os.getenv('PRICE_CHANGE_THRESHOLD', 3.0))  # процент
    
    # Bybit API
    BYBIT_BASE_URL = os.getenv('BYBIT_BASE_URL', 'https://api.bybit.com')
    
    # Файлы данных
    DATA_DIR = 'data'
    CURRENT_DATA_FILE = f'{DATA_DIR}/current_prices.json'
    PREVIOUS_DATA_FILE = f'{DATA_DIR}/previous_prices.json'
    
    @classmethod
    def validate(cls):
        """Проверяем наличие обязательных настроек"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID не установлен")
        
        # Создаем директорию для данных если её нет
        os.makedirs(cls.DATA_DIR, exist_ok=True)