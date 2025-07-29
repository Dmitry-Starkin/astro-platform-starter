import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class BybitAPI:
    """
    Bybit API - линейные контракты (фьючерсы USDT)
    """
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает все тикеры линейных контрактов с Bybit
        """
        try:
            # Используем эндпоинт для линейных контрактов (USDT фьючерсы)
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'linear'  # Линейные контракты (USDT фьючерсы)
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к Bybit API: {url}")
            print(f"Параметры: {params}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                print(f"Статус ответа Bybit: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Получен ответ от Bybit: retCode={data.get('retCode')}")
                    
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        print(f"Получено {len(tickers)} контрактов с Bybit")
                        return self._process_bybit_data(tickers)
                    else:
                        print(f"Ошибка API Bybit: {data.get('retMsg')}")
                        return None
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка Bybit {response.status}: {response_text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с Bybit: {e}")
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
                print(f"Ошибка обработки тикера Bybit {ticker}: {e}")
                continue
        
        return processed

class CoinGeckoAPI:
    """
    CoinGecko API - резервный источник данных для демонстрации
    """
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает топ криптовалют с CoinGecko
        """
        try:
            # Получаем топ 50 криптовалют для быстрой демонстрации
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к CoinGecko API: {url}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                print(f"Статус ответа CoinGecko: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Получено {len(data)} криптовалют с CoinGecko")
                    return self._process_coingecko_data(data)
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка CoinGecko {response.status}: {response_text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с CoinGecko: {e}")
            return None
    
    def _process_coingecko_data(self, coins: List[Dict]) -> List[Dict]:
        """
        Обрабатывает данные криптовалют с CoinGecko
        """
        processed = []
        
        for coin in coins:
            try:
                symbol = coin.get('symbol', '').upper()
                name = coin.get('name', '')
                
                current_price = coin.get('current_price')
                price_change_24h = coin.get('price_change_percentage_24h')
                
                # Пропускаем монеты без цены
                if current_price is None or current_price == 0:
                    continue
                
                # Создаем символ в стиле биржи (например, BTCUSDT)
                trading_symbol = f"{symbol}USDT"
                
                processed_coin = {
                    'symbol': trading_symbol,
                    'name': name,
                    'price': float(current_price),
                    'change_24h_percent': round(float(price_change_24h or 0), 2),
                    'volume_24h': float(coin.get('total_volume', 0)),
                    'market_cap': float(coin.get('market_cap', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://www.coingecko.com/en/coins/{coin.get('id', '')}"
                }
                
                processed.append(processed_coin)
                
            except (ValueError, TypeError) as e:
                print(f"Ошибка обработки монеты CoinGecko {coin}: {e}")
                continue
        
        return processed

# Функция для тестирования API
async def test_apis():
    """Тестовая функция для проверки работы API"""
    print("🔄 Тестируем API...")
    
    # 1. Пробуем Bybit
    print("\n1️⃣ Тестируем Bybit API...")
    async with BybitAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Bybit: получено {len(tickers)} USDT контрактов")
            return tickers, "Bybit"
    
    # 2. Пробуем CoinGecko как резерв
    print("\n2️⃣ Bybit недоступен, тестируем CoinGecko API...")
    async with CoinGeckoAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ CoinGecko: получено {len(tickers)} криптовалют")
            return tickers, "CoinGecko"
    
    print("❌ Все API недоступны")
    return None, None

if __name__ == "__main__":
    asyncio.run(test_apis())