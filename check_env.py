import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
   
print("=" * 50)
print(f"ЗНАЙДЕНИЙ URL: '{url}'")
print(f"Довжина рядка: {len(url) if url else 0}")
   
if url:
       if url.endswith(" "):
           print("⚠️ УВАГА: В кінці URL є ПРИХОВАНИЙ ПРОБІЛ! Це ламає підключення.")
       else:
           print("✅ URL виглядає чистим (без пробілів в кінці).")
else:
       print("❌ URL не знайдено! Перевірте файл .env")
print("=" * 50)