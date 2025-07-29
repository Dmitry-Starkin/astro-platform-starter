import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class BybitAPI:
    def __init__(self):
        self.base_url = Config.BYBIT_BASE_URL
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
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'spot'  # Только спотовые пары
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        return self._process_tickers(tickers)
                    else:
                        print(f"Ошибка API Bybit: {data.get('retMsg')}")
                        return None
                else:
                    print(f"HTTP ошибка: {response.status}")
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
            
            async with self.session.get(url, params=params) as response:
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

# Функция для тестирования API
async def test_bybit_api():
    """Тестовая функция для проверки работы API"""
    async with BybitAPI() as api:
        print("Тестируем Bybit API...")
        
        # Получаем все тикеры
        tickers = await api.get_all_tickers()
        
        if tickers:
            print(f"Получено {len(tickers)} криптопар")
            print("\nПервые 5 пар:")
            for ticker in tickers[:5]:
                print(f"  {ticker['symbol']}: ${ticker['price']:.4f} ({ticker['change_24h_percent']:+.2f}%)")
        else:
            print("Ошибка получения данных")

if __name__ == "__main__":
    asyncio.run(test_bybit_api())