import os
import html  # <-- ЦЕЙ РЯДОК ДОДАЄМО ДЛЯ БЕЗПЕЧНОГО ТЕКСТУ
from supabase import create_client, Client
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any

# Завантажуємо змінні оточення
load_dotenv()

# Отримуємо ключі
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# Ініціалізуємо клієнт Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# АВТЕНТИФІКАЦІЯ (Реєстрація / Вхід / Вихід)
# ============================================================================

def register_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
    """
    Реєструє нового користувача в Supabase Auth.
    Повертає словник з результатом: {'success': bool, 'user_id': str, 'error': str}
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })
        
        if response.user:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "error": None
            }
        else:
            return {
                "success": False,
                "user_id": None,
                "error": "Не вдалося зареєструвати користувача"
            }
    except Exception as e:
        return {
            "success": False,
            "user_id": None,
            "error": str(e)
        }


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Входить користувачем в систему.
    Повертає словник з результатом: {'success': bool, 'user_id': str, 'error': str}
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "error": None
            }
        else:
            return {
                "success": False,
                "user_id": None,
                "error": "Невірний email або пароль"
            }
    except Exception as e:
        return {
            "success": False,
            "user_id": None,
            "error": str(e)
        }


def logout_user() -> bool:
    """Виходить з системи"""
    try:
        supabase.auth.sign_out()
        return True
    except:
        return False


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Повертає інформацію про поточного користувача, якщо він залогінений.
    """
    try:
        user = supabase.auth.get_user()
        if user and user.user:
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "full_name": user.user.user_metadata.get("full_name", "")
            }
        return None
    except:
        return None


# ============================================================================
# ПРОФІЛЬ (Збереження / Завантаження)
# ============================================================================

def save_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    """
    Зберігає або оновлює профіль користувача.
    """
    try:
        # 🔍 ДІАГНОСТИКА: Друкуємо в консоль, що ми отримуємо
        print(f"💾 save_profile отримав site_config: {'Так' if 'site_config' in profile_data and profile_data['site_config'] else 'Ні (NULL)'}")
        
        # Спочатку пробуємо оновити
        response = supabase.table('profiles').update(profile_data).eq('id', user_id).execute()
        
        # Якщо не вийшло (профіль не існує), створюємо новий
        if not response.data:
            profile_data['id'] = user_id
            profile_data['slug'] = profile_data.get('name', '').lower().replace(' ', '-')
            response = supabase.table('profiles').insert(profile_data).execute()
        
        return True
    except Exception as e:
        print(f"Помилка збереження профілю: {e}")
        return False


