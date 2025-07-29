import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config

class DataManager:
    def __init__(self):
        self.current_file = Config.CURRENT_DATA_FILE
        self.previous_file = Config.PREVIOUS_DATA_FILE
        
        # Создаем директорию если её нет
        os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    def save_data(self, data: List[Dict], is_current: bool = True) -> bool:
        """
        Сохраняет данные в файл
        
        Args:
            data: Список данных о криптопарах
            is_current: True для текущих данных, False для предыдущих
        """
        try:
            filename = self.current_file if is_current else self.previous_file
            
            save_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'count': len(data)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"Сохранено {len(data)} криптопар в {filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
            return False
    
    def load_data(self, is_current: bool = True) -> Optional[Dict]:
        """
        Загружает данные из файла
        
        Args:
            is_current: True для текущих данных, False для предыдущих
        """
        try:
            filename = self.current_file if is_current else self.previous_file
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Ошибка загрузки данных из {filename}: {e}")
            return None
    
    def rotate_data(self) -> bool:
        """
        Перемещает текущие данные в предыдущие
        (current -> previous)
        """
        try:
            if os.path.exists(self.current_file):
                # Если есть предыдущий файл, удаляем его
                if os.path.exists(self.previous_file):
                    os.remove(self.previous_file)
                
                # Перемещаем текущий в предыдущий
                os.rename(self.current_file, self.previous_file)
                print("Данные ротированы: current -> previous")
                return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка ротации данных: {e}")
            return False
    
    def compare_data(self) -> List[Dict]:
        """
        Сравнивает текущие и предыдущие данные, находит значительные изменения
        
        Returns:
            Список изменений, превышающих порог
        """
        current_data = self.load_data(is_current=True)
        previous_data = self.load_data(is_current=False)
        
        if not current_data or not previous_data:
            print("Недостаточно данных для сравнения")
            return []
        
        current_prices = {item['symbol']: item for item in current_data['data']}
        previous_prices = {item['symbol']: item for item in previous_data['data']}
        
        significant_changes = []
        
        for symbol, current_item in current_prices.items():
            if symbol not in previous_prices:
                continue
            
            previous_item = previous_prices[symbol]
            
            # Вычисляем изменение цены
            current_price = current_item['price']
            previous_price = previous_item['price']
            
            if previous_price == 0:
                continue
            
            # Процентное изменение
            price_change_percent = ((current_price - previous_price) / previous_price) * 100
            
            # Проверяем, превышает ли изменение порог
            if abs(price_change_percent) >= Config.PRICE_CHANGE_THRESHOLD:
                change_info = {
                    'symbol': symbol,
                    'previous_price': previous_price,
                    'current_price': current_price,
                    'price_change_percent': round(price_change_percent, 2),
                    'price_change_abs': round(current_price - previous_price, 8),
                    'direction': 'up' if price_change_percent > 0 else 'down',
                    'volume_24h': current_item['volume_24h'],
                    'exchange_url': current_item['exchange_url'],
                    'timestamp_previous': previous_data['timestamp'],
                    'timestamp_current': current_data['timestamp'],
                    'monitoring_period_minutes': Config.MONITORING_INTERVAL
                }
                
                significant_changes.append(change_info)
        
        # Сортируем по величине изменения (по убыванию)
        significant_changes.sort(key=lambda x: abs(x['price_change_percent']), reverse=True)
        
        return significant_changes
    
    def get_data_age(self, is_current: bool = True) -> Optional[timedelta]:
        """
        Получает возраст данных
        
        Args:
            is_current: True для текущих данных, False для предыдущих
        """
        data = self.load_data(is_current)
        if not data:
            return None
        
        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
            return datetime.now() - timestamp
        except Exception:
            return None
    
    def cleanup_old_data(self, max_age_hours: int = 24) -> bool:
        """
        Удаляет старые данные
        
        Args:
            max_age_hours: Максимальный возраст данных в часах
        """
        try:
            for filename in [self.current_file, self.previous_file]:
                if os.path.exists(filename):
                    file_age = self.get_data_age(filename == self.current_file)
                    if file_age and file_age.total_seconds() > max_age_hours * 3600:
                        os.remove(filename)
                        print(f"Удален старый файл: {filename}")
            
            return True
            
        except Exception as e:
            print(f"Ошибка очистки старых данных: {e}")
            return False

# Функция для тестирования
def test_data_manager():
    """Тестовая функция для проверки работы DataManager"""
    dm = DataManager()
    
    # Тестовые данные
    test_data_1 = [
        {'symbol': 'BTCUSDT', 'price': 42000.0, 'change_24h_percent': 2.5, 'volume_24h': 1000000, 'exchange_url': 'https://example.com'},
        {'symbol': 'ETHUSDT', 'price': 2500.0, 'change_24h_percent': -1.2, 'volume_24h': 500000, 'exchange_url': 'https://example.com'},
    ]
    
    test_data_2 = [
        {'symbol': 'BTCUSDT', 'price': 43500.0, 'change_24h_percent': 5.8, 'volume_24h': 1200000, 'exchange_url': 'https://example.com'},  # +3.57%
        {'symbol': 'ETHUSDT', 'price': 2480.0, 'change_24h_percent': -2.1, 'volume_24h': 480000, 'exchange_url': 'https://example.com'},  # -0.8%
    ]
    
    print("Тестируем DataManager...")
    
    # Сохраняем первые данные как предыдущие
    dm.save_data(test_data_1, is_current=False)
    
    # Сохраняем вторые данные как текущие
    dm.save_data(test_data_2, is_current=True)
    
    # Сравниваем данные
    changes = dm.compare_data()
    
    print(f"\nНайдено {len(changes)} значительных изменений:")
    for change in changes:
        direction = "📈 РОСТ" if change['direction'] == 'up' else "📉 ПАДЕНИЕ"
        print(f"  {direction}: {change['symbol']} {change['price_change_percent']:+.2f}%")

if __name__ == "__main__":
    test_data_manager()