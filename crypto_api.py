import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class CoinCapAPI:
    """
    CoinCap API - простой и надежный источник данных без ограничений
    """
    def __init__(self):
        self.base_url = "https://api.coincap.io/v2"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает все криптовалюты с CoinCap
        """
        try:
            # Получаем топ 2000 криптовалют (максимальный лимит)
            url = f"{self.base_url}/assets"
            params = {
                'limit': 2000
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoBot/1.0)',
                'Accept': 'application/json'
            }
            
            print(f"Запрос к CoinCap API: {url}")
            print(f"Параметры: {params}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                print(f"Статус ответа CoinCap: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    assets = data.get('data', [])
                    print(f"Получено {len(assets)} криптовалют с CoinCap")
                    return self._process_coincap_data(assets)
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка CoinCap {response.status}: {response_text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с CoinCap: {e}")
            return None
    
    def _process_coincap_data(self, assets: List[Dict]) -> List[Dict]:
        """
        Обрабатывает данные криптовалют с CoinCap
        """
        processed = []
        
        for asset in assets:
            try:
                symbol = asset.get('symbol', '').upper()
                name = asset.get('name', '')
                
                price_usd = asset.get('priceUsd')
                change_percent_24hr = asset.get('changePercent24Hr')
                
                # Пропускаем активы без цены
                if not price_usd or float(price_usd) == 0:
                    continue
                
                # Создаем символ в стиле биржи
                trading_symbol = f"{symbol}USDT"
                
                processed_asset = {
                    'symbol': trading_symbol,
                    'name': name,
                    'price': float(price_usd),
                    'change_24h_percent': round(float(change_percent_24hr or 0), 2),
                    'volume_24h': float(asset.get('volumeUsd24Hr', 0)),
                    'market_cap': float(asset.get('marketCapUsd', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'exchange_url': f"https://coincap.io/assets/{asset.get('id', '')}"
                }
                
                processed.append(processed_asset)
                
            except (ValueError, TypeError) as e:
                print(f"Ошибка обработки актива CoinCap {asset}: {e}")
                continue
        
        return processed

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

class BinanceAPI:
    """
    Binance API - быстрый и надежный источник данных
    """
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        Получает все тикеры с Binance
        """
        try:
            # Получаем данные о 24h статистике (включает цены и изменения)
            url = f"{self.base_url}/ticker/24hr"
            
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
                    return self._process_binance_data(data)
                else:
                    response_text = await response.text()
                    print(f"HTTP ошибка Binance {response.status}: {response_text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"Ошибка при получении данных с Binance: {e}")
            return None
    
    def _process_binance_data(self, tickers: List[Dict]) -> List[Dict]:
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
                    'name': symbol.replace('USDT', ''),  # Используем символ как имя
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
                    'name': symbol.replace('USD', ''),
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
    
    # 1. Пробуем CoinCap (новый приоритетный - без ограничений)
    print("\n1️⃣ Тестируем CoinCap API...")
    async with CoinCapAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ CoinCap: получено {len(tickers)} криптовалют")
            print("Топ 5 по капитализации:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "CoinCap"
    
    # 2. Пробуем Bybit
    print("\n2️⃣ CoinCap недоступен, тестируем Bybit API (linear контракты)...")
    async with BybitAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Bybit: получено {len(tickers)} USDT контрактов")
            print("Топ 5 контрактов:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "Bybit"
    
    # 3. Пробуем Binance
    print("\n3️⃣ Bybit недоступен, тестируем Binance API...")
    async with BinanceAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ Binance: получено {len(tickers)} USDT пар")
            print("Топ 5 пар:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "Binance"
    
    # 4. Пробуем CoinGecko
    print("\n4️⃣ Binance недоступен, тестируем CoinGecko API...")
    async with CoinGeckoAPI() as api:
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"✅ CoinGecko: получено {len(tickers)} криптовалют")
            print("Топ 5 по капитализации:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
            return tickers, "CoinGecko"
    
    # 5. Пробуем Kraken
    print("\n5️⃣ CoinGecko недоступен, тестируем Kraken API...")
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