def load_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Завантажує профіль користувача з бази даних.
    """
    try:
        response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Помилка завантаження профілю: {e}")
        return None


# ============================================================================
# ПОСИЛАННЯ (Збереження / Завантаження)
# ============================================================================

def save_links(user_id: str, links: List[Dict[str, Any]]) -> bool:
    """
    Зберігає всі посилання користувача.
    Спочатку видаляє старі, потім додає нові.
    """
    try:
        # Видаляємо старі посилання
        supabase.table('links').delete().eq('profile_id', user_id).execute()
        
        # Додаємо нові
        if links:
            links_to_insert = []
            for idx, link in enumerate(links):
                links_to_insert.append({
                    'profile_id': user_id,
                    'title': link.get('title', ''),
                    'url': link.get('url', ''),
                    'is_paid': link.get('is_paid', False),
                    'price': link.get('price', 0),
                    'position': idx
                })
            supabase.table('links').insert(links_to_insert).execute()
        
        return True
    except Exception as e:
        print(f"Помилка збереження посилань: {e}")
        return False


def load_links(user_id: str) -> List[Dict[str, Any]]:
    """
    Завантажує всі посилання користувача.
    """
    try:
        response = supabase.table('links').select('*').eq('profile_id', user_id).order('position').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Помилка завантаження посилань: {e}")
        return []


# ============================================================================
# ТОВАРИ (Збереження / Завантаження)
# ============================================================================

def save_products(user_id: str, products: List[Dict[str, Any]]) -> bool:
    """
    Зберігає всі товари користувача.
    """
    try:
        # Видаляємо старі товари
        supabase.table('products').delete().eq('profile_id', user_id).execute()
        
        # Додаємо нові
        if products:
            products_to_insert = []
            for idx, prod in enumerate(products):
                products_to_insert.append({
                    'profile_id': user_id,
                    'title': prod.get('title', ''),
                    'description': prod.get('description', ''),
                    'price': prod.get('price', 0),
                    'image_url': prod.get('image', ''),
                    'is_available': True,
                    'position': idx
                })
            supabase.table('products').insert(products_to_insert).execute()
        
        return True
    except Exception as e:
        print(f"Помилка збереження товарів: {e}")
        return False


def load_products(user_id: str) -> List[Dict[str, Any]]:
    """
    Завантажує всі товари користувача.
    """
    try:
        response = supabase.table('products').select('*').eq('profile_id', user_id).order('position').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Помилка завантаження товарів: {e}")
        return []


# ============================================================================
# ЗАМОВЛЕННЯ (Створення / Сповіщення)
# ============================================================================

def create_order(profile_id: str, order_data: Dict[str, Any]) -> Optional[str]:
    """
    Створює нове замовлення.
    order_data має містити: customer_name, customer_phone, delivery_type, delivery_city, delivery_address, comment, items_json, total_amount
    Повертає ID замовлення або None.
    """
    try:
        order_data['profile_id'] = profile_id
        response = supabase.table('orders').insert(order_data).execute()
        
        if response.data and len(response.data) > 0:
            order_id = response.data[0]['id']
            
            # Відправляємо сповіщення власнику
            send_order_notification(profile_id, order_id, order_data)
            
            return order_id
        return None
    except Exception as e:
        print(f"Помилка створення замовлення: {e}")
        return None


def send_order_notification(profile_id: str, order_id: str, order_data: Dict[str, Any]):
    """
    Відправляє сповіщення про нове замовлення власнику в Telegram (через HTML).
    """
    try:
        print(f"🔍 Починаємо відправку сповіщення для profile_id: {profile_id}")
        
        profile = load_profile(profile_id)
        if not profile:
            print("❌ Помилка: Профіль не знайдено в базі даних!")
            return
            
        chat_id = profile.get('telegram_chat_id')
        print(f"📱 Знайдений chat_id у базі: '{chat_id}'")
        
        if not chat_id:
            print("❌ Помилка: У власника не вказано telegram_chat_id в профілі!")
            return
        
        # Безпечно екрануємо дані користувача для HTML
        customer_name = html.escape(str(order_data.get('customer_name', '')))
        customer_phone = html.escape(str(order_data.get('customer_phone', '')))
        delivery_type = html.escape(str(order_data.get('delivery_type', '')))
        delivery_city = html.escape(str(order_data.get('delivery_city', '')))
        delivery_address = html.escape(str(order_data.get('delivery_address', '')))
        comment = html.escape(str(order_data.get('comment', 'Немає')))
        
        # Формуємо список товарів з екрануванням назв
        items_text = "\n".join([
            f"• {html.escape(str(item.get('title', '')))} — {item.get('price', 0)}₴ × {item.get('quantity', 1)}"
            for item in order_data.get('items_json', [])
        ])
        
        # Використовуємо HTML теги (<b> замість *)
        message = f"""🔔 <b>Нове замовлення #{str(order_id)[:8]}</b>

👤 Клієнт: {customer_name}
📞 Телефон: {customer_phone}

📦 Доставка: {delivery_type}
🏙 Місто: {delivery_city}
🏢 Адреса: {delivery_address}

🛒 <b>Товари:</b>
{items_text}

💰 <b>Сума: {order_data.get('total_amount', 0)}₴</b>
💬 Коментар: {comment}"""
        
        print("📤 Відправляємо запит до Telegram API (режим HTML)...")
        
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": str(chat_id),
            "text": message,
            "parse_mode": "HTML"  # <--- ЗМІНЕНО З Markdown НА HTML
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Сповіщення успішно відправлено в Telegram!")
        else:
            print(f"❌ Помилка Telegram API: {response.status_code}")
            print(f"📄 Деталі помилки: {response.text}")
            
    except Exception as e:
        print(f"❌ Критична помилка у send_order_notification: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# АНАЛІТИКА
# ============================================================================

def track_event(profile_id: str, event_type: str, target_id: Optional[str] = None):
    """
    Відстежує подію (перегляд, клік тощо).
    """
    try:
        supabase.table('analytics').insert({
            'profile_id': profile_id,
            'event_type': event_type,
            'target_id': target_id
        }).execute()
    except Exception as e:
        print(f"Помилка відстеження події: {e}")


def get_analytics(profile_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Отримує аналітику за останні N днів.
    """
    try:
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        response = supabase.table('analytics').select('*').eq('profile_id', profile_id).gte('created_at', start_date).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Помилка отримання аналітики: {e}")
        return []
    
    # ============================================================================
# ВИДАЛЕННЯ ДАНИХ (Для повного очищення акаунту)
# ============================================================================

def delete_profile(user_id: str) -> bool:
    """Видаляє профіль користувача"""
    try:
        supabase.table('profiles').delete().eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Помилка видалення профілю: {e}")
        return False

def delete_links(user_id: str) -> bool:
    """Видаляє всі посилання користувача"""
    try:
        supabase.table('links').delete().eq('profile_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Помилка видалення посилань: {e}")
        return False

def delete_products(user_id: str) -> bool:
    """Видаляє всі товари користувача"""
    try:
        supabase.table('products').delete().eq('profile_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Помилка видалення товарів: {e}")
        return False