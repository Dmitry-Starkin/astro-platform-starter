#!/usr/bin/env python3
"""
Crypto Price Monitor Bot
Мониторинг изменений цен криптовалют на Bybit с уведомлениями в Telegram
"""

import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional

from config import Config
from bybit_api import BybitAPI
from data_manager import DataManager
from telegram_bot import CryptoTelegramBot

class CryptoPriceMonitor:
    def __init__(self):
        self.running = False
        self.data_manager = DataManager()
        self.telegram_bot = None
        self.bybit_api = None
        
        # Проверяем конфигурацию
        try:
            Config.validate()
        except ValueError as e:
            print(f"Ошибка конфигурации: {e}")
            print("Проверьте файл .env и настройте необходимые переменные")
            sys.exit(1)
    
    async def initialize(self) -> bool:
        """
        Инициализация компонентов бота
        """
        try:
            print("🚀 Инициализация Crypto Price Monitor...")
            
            # Инициализируем Telegram бота
            self.telegram_bot = CryptoTelegramBot()
            
            # Тестируем подключение к Telegram
            if not await self.telegram_bot.test_connection():
                print("❌ Ошибка подключения к Telegram")
                return False
            
            # Инициализируем Bybit API
            self.bybit_api = BybitAPI()
            
            print("✅ Инициализация завершена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def fetch_and_save_data(self) -> bool:
        """
        Получает данные с Bybit и сохраняет их
        """
        try:
            print(f"📊 Получение данных с Bybit... ({datetime.now().strftime('%H:%M:%S')})")
            
            async with self.bybit_api as api:
                tickers = await api.get_all_tickers()
            
            if not tickers:
                print("❌ Не удалось получить данные с Bybit")
                return False
            
            # Ротируем данные (current -> previous)
            self.data_manager.rotate_data()
            
            # Сохраняем новые данные как текущие
            if self.data_manager.save_data(tickers, is_current=True):
                print(f"✅ Сохранено {len(tickers)} криптопар")
                return True
            else:
                print("❌ Ошибка сохранения данных")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            return False
    
    async def check_price_changes(self) -> bool:
        """
        Проверяет изменения цен и отправляет уведомления
        """
        try:
            print("🔍 Анализ изменений цен...")
            
            # Сравниваем данные и находим значительные изменения
            changes = self.data_manager.compare_data()
            
            if not changes:
                print("📈 Значительных изменений не обнаружено")
                return True
            
            print(f"🚨 Обнаружено {len(changes)} значительных изменений:")
            for change in changes[:5]:  # Показываем первые 5
                direction = "📈" if change['direction'] == 'up' else "📉"
                print(f"  {direction} {change['symbol']}: {change['price_change_percent']:+.2f}%")
            
            if len(changes) > 5:
                print(f"  ... и ещё {len(changes) - 5} изменений")
            
            # Отправляем уведомления в Telegram
            if await self.telegram_bot.send_price_alerts(changes):
                print("✅ Уведомления отправлены в Telegram")
                return True
            else:
                print("❌ Ошибка отправки уведомлений")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка анализа изменений: {e}")
            return False
    
    async def monitoring_cycle(self):
        """
        Основной цикл мониторинга
        """
        print(f"🔄 Запуск мониторинга (интервал: {Config.MONITORING_INTERVAL} мин, порог: {Config.PRICE_CHANGE_THRESHOLD}%)")
        
        # Первый запуск - только получаем данные
        print("\n" + "="*50)
        print("📊 ПЕРВИЧНОЕ ПОЛУЧЕНИЕ ДАННЫХ")
        print("="*50)
        
        await self.fetch_and_save_data()
        
        print(f"⏰ Ожидание {Config.MONITORING_INTERVAL} минут до первого сравнения...")
        await asyncio.sleep(Config.MONITORING_INTERVAL * 60)
        
        cycle_count = 1
        
        while self.running:
            try:
                print("\n" + "="*50)
                print(f"🔄 ЦИКЛ МОНИТОРИНГА #{cycle_count}")
                print("="*50)
                
                # Получаем новые данные
                if await self.fetch_and_save_data():
                    # Анализируем изменения и отправляем уведомления
                    await self.check_price_changes()
                else:
                    print("⚠️ Пропускаем анализ из-за ошибки получения данных")
                
                print(f"⏰ Следующая проверка через {Config.MONITORING_INTERVAL} минут...")
                
                # Ждем до следующего цикла
                await asyncio.sleep(Config.MONITORING_INTERVAL * 60)
                cycle_count += 1
                
            except asyncio.CancelledError:
                print("🛑 Мониторинг остановлен")
                break
            except Exception as e:
                print(f"❌ Ошибка в цикле мониторинга: {e}")
                print(f"⏰ Повтор через {Config.MONITORING_INTERVAL} минут...")
                await asyncio.sleep(Config.MONITORING_INTERVAL * 60)
    
    async def start(self):
        """
        Запуск мониторинга
        """
        if not await self.initialize():
            return False
        
        self.running = True
        
        try:
            await self.monitoring_cycle()
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки")
        finally:
            await self.stop()
        
        return True
    
    async def stop(self):
        """
        Остановка мониторинга
        """
        print("🛑 Остановка мониторинга...")
        self.running = False
        
        # Отправляем уведомление об остановке
        if self.telegram_bot:
            try:
                stop_message = f"🛑 <b>Мониторинг остановлен</b>\n🕐 Время: {datetime.now().strftime('%H:%M:%S')}"
                await self.telegram_bot.send_status_message(stop_message)
            except:
                pass  # Игнорируем ошибки при остановке
        
        print("✅ Мониторинг остановлен")

def setup_signal_handlers(monitor):
    """
    Настройка обработчиков сигналов для корректной остановки
    """
    def signal_handler(signum, frame):
        print(f"\n🛑 Получен сигнал {signum}")
        asyncio.create_task(monitor.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """
    Главная функция
    """
    print("🚀 Crypto Price Monitor Bot")
    print("="*50)
    print(f"📊 Биржа: Bybit")
    print(f"⏰ Интервал: {Config.MONITORING_INTERVAL} минут")
    print(f"📈 Порог уведомлений: {Config.PRICE_CHANGE_THRESHOLD}%")
    print(f"💬 Telegram Chat ID: {Config.TELEGRAM_CHAT_ID}")
    print("="*50)
    
    monitor = CryptoPriceMonitor()
    
    # Настраиваем обработчики сигналов
    setup_signal_handlers(monitor)
    
    try:
        success = await monitor.start()
        if not success:
            print("❌ Не удалось запустить мониторинг")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
        sys.exit(1)