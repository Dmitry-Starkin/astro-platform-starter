import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class BybitAPI:
    def __init__(self):
        # Используем актуальный базовый URL для Bybit API
        self.base_url = "https://api-testnet.bybit.com"  # Тестовый URL
        # Для продакшена: self.base_url = "https://api.bybit.com"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает все тикеры с Bybit для спотовой торговли
        """
        try:
            # Используем публичный эндпоинт для получения тикеров
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'spot'  # Только спотовые пары
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к URL: {url}")
            print(f"Параметры: {params}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                print(f"Статус ответа: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Получен ответ: {json.dumps(data, indent=2)[:500]}...")
                    
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        return self._process_tickers(tickers)
                    else:
                        print(f"Ошибка API Bybit: {data.get('retMsg')}")
                        return None
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка {response.status}: {response_text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с Bybit: {e}")
            return None
    
    def _process_tickers(self, tickers: List[Dict]) -> List[Dict]:
        """
        Обрабатывает сырые данные тикеров в нужный формат
        """
        processed = []
        
        for ticker in tickers:
            try:
                symbol = ticker.get('symbol', '')
                # Фильтруем только USDT пары
                if not symbol.endswith('USDT'):
                    continue
                
                last_price = float(ticker.get('lastPrice', 0))
                price_24h_pcnt = float(ticker.get('price24hPcnt', 0)) * 100  # Конвертируем в проценты
                
                # Пропускаем пары с нулевой ценой
                if last_price == 0:
                    continue
                
                processed_ticker = {
                    'symbol': symbol,
                    'price': last_price,
                    'change_24h_percent': round(price_24h_pcnt, 2),
                    'volume_24h': float(ticker.get('volume24h', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://www.bybit.com/trade/usdt/{symbol}"
                }
                
                processed.append(processed_ticker)
                
            except (ValueError, TypeError) as e:
                print(f"Ошибка обработки тикера {ticker}: {e}")
                continue
        
        return processed
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Получает информацию о конкретной паре
        """
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'spot',
                'symbol': symbol
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        if tickers:
                            return self._process_tickers(tickers)[0]
                return None
                
        except Exception as e:
            print(f"Ошибка при получении информации о {symbol}: {e}")
            return None

# Альтернативный класс для работы с другим API (если Bybit не работает)
class AlternativeCryptoAPI:
    def __init__(self):
        self.base_url = "https://api.binance.com"  # Используем Binance как альтернативу
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает все тикеры с Binance (альтернатива)
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к Binance API: {url}")
            
            async with self.session.get(url, headers=headers) as response:
                print(f"Статус ответа Binance: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Получено {len(data)} тикеров с Binance")
                    return self._process_binance_tickers(data)
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка Binance {response.status}: {response_text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с Binance: {e}")
            return None
    
    def _process_binance_tickers(self, tickers: List[Dict]) -> List[Dict]:
        """
        Обрабатывает данные тикеров с Binance
        """
        processed = []
        
        for ticker in tickers:
            try:
                symbol = ticker.get('symbol', '')
                # Фильтруем только USDT пары
                if not symbol.endswith('USDT'):
                    continue
                
                last_price = float(ticker.get('lastPrice', 0))
                price_change_percent = float(ticker.get('priceChangePercent', 0))
                
                # Пропускаем пары с нулевой ценой
                if last_price == 0:
                    continue
                
                processed_ticker = {
                    'symbol': symbol,
                    'price': last_price,
                    'change_24h_percent': round(price_change_percent, 2),
                    'volume_24h': float(ticker.get('volume', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://www.binance.com/en/trade/{symbol}"
                }
                
                processed.append(processed_ticker)
                
            except (ValueError, TypeError) as e:
                print(f"Ошибка обработки тикера Binance {ticker}: {e}")
                continue
        
        return processed

# Функция для тестирования API
async def test_crypto_apis():
    """Тестовая функция для проверки работы API"""
    print("🔄 Тестируем криптовалютные API...")
    
    # Сначала пробуем Bybit
    print("\n1️⃣ Тестируем Bybit API...")
    async with BybitAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Bybit: получено {len(tickers)} криптопар")
            print("Первые 5 пар:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers
    
    # Если Bybit не работает, пробуем Binance
    print("\n2️⃣ Bybit недоступен, тестируем Binance API...")
    async with AlternativeCryptoAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Binance: получено {len(tickers)} криптопар")
            print("Первые 5 пар:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers
    
    print("❌ Все API недоступны")
    return None

if __name__ == "__main__":
    asyncio.run(test_crypto_apis())