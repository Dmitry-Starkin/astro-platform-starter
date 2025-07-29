import asyncio
from datetime import datetime
from typing import List, Dict
from telegram import Bot
from telegram.error import TelegramError
from config import Config

class CryptoTelegramBot:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.bot = None
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Не настроены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
        
        self.bot = Bot(token=self.bot_token)
    
    def format_price_change_message(self, change: Dict) -> str:
        """
        Форматирует сообщение об изменении цены
        
        Args:
            change: Словарь с данными об изменении цены
        """
        # Определяем эмодзи и направление
        if change['direction'] == 'up':
            emoji = "🚀"
            direction_text = "РОСТ ЦЕНЫ"
            change_emoji = "📈"
        else:
            emoji = "📉"
            direction_text = "ПАДЕНИЕ ЦЕНЫ"
            change_emoji = "📉"
        
        # Форматируем цену
        price = change['current_price']
        if price >= 1:
            price_str = f"${price:,.2f}"
        else:
            price_str = f"${price:.6f}"
        
        # Форматируем объем
        volume = change['volume_24h']
        if volume >= 1_000_000:
            volume_str = f"{volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            volume_str = f"{volume/1_000:.1f}K"
        else:
            volume_str = f"{volume:.0f}"
        
        # Создаем сообщение
        message = f"""
{emoji} <b>{direction_text}</b>

<b>Пара:</b> {change['symbol']}
<b>Изменение:</b> {change['price_change_percent']:+.2f}%
<b>Цена:</b> {price_str}
<b>Период:</b> {change['monitoring_period_minutes']} минут
<b>Объем 24ч:</b> {volume_str} USDT

{change_emoji} <a href="{change['exchange_url']}">Торговать на Bybit</a>
        """.strip()
        
        return message
    
    def format_summary_message(self, changes: List[Dict]) -> str:
        """
        Форматирует сводное сообщение с несколькими изменениями
        
        Args:
            changes: Список изменений
        """
        if not changes:
            return "Значительных изменений цен не обнаружено."
        
        # Разделяем на рост и падение
        up_changes = [c for c in changes if c['direction'] == 'up']
        down_changes = [c for c in changes if c['direction'] == 'down']
        
        message_parts = []
        
        if len(changes) == 1:
            return self.format_price_change_message(changes[0])
        
        # Заголовок
        message_parts.append(f"📊 <b>ОБНАРУЖЕНО {len(changes)} ИЗМЕНЕНИЙ</b>")
        message_parts.append(f"⏰ Период мониторинга: {changes[0]['monitoring_period_minutes']} минут")
        message_parts.append("")
        
        # Рост цен
        if up_changes:
            message_parts.append("🚀 <b>РОСТ ЦЕНЫ:</b>")
            for change in up_changes[:5]:  # Показываем максимум 5
                price = change['current_price']
                price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
                message_parts.append(f"• {change['symbol']}: <b>{change['price_change_percent']:+.2f}%</b> ({price_str})")
            
            if len(up_changes) > 5:
                message_parts.append(f"... и ещё {len(up_changes) - 5} пар")
            message_parts.append("")
        
        # Падение цен
        if down_changes:
            message_parts.append("📉 <b>ПАДЕНИЕ ЦЕНЫ:</b>")
            for change in down_changes[:5]:  # Показываем максимум 5
                price = change['current_price']
                price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
                message_parts.append(f"• {change['symbol']}: <b>{change['price_change_percent']:+.2f}%</b> ({price_str})")
            
            if len(down_changes) > 5:
                message_parts.append(f"... и ещё {len(down_changes) - 5} пар")
            message_parts.append("")
        
        # Ссылка на биржу
        message_parts.append("📈 <a href='https://www.bybit.com/trade/usdt/BTCUSDT'>Торговать на Bybit</a>")
        
        return "\n".join(message_parts)
    
    async def send_price_alerts(self, changes: List[Dict]) -> bool:
        """
        Отправляет уведомления об изменениях цен
        
        Args:
            changes: Список изменений цен
        """
        if not changes:
            print("Нет изменений для отправки")
            return True
        
        try:
            # Если изменений много, отправляем сводку
            if len(changes) > 3:
                message = self.format_summary_message(changes)
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
                print(f"Отправлена сводка с {len(changes)} изменениями")
            else:
                # Отправляем отдельные сообщения для каждого изменения
                for change in changes:
                    message = self.format_price_change_message(change)
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    # Небольшая задержка между сообщениями
                    await asyncio.sleep(0.5)
                
                print(f"Отправлено {len(changes)} уведомлений")
            
            return True
            
        except TelegramError as e:
            print(f"Ошибка Telegram API: {e}")
            return False
        except Exception as e:
            print(f"Ошибка отправки уведомлений: {e}")
            return False
    
    async def send_status_message(self, message: str) -> bool:
        """
        Отправляет статусное сообщение
        
        Args:
            message: Текст сообщения
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки статуса: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Тестирует подключение к Telegram API
        """
        try:
            bot_info = await self.bot.get_me()
            print(f"Подключение к боту успешно: @{bot_info.username}")
            
            # Отправляем тестовое сообщение
            test_message = f"🤖 <b>Бот запущен!</b>\n\n⏰ Интервал мониторинга: {Config.MONITORING_INTERVAL} мин\n📊 Порог уведомлений: {Config.PRICE_CHANGE_THRESHOLD}%\n🕐 Время запуска: {datetime.now().strftime('%H:%M:%S')}"
            
            await self.send_status_message(test_message)
            return True
            
        except Exception as e:
            print(f"Ошибка тестирования бота: {e}")
            return False

# Функция для тестирования
async def test_telegram_bot():
    """Тестовая функция для проверки работы Telegram бота"""
    try:
        bot = CryptoTelegramBot()
        
        print("Тестируем Telegram бота...")
        
        # Тестируем подключение
        if not await bot.test_connection():
            print("Ошибка подключения к боту")
            return
        
        # Тестовые данные об изменениях
        test_changes = [
            {
                'symbol': 'BTCUSDT',
                'previous_price': 42000.0,
                'current_price': 43500.0,
                'price_change_percent': 3.57,
                'direction': 'up',
                'volume_24h': 1200000,
                'exchange_url': 'https://www.bybit.com/trade/usdt/BTCUSDT',
                'monitoring_period_minutes': 3
            },
            {
                'symbol': 'ETHUSDT',
                'previous_price': 2500.0,
                'current_price': 2425.0,
                'price_change_percent': -3.0,
                'direction': 'down',
                'volume_24h': 800000,
                'exchange_url': 'https://www.bybit.com/trade/usdt/ETHUSDT',
                'monitoring_period_minutes': 3
            }
        ]
        
        # Отправляем тестовые уведомления
        await bot.send_price_alerts(test_changes)
        
        print("Тест завершен успешно!")
        
    except Exception as e:
        print(f"Ошибка тестирования: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram_bot())