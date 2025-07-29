#!/usr/bin/env python3
"""
Скрипт для отправки файлов проекта в Telegram
"""

import asyncio
from telegram import Bot

# Ваши данные
BOT_TOKEN = "8228590806:AAE-P_9YHO9fuow_lZSLfw5hgoHPIwFABfM"
CHAT_ID = "89156628"

async def send_project_files():
    """Отправляет все файлы проекта в Telegram"""
    bot = Bot(token=BOT_TOKEN)
    
    files_content = {
        "requirements.txt": """requests>=2.31.0
python-telegram-bot>=20.7
aiohttp>=3.9.1
python-dotenv>=1.0.0""",
        
        ".env": """TELEGRAM_BOT_TOKEN=8228590806:AAE-P_9YHO9fuow_lZSLfw5hgoHPIwFABfM
TELEGRAM_CHAT_ID=89156628
MONITORING_INTERVAL=3
PRICE_CHANGE_THRESHOLD=2.0
BYBIT_BASE_URL=https://api.bybit.com""",
        
        "config.py": """import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    # Telegram настройки
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Настройки мониторинга
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 3))  # минуты
    PRICE_CHANGE_THRESHOLD = float(os.getenv('PRICE_CHANGE_THRESHOLD', 2.0))  # процент
    
    # Bybit API
    BYBIT_BASE_URL = os.getenv('BYBIT_BASE_URL', 'https://api.bybit.com')
    
    # Файлы данных
    DATA_DIR = 'data'
    CURRENT_DATA_FILE = f'{DATA_DIR}/current_prices.json'
    PREVIOUS_DATA_FILE = f'{DATA_DIR}/previous_prices.json'
    
    @classmethod
    def validate(cls):
        \"\"\"Проверяем наличие обязательных настроек\"\"\"
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID не установлен")
        
        # Создаем директорию для данных если её нет
        os.makedirs(cls.DATA_DIR, exist_ok=True)""",
        
        "crypto_api.py": """import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config
import random

class BybitAPI:
    \"\"\"
    Bybit API - линейные контракты (фьючерсы USDT)
    https://api.bybit.com/v5/market/tickers?category=linear
    \"\"\"
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = None
    
    async def __aenter__(self):
        # Создаем сессию с куками и таймаутом
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            cookie_jar=aiohttp.CookieJar()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        \"\"\"
        Получает все тикеры линейных контрактов с Bybit
        \"\"\"
        try:
            # Добавляем случайную задержку для имитации человека
            await asyncio.sleep(random.uniform(1, 3))
            
            # Используем эндпоинт для линейных контрактов (USDT фьючерсы)
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'linear'  # Линейные контракты (USDT фьючерсы)
            }
            
            # Максимально реалистичные заголовки браузера
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.bybit.com/',
                'Origin': 'https://www.bybit.com',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            print(f"🔄 Запрос к Bybit API: {url}")
            print(f"📋 Параметры: {params}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                print(f"📡 Статус ответа Bybit: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 Получен ответ от Bybit: retCode={data.get('retCode')}")
                    
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        print(f"✅ Получено {len(tickers)} USDT контрактов с Bybit")
                        return self._process_bybit_data(tickers)
                    else:
                        print(f"❌ Ошибка API Bybit: {data.get('retMsg')}")
                        return None
                else:
                    response_text = await response.text()
                    print(f"❌ HTTP ошибка Bybit {response.status}: {response_text[:200]}...")
                    return None
                    
        except Exception as e:
            print(f"❌ Ошибка при получении данных с Bybit: {e}")
            return None
    
    def _process_bybit_data(self, tickers: List[Dict]) -> List[Dict]:
        \"\"\"
        Обрабатывает данные тикеров с Bybit
        \"\"\"
        processed = []
        
        for ticker in tickers:
            try:
                symbol = ticker.get('symbol', '')
                # Фильтруем только USDT пары (линейные контракты)
                if not symbol.endswith('USDT'):
                    continue
                
                last_price = float(ticker.get('lastPrice', 0))
                price_24h_pcnt = float(ticker.get('price24hPcnt', 0)) * 100  # Конвертируем в проценты
                
                # Пропускаем пары с нулевой ценой
                if last_price == 0:
                    continue
                
                processed_ticker = {
                    'symbol': symbol,
                    'name': symbol.replace('USDT', ''),  # Убираем USDT из названия
                    'price': last_price,
                    'change_24h_percent': round(price_24h_pcnt, 2),
                    'volume_24h': float(ticker.get('volume24h', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://www.bybit.com/trade/usdt/{symbol}"
                }
                
                processed.append(processed_ticker)
                
            except (ValueError, TypeError) as e:
                print(f"⚠️ Ошибка обработки тикера Bybit {ticker}: {e}")
                continue
        
        print(f"📊 Обработано {len(processed)} USDT пар")
        return processed

# Функция для тестирования Bybit API
async def test_bybit_api():
    \"\"\"Тестовая функция для проверки работы Bybit API\"\"\"
    print("🧪 Тестируем Bybit API с улучшенными заголовками...")
    
    async with BybitAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Успешно! Получено {len(tickers)} USDT контрактов")
            print("\\n📈 Топ 5 контрактов:")
            for ticker in tickers[:5]:
                print(f"  💰 {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return True
        else:
            print("❌ Не удалось получить данные с Bybit API")
            return False

if __name__ == "__main__":
    asyncio.run(test_bybit_api())""",
    }
    
    try:
        # Отправляем приветственное сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🚀 <b>Crypto Bot Project Files</b>\n\nОтправляю все файлы проекта...",
            parse_mode='HTML'
        )
        
        # Отправляем каждый файл
        for filename, content in files_content.items():
            message = f"📄 <b>{filename}</b>\n\n<pre><code>{content}</code></pre>"
            
            # Разбиваем длинные сообщения
            if len(message) > 4000:
                # Отправляем заголовок
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"📄 <b>{filename}</b>",
                    parse_mode='HTML'
                )
                
                # Разбиваем контент на части
                chunks = [content[i:i+3800] for i in range(0, len(content), 3800)]
                for i, chunk in enumerate(chunks):
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"<pre><code>{chunk}</code></pre>",
                        parse_mode='HTML'
                    )
                    await asyncio.sleep(1)  # Задержка между сообщениями
            else:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='HTML'
                )
            
            await asyncio.sleep(2)  # Задержка между файлами
        
        # Финальное сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text="✅ <b>Все файлы отправлены!</b>\n\n📝 Скопируйте код и создайте файлы на Mac",
            parse_mode='HTML'
        )
        
        print("✅ Все файлы отправлены в Telegram!")
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

if __name__ == "__main__":
    asyncio.run(send_project_files())