import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class CoinGeckoAPI:
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
            # Получаем топ 250 криптовалют (бесплатный лимит)
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к CoinGecko API: {url}")
            print(f"Параметры: {params}")
            
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

class KrakenAPI:
    """
    Альтернативный API - Kraken (обычно более доступен)
    """
    def __init__(self):
        self.base_url = "https://api.kraken.com/0/public"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает тикеры с Kraken
        """
        try:
            url = f"{self.base_url}/Ticker"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к Kraken API: {url}")
            
            async with self.session.get(url, headers=headers) as response:
                print(f"Статус ответа Kraken: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    if data.get('error') and len(data['error']) == 0:
                        result = data.get('result', {})
                        print(f"Получено {len(result)} пар с Kraken")
                        return self._process_kraken_data(result)
                    else:
                        print(f"Ошибка Kraken API: {data.get('error')}")
                        return None
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка Kraken {response.status}: {response_text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с Kraken: {e}")
            return None
    
    def _process_kraken_data(self, pairs: Dict) -> List[Dict]:
        """
        Обрабатывает данные пар с Kraken
        """
        processed = []
        
        for pair_name, pair_data in pairs.items():
            try:
                # Фильтруем только USD пары
                if not ('USD' in pair_name or 'USDT' in pair_name):
                    continue
                
                # Получаем последнюю цену и изменение за 24ч
                last_price = float(pair_data.get('c', [0])[0])  # Последняя цена
                
                if last_price == 0:
                    continue
                
                # Вычисляем изменение за 24ч
                open_price = float(pair_data.get('o', 0))
                change_24h_percent = 0
                if open_price > 0:
                    change_24h_percent = ((last_price - open_price) / open_price) * 100
                
                # Очищаем имя пары
                symbol = pair_name.replace('XXBT', 'BTC').replace('XETH', 'ETH').replace('ZUSD', 'USD')
                
                processed_pair = {
                    'symbol': symbol,
                    'price': last_price,
                    'change_24h_percent': round(change_24h_percent, 2),
                    'volume_24h': float(pair_data.get('v', [0])[1]),  # 24h объем
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://trade.kraken.com/charts/KRAKEN:{symbol}"
                }
                
                processed.append(processed_pair)
                
            except (ValueError, TypeError, IndexError) as e:
                print(f"Ошибка обработки пары Kraken {pair_name}: {e}")
                continue
        
        return processed

# Функция для тестирования всех API
async def test_all_crypto_apis():
    """Тестовая функция для проверки работы всех API"""
    print("🔄 Тестируем все доступные криптовалютные API...")
    
    # 1. Пробуем CoinGecko
    print("\n1️⃣ Тестируем CoinGecko API...")
    async with CoinGeckoAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ CoinGecko: получено {len(tickers)} криптовалют")
            print("Топ 5 по капитализации:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "CoinGecko"
    
    # 2. Пробуем Kraken
    print("\n2️⃣ CoinGecko недоступен, тестируем Kraken API...")
    async with KrakenAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Kraken: получено {len(tickers)} пар")
            print("Первые 5 пар:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "Kraken"
    
    print("❌ Все API недоступны")
    return None, None

if __name__ == "__main__":
    asyncio.run(test_all_crypto_apis())