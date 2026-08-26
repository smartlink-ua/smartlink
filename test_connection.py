import os
from supabase import create_client, Client
import requests
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

print("🔄 Перевірка з'єднання з Supabase...")
try:
    # Ініціалізуємо клієнт Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase підключено успішно!")
    
    # Спробуємо зробити простий запит
    response = supabase.table('profiles').select('id').limit(1).execute()
    print("✅ База даних відповідає!")
except Exception as e:
    print(f"❌ Помилка Supabase: {e}")
    print("💡 Переконайтеся, що ви запустили SQL-скрипт у Supabase SQL Editor!")

print("\n🔄 Перевірка Telegram-бота...")
try:
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": "🚀 *MSSG Clone MVP*\n\nЗв'язок встановлено! Бот працює коректно і готовий відправляти сповіщення про замовлення.",
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Повідомлення в Telegram відправлено успішно! Перевірте свій чат.")
    else:
        print(f"❌ Помилка Telegram: {response.text}")
        print("💡 Переконайтеся, що ви натиснули 'Start' у цьому боті в Telegram!")
except Exception as e:
    print(f"❌ Помилка з'єднання: {e}")

print("\n🎉 Тест завершено!")