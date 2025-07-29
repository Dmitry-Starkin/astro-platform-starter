import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config
import random

class BybitAPI:
    """
    Bybit API - линейные контракты (фьючерсы USDT)
    https://api.bybit.com/v5/market/tickers?category=linear
    """
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
        """
        Получает все тикеры линейных контрактов с Bybit
        """
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
        """
        Обрабатывает данные тикеров с Bybit
        """
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
    """Тестовая функция для проверки работы Bybit API"""
    print("🧪 Тестируем Bybit API с улучшенными заголовками...")
    
    async with BybitAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Успешно! Получено {len(tickers)} USDT контрактов")
            print("\n📈 Топ 5 контрактов:")
            for ticker in tickers[:5]:
                print(f"  💰 {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return True
        else:
            print("❌ Не удалось получить данные с Bybit API")
            return False

if __name__ == "__main__":
    asyncio.run(test_bybit_api())