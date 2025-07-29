#!/usr/bin/env python3
"""
Скрипт для получения Chat ID
Напишите боту любое сообщение, затем запустите этот скрипт
"""

import requests
import json

# Ваш токен бота
BOT_TOKEN = "8228590806:AAE-P_9YHO9fuow_lZSLfw5hgoHPIwFABfM"

def get_chat_id():
    """Получает Chat ID из последних сообщений"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok'] and data['result']:
                print("🔍 Найденные чаты:")
                print("-" * 50)
                
                seen_chats = set()
                
                for update in data['result']:
                    if 'message' in update:
                        message = update['message']
                        chat = message['chat']
                        chat_id = chat['id']
                        
                        if chat_id not in seen_chats:
                            seen_chats.add(chat_id)
                            
                            chat_type = chat['type']
                            if chat_type == 'private':
                                name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                                username = chat.get('username', 'нет username')
                                print(f"👤 Личный чат: {name}")
                                print(f"   Username: @{username}")
                                print(f"   Chat ID: {chat_id}")
                            elif chat_type == 'group':
                                title = chat.get('title', 'Без названия')
                                print(f"👥 Группа: {title}")
                                print(f"   Chat ID: {chat_id}")
                            elif chat_type == 'supergroup':
                                title = chat.get('title', 'Без названия')
                                print(f"👥 Супергруппа: {title}")
                                print(f"   Chat ID: {chat_id}")
                            elif chat_type == 'channel':
                                title = chat.get('title', 'Без названия')
                                print(f"📢 Канал: {title}")
                                print(f"   Chat ID: {chat_id}")
                            
                            print("-" * 30)
                
                if not seen_chats:
                    print("❌ Сообщения не найдены!")
                    print("💡 Напишите боту любое сообщение и запустите скрипт снова")
                else:
                    print("\n✅ Скопируйте нужный Chat ID и добавьте его в .env файл")
                    print("📝 Замените 'your_chat_id_here' на ваш Chat ID")
                    
            else:
                print("❌ Нет обновлений от бота")
                print("💡 Убедитесь, что вы написали боту сообщение")
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print("💡 Проверьте токен бота")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Получение Chat ID для Telegram бота")
    print("=" * 50)
    get_chat_id()