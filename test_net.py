   import requests
   try:
       response = requests.get("https://supabase.com", timeout=5)
       print("✅ Інтернет з Python працює! Статус:", response.status_code)
   except Exception as e:
       print("❌ Python НЕ бачить інтернет. Помилка:", e)